from __future__ import absolute_import
from datetime import timedelta
from dimagi.utils.couch.delete import delete
from dimagi.utils.couch.safe_index import safe_index
from dimagi.utils.couch.cache.cache_core import get_redis_client
from couchdbkit.ext.django.schema import DateTimeProperty, DocumentSchema
from couchdbkit.exceptions import ResourceConflict
import json

LOCK_EXPIRATION = timedelta(hours = 1)

class LockableMixIn(DocumentSchema):
    lock_date = DateTimeProperty()

    def acquire_lock(self, now):
        """
        Returns True if the lock was acquired by the calling thread,
        False if another thread acquired it first
        """
        if (self.lock_date is None) or (now > (self.lock_date + LOCK_EXPIRATION)):
            try:
                self.lock_date = now
                self.save()
                return True
            except ResourceConflict:
                return False
        else:
            return False

    def release_lock(self):
        assert self.lock_date is not None
        self.lock_date = None
        self.save()

class RedisLockableMixIn(object):
    @classmethod
    def _redis_obj_lock_key(cls, obj_id):
        """
        This method should return a string representing the name of the key
        that will be used to lock an object of this class.
        """
        return "redis-object-lock-%s-%s" % (cls.__name__, obj_id)

    @classmethod
    def _redis_class_lock_key(cls):
        """
        This method should return a string representing the name of the key
        that will be used to lock access to this class.
        """
        return "redis-class-lock-%s" % cls.__name__

    @classmethod
    def get_obj_id(cls, obj):
        """
        This method should return the unique identifier of the given object.
        """
        raise NotImplementedError("Please implement this method.")

    @classmethod
    def get_obj(cls, *args, **kwargs):
        """
        This method should return an instance of this class matching the passed
        arguments, or None if not found.
        """
        raise NotImplementedError("Please implement this method.")

    @classmethod
    def get_obj_by_id(cls, _id):
        """
        This method should return an instance of this class matching the passed
        id, or None if not found.
        """
        raise NotImplementedError("Please implement this method.")

    @classmethod
    def create_obj(cls, *args, **kwargs):
        """
        This method should create and return an instance of this class using the
        passed arguments.
        """
        raise NotImplementedError("Please implement this method.")

    @classmethod
    def get_latest_obj(cls, obj):
        obj_id = cls.get_obj_id(obj)
        return cls.get_obj_by_id(obj_id)

    @classmethod
    def get_obj_lock(cls, obj, timeout_seconds=30):
        obj_id = cls.get_obj_id(obj)
        return cls.get_redis_lock(cls._redis_obj_lock_key(obj_id), timeout_seconds)

    @classmethod
    def get_obj_lock_by_id(cls, obj_id, timeout_seconds=30):
        return cls.get_redis_lock(cls._redis_obj_lock_key(obj_id), timeout_seconds)

    @classmethod
    def get_redis_lock(cls, key, timeout_seconds):
        client = get_redis_client()
        lock = client.lock(key, timeout=timeout_seconds)
        return lock

    @classmethod
    def get_class_lock(cls, timeout_seconds=30):
        return cls.get_redis_lock(cls._redis_class_lock_key(), timeout_seconds)

    @classmethod
    def get_locked_obj(cls, *args, **kwargs):
        """
        Returns a two-tuple containing the object and its lock, which has 
        already been acquired. Once you're finished processing the object, 
        you should call .release() on the lock.

        Pass in a kwarg of _id to get the object with get_obj_by_id. Otherwise,
        the object will be retrieved by calling get_obj and passing it all of
        the args.

        Pass in a kwarg of create=True to create the object if it doesn't exist.
        The object will be created calling create_obj and passing it all of the
        args. If create is False or is not set, and if the object doesn't exist,
        (None, None) is returned.
        """
        create = kwargs.pop("create", False)
        _id = kwargs.get("_id", None)

        if _id:
            lock = cls.get_obj_lock_by_id(_id)
            lock.acquire(blocking=True)
        else:
            lock = cls.get_class_lock(timeout_seconds=60)
            lock.acquire(blocking=True)
        try:
            if _id:
                obj = cls.get_obj_by_id(_id)
            else:
                obj = cls.get_obj(*args, **kwargs)
            if not obj:
                if create:
                    obj = cls.create_obj(*args, **kwargs)
                else:
                    lock.release()
                    return (None, None)
        except:
            lock.release()
            raise
        else:
            if _id:
                return (obj, lock)
            else:
                obj_lock = cls.get_obj_lock(obj)
                obj_lock.acquire()
                # Refresh the object in case another thread has updated it
                obj = cls.get_latest_obj(obj)
                lock.release()
                return (obj, obj_lock)

class CouchDocLockableMixIn(RedisLockableMixIn):
    """
    A mixin to prevent document update conflicts and race conditions.
    An example implementation would be:
    
    >>> class Patient(Document, CouchDocLockableMixIn):
            patient_id = StringProperty()
            last_visit = DateProperty()

            @classmethod
            def get_obj(cls, patient_id, *args, **kwargs):
                return Patient.view("patient/by_patient_id",
                                    key=patient_id,
                                    include_docs=True).one()

            @classmethod
            def create_obj(cls, patient_id, *args, **kwargs):
                obj = Patient(patient_id=patient_id)
                obj.save()
                return obj

    >>> # Prevent race condition from creating two patients
    >>> patient, lock = Patient.get_locked_obj("pid-1234", create=True)
    >>> patient.last_visit = date(2014, 1, 24)
    >>> patient.save()
    >>> lock.release()

    >>> # Prevent doc update conflict
    >>> patient, lock = Patient.get_locked_obj("pid-1234")
    >>> if not patient:
    >>>     raise RunTimeError("Patient not found")
    >>>
    >>> patient.last_visit = date(2014, 1, 25)
    >>> patient.save()
    >>> lock.release()

    >>> # Lookup using couch doc _id
    >>> patient, lock = Patient.get_locked_obj(_id="fa98e2...")
    >>> if not patient:
    >>>     raise RunTimeError("Patient not found")
    >>>
    >>> patient.last_visit = date(2014, 1, 26)
    >>> patient.save()
    >>> lock.release()
    """

    @classmethod
    def get_obj_id(cls, obj):
        return obj._id

    @classmethod
    def get_obj(cls, *args, **kwargs):
        """
        This method should lookup to the appropriate couch view using the
        passed arguments and return the object if found, otherwise None.
        """
        raise NotImplementedError("Please implement this method.")

    @classmethod
    def get_obj_by_id(cls, _id):
        return cls.get(_id)

    @classmethod
    def create_obj(cls, *args, **kwargs):
        """
        This method should create and return an instance of this class using the
        passed arguments.
        """
        raise NotImplementedError("Please implement this method.")

class LooselyEqualDocumentSchema(DocumentSchema):
    """
    A DocumentSchema that will pass equality and hash checks if its
    contents are the same as another document.
    """

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._doc == other._doc

    def __hash__(self):
        return hash(json.dumps(self._doc, sort_keys=True))

class IncompatibleDocument(Exception):
    pass

def get_cached_property(couch_cls, obj_id, prop_name, expiry=12*60*60):
    """
        A function that returns a property of any couch object. If it doesn't find the property in memcached, it does
        the couch query to pull the object and grabs the property. Then it caches the retrieved property.
        Note: The property needs to be pickleable
    """
    from django.core.cache import cache
    cache_str = "{0}:{1}:{2}".format(couch_cls.__name__, obj_id, prop_name)
    ret = cache.get(cache_str)
    if not ret:
        data = couch_cls.get_db().get(obj_id)
        if couch_cls._doc_type in [data.get("doc_type"), data.get("base_doc")]:
            obj = couch_cls.wrap(data)
            ret = getattr(obj, prop_name)
            cache.set(cache_str, ret, expiry)
        else:
            raise IncompatibleDocument("The retrieved document doesn't match the Document Class provided")
    return ret
