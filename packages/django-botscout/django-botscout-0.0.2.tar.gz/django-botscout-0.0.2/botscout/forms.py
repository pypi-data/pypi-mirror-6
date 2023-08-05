import hashlib
import logging
from urllib import urlencode
import urllib2

from django.core import cache
from django import forms
from django.utils.translation import ugettext_lazy as _

from .settings import (BOTSCOUT_API_KEY, BOTSCOUT_API_URL,
                       BOTSCOUT_CACHE_TIMEOUT, BOTSCOUT_NETWORK_TIMEOUT)

logger = logging.getLogger(__name__)


class BotScoutForm(object):
    """
    BotScoutForm is a form mixin which should work with both regular and model
    forms to prevent spam bots. It checks all available data against the
    botscout.com database for any bots known to them.

    This mixin should precede forms.Form/ModelForm.
    """
    error_messages = {'botscout': _('This request was matched in the BotScout database')}

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        error_msg = getattr(self, 'BOTSCOUT_ERROR_MESSAGE', None)
        if error_msg is not None:
            self.error_messages['botscout'] = error_msg
        super(BotScoutForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super(BotScoutForm, self).clean()
        try:
            bot_cache = cache.get_cache('botscout')
        except cache.InvalidCacheBackendError:
            bot_cache = cache.get_cache('default')
        using_ip = self.request is not None
        name_field = getattr(self, 'BOTSCOUT_NAME_FIELD', 'name')
        email_field = getattr(self, 'BOTSCOUT_EMAIL_FIELD', 'email')
        test_data = {'name': data.get(name_field, None),
                     'mail': data.get(email_field, None)}
        if using_ip:
            test_data['ip'] = self.request.META.get('REMOTE_ADDR', None)
        test_data = dict((x, y.strip()) for x, y in test_data.iteritems() if y is not None)
        cached_data = bot_cache.get_many(['botscout:%s:%s' % (x, hashlib.sha256(y).hexdigest())
                                          for x, y in test_data.iteritems()])
        if any(cached_data.values()):
            raise forms.ValidationError(self.error_messages['botscout'])
        untested = dict((x, y) for x, y in test_data.iteritems()
                        if 'botscout:%s:%s' % (x, hashlib.sha256(y).hexdigest()) not in cached_data)
        if untested:
            test_url = '%s?multi&%s' % (BOTSCOUT_API_URL, urlencode(untested))
            if BOTSCOUT_API_KEY is not None:
                test_url = '%s&key=%s' % (test_url, BOTSCOUT_API_KEY)
            try:
                scout_handle = urllib2.urlopen(test_url, timeout=BOTSCOUT_NETWORK_TIMEOUT)
                response = scout_handle.read(1024)
                if response.startswith('!'):
                    logger.error(response)
                else:
                    # Format: Y|MULTI|IP|3|MAIL|1|NAME|2
                    (unused, unused, unused, ip_hits, unused, mail_hits,
                     unused, name_hits) = response.split('|')
                    hit_data = {}
                    if 'ip' in untested:
                        hit_data['botscout:ip:%s' % hashlib.sha256(untested['ip']).hexdigest()] = int(ip_hits)
                    if 'mail' in untested:
                        hit_data['botscout:mail:%s' % hashlib.sha256(untested['mail']).hexdigest()] = int(mail_hits)
                    if 'name' in untested:
                        hit_data['botscout:name:%s' % hashlib.sha256(untested['name']).hexdigest()] = int(name_hits)
                    bot_cache.set_many(hit_data, BOTSCOUT_CACHE_TIMEOUT)
                    if any(hit_data.values()):
                        raise forms.ValidationError(self.error_messages['botscout'])
            except urllib2.URLError:
                """
                In case of an error on BotScout's side, we don't want to block this
                request.
                """
                pass
        return data
