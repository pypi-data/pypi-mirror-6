from pyramid.security import remember, forget, unauthenticated_userid
from pyramid.httpexceptions import HTTPMethodNotAllowed, HTTPFound

from .utils import get_odesk_client


class BaseHandler(object):
    """Base handler with ACL management.

    Inherit and define the desired methods,
    then register views and set permissions.

    """

    def __init__(self, request):
        self.request = request

    def __call__(self):
        """Dispatch the request."""
        method = self.request.method
        try:
            return getattr(self, method.lower())()
        except NotImplementedError:
            raise HTTPMethodNotAllowed(method)

    def get(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

    def put(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError


class Login(BaseHandler):
    def post(self):
        """The login view performs following actions:

        - Redirects user to oDesk. If user is logged in, callback url
          is invoked, otherwise user is asked to login to oDesk.

        """
        client = get_odesk_client(self.request)
        authorize_url = client.auth.get_authorize_url()
        # Save request tokens in the session
        self.request.session['odesk_request_token'] = client.auth.request_token
        self.request.session['odesk_request_token_secret'] = \
            client.auth.request_token_secret

        return HTTPFound(location=authorize_url)


class Logout(BaseHandler):
    def post(self):
        # Forget user
        forget(self.request)
        self.request.session.invalidate()
        return HTTPFound('/')


class OauthCallback(BaseHandler):
    def get(self):
        request = self.request
        verifier = request.GET.get('oauth_verifier')

        request_token = request.session.pop('odesk_request_token', None)
        request_token_secret = request.session.pop(
            'odesk_request_token_secret', None)

        if verifier:
            client = get_odesk_client(
                request, request_token=request_token,
                request_token_secret=request_token_secret)
            oauth_access_token, oauth_access_token_secret = \
                client.auth.get_access_token(verifier)

            client = get_odesk_client(
                request,
                oauth_access_token=oauth_access_token,
                oauth_access_token_secret=oauth_access_token_secret)

            # Get user info
            user_info = client.auth.get_info()
            user_uid = user_info['auth_user']['uid']
            first_name = user_info['auth_user']['first_name']
            last_name = user_info['auth_user']['last_name']

            # Store the user UID, first and last name in session
            remember(request, user_uid)
            request.session['auth.first_name'] = first_name
            request.session['auth.last_name'] = last_name

            # Store oauth access token in session
            request.session['auth.access_token'] = oauth_access_token
            request.session['auth.access_token_secret'] = \
                oauth_access_token_secret

            # Redirect to ``next`` url
            return HTTPFound(location='/')


def forbidden(request):
    if unauthenticated_userid(request):
        # User is authenticated, but not authorized,
        # show logout link instead of login link
        return {'authenticated': True}
    return {'authenticated': False}
