import logging
import redis
import dill as pickle

from will import settings


class StorageMixin(object):
    def bootstrap_storage(self):
        # redis://localhost:6379/7
        parts = settings.WILL_REDIS_URL.replace("redis://", "")
        host = parts.split(":")[0]
        port = parts.split(":")[1].split("/")[0]
        try:
            db = parts.split(":")[1].split("/")[1]
        except:
            db = None
        self.storage = redis.StrictRedis(host=host, port=port, db=db)

    def save(self, key, value):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()
        return self.storage.set(key, pickle.dumps(value))

    def clear(self, key):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()
        return self.storage.delete(key)

    def clear_all_keys(self):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()
        return self.storage.flushdb()

    def load(self, key, default=None):
        if not hasattr(self, "storage"):
            self.bootstrap_storage()

        try:
            val = self.storage.get(key)
            if val is not None:
                return pickle.loads(val)
                
        except:
            logging.warn("Unable to load %s" % key)

        return default
