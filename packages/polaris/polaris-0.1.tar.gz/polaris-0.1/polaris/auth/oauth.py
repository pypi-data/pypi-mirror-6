"""
    polaris.auth.oauth
    ~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Polaris oauth management.
"""

import json

from flask import session

from flask_oauthlib.client import OAuth, OAuthRemoteApp


def emailgetter(self, f):
    """
    Register a function as email getter.
    """
    self._emailgetter = f
    return f
OAuthRemoteApp.emailgetter = emailgetter

oauth = OAuth()


#####
# OAuth Clients

google = oauth.remote_app(
    'google',
    request_token_params={'scope': 'email'},
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    app_key='GOOGLE')
google.emailgetter(lambda: google.get("userinfo").data.get("email"))

github = oauth.remote_app(
    'github',
    request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    content_type="application/vnd.github.v3+json",
    app_key='GITHUB')
github.emailgetter(
    lambda: next(filter(
        lambda x: x['primary'] and x['verified'],
        json.loads(github.get("user/emails").data.decode('utf-8')))
    ).get("email"))

facebook = oauth.remote_app(
    'facebook',
    request_token_params={'scope': 'email'},
    base_url='https://graph.facebook.com',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    app_key='FACEBOOK')
facebook.emailgetter(
    lambda: facebook.get("/me?fields=name,email").data.get("email"))


# a hack to use github v3 api
def v3_header(uri, headers, body):
    headers["Accept"] = "application/vnd.github.v3+json"
    return uri, headers, body
github.pre_request = v3_header


#####
# Token getter

for name, client in oauth.remote_apps.items():
    # n=name is to make a isolate scope in for loop
    client.tokengetter(lambda n=name: session.get('{}_token'.format(n)))
