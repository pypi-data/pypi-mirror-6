__author__ = 'tarzan'

import requests
from requests.auth import HTTPDigestAuth
import logging
import pyramid_vgid_oauth2 as pvo

class Identity(object):
    user = None
    is_email_verified = None
    is_phone_verified = None

class AccessCode(object):
    _verified = None

    value = None
    access_token = None
    user = None

    def __init__(self, value):
        self.value = value

    def verify(self):
        if self._verified is not None:
            return self._verified
        self._verified = False

        try:
            auth = HTTPDigestAuth(pvo.CLIENT_ID, pvo.CLIENT_SECRET)
            api_url = 'https://id.vatgia.com/oauth2/accessCode/%s?with=acc' % self.value
            r = requests.get(api_url, auth=auth)

            if r.status_code == 404:
                logging.warn("Response %d %s\n%s" % (r.status_code, r.reason, r.content))
                return False

            if r.status_code != 200:
                logging.warn("Response %d %s" % (r.status_code, r.reason))
                return False

            self.__raw_data__ = data = r.json()
            ac = data['objects'][0]
            acc = ac['acc']
            self.access_token = ac.get('access_token', None)
            acc['name'] = acc['first_name'] + ' ' + acc['last_name']
            self.value = ac['value']

            self.user = pvo.PUT_USER_CALLBACK(acc)

            self._verified = True
        except Exception, e:
            raise

        return self._verified

    def __str__(self):
        return self.value