__author__ = 'tarzan'

class SignIn(object):
    def __init__(self, request, access_code):
        """
        :type request: pyramid.request.Request
        :type access_code: pyramid_vgid_oauth2.models.AccessCode
        """
        self.request = request
        self.access_code = access_code

class SignOut(object):
    def __init__(self, request):
        """
        :type request: pyramid.request.Request
        """
        self.request = request
