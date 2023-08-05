"""
    polaris.views.auth
    ~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Polaris user auth view.
"""


import http.client as http

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed

from polaris.auth.oauth import oauth
from polaris.auth.form import SignupForm, LoginForm
from polaris.auth.signup import local_signup, oauth_signup

from polaris.models import db, User


auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    if not current_user.is_authenticated():
        form = SignupForm()
        return render_template(
            "index.jinja", form=form,
            oauth_enabled=current_app.config["OAUTH_ENABLED"]
        )
    return redirect(url_for("dashboard.list"))


@auth.route("/signup/", methods=["POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = local_signup(form.email.data, form.password.data)
        login_user(user, remember=True, force=True)
        identity_changed.send(current_app._get_current_object(),
                              identity=Identity(user.id))
        return redirect(request.args.get("next") or url_for("auth.index"))
    flash("signup failed")
    return redirect(url_for("auth.index"))


@auth.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).\
            filter(User.email == form.email.data).\
            first()
        if user and user.auth(form.password.data):
            login_user(user, remember=True, force=True)
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(user.id))
            flash("Login success!")
            return redirect(request.args.get("next") or url_for("auth.index"))
        flash("Login failed!")
    return redirect(url_for("auth.index"))


@auth.route("/oauth/<string:provider>")
def oauth_login(provider):
    """Return all charts.
    """
    if not provider in oauth.remote_apps:
        return jsonify(oauth.remote_apps.keys())
        abort(http.NOT_FOUND)
    if current_user.is_authenticated():
        return redirect(url_for("auth.index"))

    oauth_client = oauth.remote_apps[provider]
    scheme = current_app.config["SERVER_SCHEME"]
    cb_url = url_for('auth.oauth_authorized', _scheme=scheme,
                     provider=provider, _external=True)
    return oauth_client.authorize(callback=cb_url)


@auth.route("/oauth/authorized/<string:provider>")
def oauth_authorized(provider):
    if not provider in oauth.remote_apps:
        abort(http.NOT_FOUND)

    oauth_client = oauth.remote_apps[provider]
    tk = oauth_client.authorized_handler(lambda r: (r['access_token'], ''))()
    session['{}_token'.format(provider)] = tk

    email = oauth_client._emailgetter()
    user = oauth_signup(email, provider)
    login_user(user, remember=True)
    identity_changed.send(current_app._get_current_object(),
                          identity=Identity(user.id))
    flash("Login success!")
    return redirect(request.args.get("next") or url_for("auth.index"))


@auth.route("/logout/")
@login_required
def logout():
    """Return all charts.
    """
    logout_user()
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    flash("Logout success!")
    return redirect(url_for("auth.index"))
