import redis
import json

class RedisProgressTracker(object):
    def __init__(self, host='localhost', port=6379, db=15, timeout=3600):
        super(RedisProgressTracker, self).__init__()
        self.redis = redis.StrictRedis(host=host, port=port, db=db)
        self.timeout = int(timeout)

    def track(self, entryid):
        value = json.dumps((-1, None))
        self.redis.setex(entryid, self.timeout, value)

    def remove(self, entryid):
        self.redis.delete(entryid)

    def set_progress(self, entryid, value, message):
        value = json.dumps((value, message))
        self.redis.set(entryid, value)

    def get_progress(self, entryid):
        value = self.redis.get(entryid)
        if value is not None:
            value = tuple(json.loads(value.decode('ascii')))
        return value