
import time
import redis

from . import settings
from .signals import rate_limited

# Connection pool
POOL = redis.ConnectionPool(**settings.REDIS)

def check_realm(request, realm):

    conf = settings.REALMS.get(realm, {})

    source = request.META['REMOTE_ADDR']

    # Check against Realm whitelist
    if source in conf.get('whitelist', settings.DEFAULT_WHITELIST):
            return None

        key = 'rated:%s:%s' % (realm, source,)
        now = time.time()

        client = redis.Redis(connection_pool=POOL)
        # Do commands at once for speed
        # We don't need these to operate in a transaction, as none of the values
        # we send are dependant on values in the DB
        pipe = client.pipeline(transaction=False)
        # Add our timestamp to the range
        pipe.zadd(key, now, now)
        # Update to not expire for another TIMEOUT
        pipe.expireat(key, int(now + conf.get('timeout', settings.DEFAULT_TIMEOUT)))
        # Remove old values
        pipe.zremrangebyscore(key, '-inf', now - settings.DEFAULT_TIMEOUT)
        # Test count
        pipe.zcard(key)
        size = pipe.execute()[-1]
        return size > conf.get('limit', settings.DEFAULT_LIMIT)
