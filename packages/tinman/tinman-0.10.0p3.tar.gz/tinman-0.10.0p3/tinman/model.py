"""
Base tinman data models. The Model class is the base model that all other base
model classes extend. StorageModel defines the interfaces for models with built
in storage functionality.

Specific model storage base classes exist in the tornado.model package.

Example use::

    from tornado import gen
    from tornado import web
    from tinman.handlers import redis_handlers
    from tinman.model.redis import AsyncRedisModel


    class ExampleModel(AsyncRedisModel):
        name = None
        age = None
        location = None


    class Test(redis_handlers.AsynchronousRedisRequestHandler):

        @web.asynchronous
        @gen.engine
        def get(self, *args, **kwargs):
            model = ExampleModel(self.get_argument('id'),
                                 redis_client=self.redis)
            yield model.fetch()
            self.finish(model.as_dict())

        @web.asynchronous
        @gen.engine
        def post(self, *args, **kwargs):
            model = ExampleModel(self.get_argument('id', None),
                                 redis_client=self.redis)

            # Assign the posted values, requiring at least a name
            model.name = self.get_argument('name')
            model.age = self.get_argument('age', None)
            model.location = self.get_argument('location', None)

            # Save the model
            result = yield model.save()
            if result:
                self.set_status(201)
                self.finish(model.as_dict())
            else:
                raise web.HTTPError(500, 'Could not save model')

"""
from tornado import gen
import hashlib
import logging
import time
import uuid

from tinman import mapping

LOGGER = logging.getLogger(__name__)


class Model(mapping.Mapping):
    """A data object that provides attribute level assignment and retrieval of
    values, serialization and deserialization, the ability to load values from
    a dict and dump them to a dict, and Mapping and iterator behaviors.

    Base attributes are provided for keeping track of when the model was created
    and when it was last updated.

    If model attributes are passed into the constructor, they will be assigned
    to the model upon creation.

    :param str item_id: An id for the model, defaulting to a random UUID
    :param dict kwargs: Additional kwargs passed in

    """
    # A mapping of attribute name to model classes to load child models
    _child_attributes = dict()

    id = None
    created_at = None
    last_updated_at = None

    def __init__(self, item_id=None, **kwargs):
        """Create a new instance of the model, passing in a id value."""
        self.id = item_id or str(uuid.uuid4())
        self.created_at = int(time.time())
        self.last_updated_at = None

        # If values are in the kwargs that match the model keys, assign them
        for k in [k for k in kwargs.keys() if k in self.keys()]:
            setattr(self, k, kwargs[k])

    def as_dict(self):
        """Return this object as a dict value.

        :rtype: dict

        """
        items = dict(self.items())
        for key in items:
            if key in self._child_attributes:
                items[key] = items[key].as_dict()
        return items

    def from_dict(self, value):
        """Set the values of the model based upon the content of the passed in
        dictionary.

        :param dict value: The dictionary of values to assign to this model

        """
        for key in self.keys():
            if key in self._child_attributes.keys():
                setattr(self, key, self._child_attributes[key]())
                obj = getattr(self, key)
                obj.from_dict(value.get(key, dict()))
            else:
                setattr(self, key, value.get(key, None))

    def sha1(self):
        """Return a sha1 hash of the model items.

        :rtype: str

        """
        sha1 = hashlib.sha1(''.join(['%s:%s' % (k,v) for k,v in self.items()]))
        return str(sha1.hexdigest())


class StorageModel(Model):
    """A base model that defines the behavior for models with storage backends.

    :param str item_id: An id for the model, defaulting to a random UUID
    :param dict kwargs: Additional kwargs passed in

    """
    _new = True

    def __init__(self, item_id=None, **kwargs):
        super(StorageModel, self).__init__(item_id, **kwargs)
        if self.id:
            # It's no longer a new model, since it's a load
            self._new = False

            # Fetch the model values from storage
            self.fetch()

            # Toggle the changed back to false since it's an initial load
            self._dirty = False

    def delete(self):
        """Delete the data for the model from storage and assign the values.

        :raises: NotImplementedError

        """
        raise NotImplementedError("Must extend this method")

    def fetch(self):
        """Fetch the data for the model from storage and assign the values.

        :raises: NotImplementedError

        """
        raise NotImplementedError("Must extend this method")

    def save(self):
        """Store the model.

        :raises: NotImplementedError

        """
        raise NotImplementedError("Must extend this method")

    @property
    def is_new(self):
        """Return a bool indicating if it's a new item or not

        :rtype: bool

        """
        return self._new


class AsyncRedisModel(StorageModel):
    """A model base class that uses Redis for the storage backend. Uses the
    asynchronous tornadoredis client. If you assign a value to either a ttl
    (dynamic) or _ttl (static) attribute, that value will be used to set the
    expiration of the data in redis.

    Data is serialized with msgpack to cut down on the byte size, but due to
    the binary data, it is then base64 encoded. This is a win on large objects
    but a slight amount of overhead on smaller ones.

    :param str item_id: The id for the data item
    :param tornadoredis.Client: The already created tornadoredis client

    """
    _redis_client = None
    _saved = False
    _ttl = None

    def __init__(self, item_id=None, *args, **kwargs):
        if 'msgpack' not in globals():
            import msgpack
        self._serializer = msgpack
        if 'redis_client' not in kwargs:
            raise ValueError('redis_client must be passed in')
        self._redis_client = kwargs['redis_client']

        # The parent will attempt to fetch the value if item_id is set
        super(AsyncRedisModel, self).__init__(item_id, **kwargs)

    @property
    def _key(self):
        """Return a storage key for Redis that consists of the class name of
        the model and its id joined by :.

        :rtype: str

        """
        return '%s:%s' % (self.__class__.__name__, self.id)

    @gen.coroutine
    def delete(self):
        """Delete the item from storage

        :rtype: bool

        """
        result = gen.Task(self._redis_client.delete, self._key)
        raise gen.Return(bool(result))

    @gen.coroutine
    def fetch(self):
        """Fetch the data for the model from Redis and assign the values.

        :rtype: bool

        """
        raw = yield gen.Task(self._redis_client.get, self._key)
        if raw:
            self.loads(raw)
            raise gen.Return(True)
        raise gen.Return(False)

    @gen.coroutine
    def save(self):
        """Store the model in Redis.

        :rtype: bool

        """
        pipeline = self._redis_client.pipeline()
        pipeline.set(self._key, self.dumps())
        if hasattr(self, 'ttl'):
            ttl = getattr(self, 'ttl', self._ttl)
            if ttl:
                pipeline.expire(self._key, ttl)
        result = yield gen.Task(pipeline.execute)
        self._dirty, self._saved = not all(result), all(result)
        raise gen.Return(all(result))
