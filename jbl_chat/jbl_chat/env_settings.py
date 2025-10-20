import os

"""
Custom settings that can be specified at run time, especially via docker-compose or another
docker runtime.
"""

# hostname and port for redis (usually internal)
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")

# websockets host and port, usually an external url as tihs will be called from the site javascript
WEBSOCKETS_HOST = os.environ.get("WEBSOCKETS_HOST", None)
WEBSOCKETS_PORT = os.environ.get("WEBSOCKETS_PORT", "8888")

# site hostname is added to ALLOWED_HOSTS
SITE_HOSTNAME = os.environ.get("SITE_HOSTNAME")

# if SITE_HOSTNAME is set, we assume this is hosted and thus we should store the database
# in a different folder than our code. (in real life this might be via DEBUG flag)
IS_HOSTED = SITE_HOSTNAME is not None
