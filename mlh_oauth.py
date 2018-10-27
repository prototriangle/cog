import json
from flask import redirect, url_for, request, current_app, session
from rauth import OAuth1Service, OAuth2Service
from hardwarecheckout import config

class MLHSignIn(object):
    def __init__(self):
        credentials = config.OAUTH_CREDENTIALS
        self.consumer_id = credentials["id"]
        self.consumer_secret = credentials["secret"]
        self.service = OAuth2Service(
            name="mlh",
            client_id = self.consumer_id,
            client_secret = self.consumer_secret,
            authorize_url='https://my.mlh.io/oauth/authorize',
            access_token_url='https://my.mlh.io/oauth/token',
            base_url='https://my.mlh.io/'
        )

    def get_callback_url(self):
        return url_for("oauth_callback", _external=True)

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            raise ValueError(str(request.args))
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=json.loads
        )
        me = oauth_session.get('/api/v2/user.json').json()

        return (
            me.get('data').get('id'),
            me.get('data').get('email')
        )

