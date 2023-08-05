from django.conf import settings


BOTSCOUT_API_KEY = getattr(settings, 'BOTSCOUT_API_KEY', None)
BOTSCOUT_API_URL = getattr(settings, 'BOTSCOUT_API_URL', 'http://botscout.com/test/')
BOTSCOUT_CACHE_TIMEOUT = getattr(settings, 'BOTSCOUT_CACHE_TIMEOUT', (60 * 30))
BOTSCOUT_NETWORK_TIMEOUT = getattr(settings, 'BOTSCOUT_NETWORK_TIMEOUT', 5)
