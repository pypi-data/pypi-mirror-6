"""
Flask-FBLogin
"""

from base64 import urlsafe_b64decode as b64decode
from base64 import urlsafe_b64encode as b64encode
from functools import wraps
from urllib import urlencode
from urlparse import parse_qsl

import requests
from flask import abort, current_app, redirect, request, url_for
from flask_login import login_user, LoginManager, make_secure_token

FACEBOOK_OAUTH2_AUTH_URL = 'https://www.facebook.com/dialog/oauth'
FACEBOOK_OAUTH2_TOKEN_URL = 'https://graph.facebook.com/oauth/access_token'
FACEBOOK_OAUTH2_ME_URL = 'https://graph.facebook.com/me'


class FBLogin(object):
    """
    Main extension class
    """

    def __init__(self, app=None, login_manager=None):
        if login_manager:
            self.login_manager = login_manager
        else:
            self.login_manager = LoginManager()

        if app:
            self._app = app
            self.init_app(app)

    def init_app(self, app, add_context_processor=True, login_manager=None):
        """
        Initialize with app configuration. Existing
        `flask_login.LoginManager` instance can be passed.
        """

        if login_manager:
            self.login_manager = login_manager
        else:
            self.login_manager = LoginManager()

        # Check if login manager has been init
        if not hasattr(app, 'login_manager'):
            self.login_manager.init_app(
                app,
                add_context_processor=add_context_processor)

        # Clear flashed messages since we redirect to auth immediately
        self.login_manager.login_message = None
        self.login_manager.needs_refresh_message = None

        # Set default unauthorized callback
        self.login_manager.unauthorized_handler(self.unauthorized_callback)

    @property
    def app(self):
        return getattr(self, '_app', current_app)

    @property
    def scopes(self):
        return self.app.config.get('FACEBOOK_LOGIN_SCOPES', 'email')

    @property
    def client_id(self):
        return self.app.config['FACEBOOK_LOGIN_CLIENT_ID']

    @property
    def client_secret(self):
        return self.app.config['FACEBOOK_LOGIN_CLIENT_SECRET']

    @property
    def redirect_uri(self):
        return self.app.config.get('FACEBOOK_LOGIN_REDIRECT_URI')

    @property
    def redirect_scheme(self):
        return self.app.config.get('FACEBOOK_LOGIN_REDIRECT_SCHEME', 'http')

    def sign_params(self, params):
        return b64encode(urlencode(dict(sig=make_secure_token(**params),
                                        **params)))

    def parse_state(self, state):
        return dict(parse_qsl(b64decode(str(state))))

    def login_url(self, params=None, **kwargs):
        """
        Return login url with params encoded in state
        """

        kwargs.setdefault('response_type', 'code')
        scopes = kwargs.pop('scopes', self.scopes.split(','))
        redirect_uri = kwargs.pop('redirect_uri', self.redirect_uri)
        state = self.sign_params(params or {})

        return FACEBOOK_OAUTH2_AUTH_URL + '?' + urlencode(
            dict(client_id=self.client_id,
                 scope=','.join(scopes),
                 redirect_uri=redirect_uri,
                 state=state,
                 **kwargs))

    def unauthorized_callback(self):
        """
        Redirect to login url with next param set as request.url
        """
        return redirect(self.login_url(params=dict(next=request.url)))

    def exchange_code(self, code, redirect_uri):
        """
        Exchanges code for token/s
        """

        token = dict(parse_qsl(requests.post(FACEBOOK_OAUTH2_TOKEN_URL, data=dict(
            code=code,
            redirect_uri=redirect_uri,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )).text))

        if not token or token.get('error'):
            return

        return token

    def get_me(self, access_token):
        me = requests.get(FACEBOOK_OAUTH2_ME_URL, params=dict(
            access_token=access_token,
        )).json

        if not me or me.get('error'):
            return

        return me

    def inspect_token(self, input_token):
        return NotImplemented()

    def oauth2callback(self, view_func):
        """
        Decorator for OAuth2 callback.
        """

        @wraps(view_func)
        def decorated(*args, **kwargs):
            # Check for error in authorization
            if 'error' in request.args:
                return self.login_manager.unauthorized()

            # Check sig
            params = self.parse_state(request.args.get('state'))
            if params.pop('sig', None) != make_secure_token(**params):
                return self.login_manager.unauthorized()

            # Get token
            token = self.exchange_code(
                request.args['code'],
                url_for(
                    request.endpoint,
                    _external=True,
                    _scheme=self.redirect_scheme,
                ),
            )
            if token:
                params.update(token=token)
            else:
                return self.login_manager.unauthorized()

            # Get user info
            me = self.get_me(token['access_token'])
            if me:
                params.update(me=me)
            else:
                return self.login_manager.unauthorized()

            # Get user instance
            user = self.user_callback(**me)
            if user:
                login_user(user)
            else:
                return self.login_manager.unauthorized()

            return view_func(**params)

        return decorated

    def user_loader(self, callback):
        self.user_callback = callback
        return callback

