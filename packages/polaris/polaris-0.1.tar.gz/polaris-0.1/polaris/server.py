"""
    polaris.server
    ~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Polaris app server.
"""

from flask import Flask, current_app

from polaris.utils import import_string


def create_app():
    app = Flask(__name__)
    app.config.from_object("polaris.defaults")
    app.config.from_object("polaris_config")

    app.secret_key = app.config["SECRET_KEY"]

    ##########
    # Register Extension

    from polaris.models import db
    db.init_app(app)

    from polaris.auth.oauth import oauth
    oauth.init_app(app)

    from polaris.auth.login import login
    login.init_app(app)

    from polaris.auth.form import csrf
    csrf.init_app(app)

    from polaris.auth.principal import principal
    principal.init_app(app)

    ##########
    # Register blueprints

    from polaris.views import (
        api,
        auth,
        chart,
        dashboard,
        errors
    )
    app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(chart)
    app.register_blueprint(errors)

    ##########
    # Register signal handlers

    @app.before_first_request
    def initialize_database():
        db.create_all()

    ##########
    # Dogpile Cache

    from dogpile.cache import make_region
    from polaris.utils import kw_generator

    region = make_region(function_key_generator=kw_generator).configure(
        **app.config["CACHE"])
    app.config["cache_region"] = region

    ##########
    # Register sources

    app.config["ext"] = {}
    for name, path in app.config["EXTENSIONS"].items():
        app.config["ext"][name] = import_string(path)

    app.config["source"] = {}
    for name, cfg in app.config["SOURCES"].items():
        source = app.config["ext"][cfg["ext"]](cache=region, **cfg["params"])
        app.config["source"][name] = source

    ##########
    # CDN support

    def cdn_url_for(asset_name):
        return current_app.config["CDN_JS"][asset_name]
    app.jinja_env.globals['cdn_url_for'] = cdn_url_for

    return app
