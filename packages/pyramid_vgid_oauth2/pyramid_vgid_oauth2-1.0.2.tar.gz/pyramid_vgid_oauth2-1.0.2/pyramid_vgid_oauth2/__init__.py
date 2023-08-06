__author__ = 'tarzan'

from pyramid_vgid_oauth2 import views
import importlib

VGID_OAUTH_URL = None
VGID_SIGNOUT_URL = None
CLIENT_ID = None
CLIENT_SECRET = None
BASE_URL = None

PUT_USER_CALLBACK = None

def set_put_user_callback(fn):
    global PUT_USER_CALLBACK
    PUT_USER_CALLBACK = fn

def signin_url(request, _cont=None, _query={}, **kwargs):
    if _cont:
        _query['_cont'] = _cont
    return request.route_url('pyramid_vgid_oauth2',
                             traverse='signin',
                             _query=_query,
                             **kwargs)

def signout_url(request, _cont=None, _query={}, **kwargs):
    if _cont:
        _query['_cont'] = _cont
    return request.route_url('pyramid_vgid_oauth2',
                             traverse='signout',
                             _query=_query,
                             **kwargs)

def includeme(config):
    """
    :type config: pyramid.config.Configurator
    """
    global VGID_OAUTH_URL
    global VGID_SIGNOUT_URL
    global CLIENT_ID
    global CLIENT_SECRET
    global BASE_URL

    _prefix = 'pyramid_vgid_oauth2.'
    settings = config.registry.settings
    conf = {k[len(_prefix):]:settings[k] for k in settings if k.startswith(_prefix)}

    def get_config(key):
        assert key in conf, "You have to specify " + _prefix + key
        return conf[key]

    VGID_OAUTH_URL = conf.get('vgid_url',
                              'https://id.vatgia.com/dang-nhap/oauth')

    VGID_SIGNOUT_URL = conf.get('vgid_signout_url',
                              'https://id.vatgia.com/dang-xuat/')
    CLIENT_ID = get_config('client_id')
    CLIENT_SECRET = get_config('client_secret')

    put_user_callback_path = get_config('put_user_callback')
    module_name, attr_name = put_user_callback_path.rsplit('.', 1)
    module = importlib.import_module(module_name, package=None)
    put_user_callback_fn = getattr(module, attr_name)
    set_put_user_callback(put_user_callback_fn)

    BASE_URL = get_config('base_url').lstrip('/') + '/'
    config.add_route('pyramid_vgid_oauth2', BASE_URL + '*traverse')
    config.scan(views)

    config.add_request_method(views.get_vgid_access_token,
                              "vgid_access_token",
                              property=True)