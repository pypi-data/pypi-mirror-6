from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.url import urlencode
from pyramid.security import remember, forget
import events
from pyramid.events import subscriber
from pyramid_vgid_oauth2.models import AccessCode
import pyramid_vgid_oauth2 as pvo


@view_config(route_name='pyramid_vgid_oauth2', name='signin', renderer='json')
def signin(request):
    _cont = request.params.get('_cont', request.referer)

    _cont = request.route_url('pyramid_vgid_oauth2', traverse='callback', _query={'_cont': _cont,})
    vgid_url = pvo.VGID_OAUTH_URL + '?' + urlencode({
        'client_id': pvo.CLIENT_ID,
        '_cont': _cont,
    })
    return HTTPFound(vgid_url)

@view_config(route_name='pyramid_vgid_oauth2', name='callback')
def callback(request):
    if 'access_code' not in request.params:
        raise HTTPBadRequest('access_code argument is missing')
    access_code = AccessCode(request.params['access_code'])
    if not access_code.verify():
        return HTTPBadRequest('Can not request AccessToken from AccessCode#%s' % access_code)

    user = access_code.user
    request.registry.notify(events.SignIn(request, access_code))
    headers = remember(request, user.id)
    _cont = request.params.get('_cont', '/')
    return HTTPFound(_cont, headers=headers)

@view_config(route_name='pyramid_vgid_oauth2', name='signout', renderer='json')
def signout(request):
    _cont = request.params.get('_cont', request.referer)
    if not _cont:
        _cont = '/'
    request.registry.notify(events.SignOut(request))
    headers = forget(request)
    redirect_url = pvo.VGID_SIGNOUT_URL + '?' + urlencode({
        'client_id': pvo.CLIENT_ID,
        '_cont': _cont,
    })
    return HTTPFound(redirect_url, headers=headers)


@subscriber(events.SignIn)
def on_user_sign_in(event):
    """
    :type event: events.SignIn
    """
    print event.access_code.access_token
    event.request.session['vgid_access_token'] = event.access_code.access_token

@subscriber(events.SignOut)
def on_user_sign_out(event):
    """
    :type event: events.SignOut
    """
    try:
        del(event.request.session['vgid_access_token'])
    except KeyError:
        pass

def get_vgid_access_token(request):
    try:
        return request.session['vgid_access_token']
    except KeyError:
        return None