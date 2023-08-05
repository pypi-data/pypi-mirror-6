"""
    polaris.cmd
    ~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Polaris console command.
"""

import os
import hashlib

from os.path import expanduser


CONFIG_TMPL = """
# Polaris config template
#
# You may refer to polaris.defaults for the default settings.

# Flask related configs
#
# Secret key is used for flask session and must be set, make it something
# unique and secret.
SECRET_KEY = "%(default_secret)s"
#
# Config whether the app served under http or https.
# This is used in oauth redirect uri construction.
SERVER_SCHEME = "http"
# Config server name, must be provided for oauth to work.
#SERVER_NAME = "polaris.eleme.io"
#
# Session protection for login users.
SESSION_PROTECTION = "basic"

# RDB configs
#
# The same as Flask-SQLAlchemy configs
SQLALCHEMY_DATABASE_URI = "%(default_db)s"

# Cache configs
#
# Region configs for dogpile.cache, refer to dogpile.cache documentation for
# more info.
# You can use memcache or redis as a more advanced cache backend.
# Redis backend config example:
#
# CACHE = {
#     "backend": 'dogpile.cache.redis',
#     "arguments": {
#         'host': 'localhost',
#         'port': 6379,
#         'db': 0,
#         'redis_expiration_time': 60*60*12,   # 12 hours
#         'distributed_lock': True
#     }
# }
CACHE = {
    "backend": "dogpile.cache.memory_pickle"
}

# Extension configs
#
# EXTENSIONS defines where to find polaris extensions.
# Extensions can be easily customized, just add your extension path to
# customized settings.
EXTENSIONS = {
    "database": "polaris.ext.database:Database",
    "rand": "polaris.ext.rand:Rand"
}

# Sources configs
#
# SOURCES is a dict contains all sources for polaris charts.
# An extension can be used by many sources with different settings.
#
# A typical settings should be like this:
# SOURCES = {
#    "source_name": {
#        "ext": "extension name"
#        "params": {
#            // extension init params
#        }
#    }
#}
#
# This is an example using the default postgres extension.
#SOURCES = {
#    "prod": {
#        "ext": "database",
#        "params": {
#            "url": "postgresql://{user}:{passwd}@{host}/{database}",
#            "pool_size": 10
#        }
#    }
#}
SOURCES = {
    "random": {
        "ext": "rand",
        "params": {}
    }
}

# OAuth configs
#
# Polaris have 3 oauth login support build in: google, facebook, github.
OAUTH_ENABLED = ["google", "facebook", "github"]

# To make it actually work, you need to add consumer key and consumer secret
# for oauth services.
#
#GOOGLE_CONSUMER_KEY = ""
#GOOGLE_CONSUMER_SECRET = ""
#
#GITHUB_CONSUMER_KEY = ""
#GITHUB_CONSUMER_SECRET = ""
#
#FACEBOOK_CONSUMER_KEY = ""
#FACEBOOK_CONSUMER_SECRET = ""
"""


def init():
    with open("polaris_config.py", 'w') as f:
        default_secret = hashlib.sha1(os.urandom(64)).hexdigest()
        default_db = "sqlite:///{}/.polaris.db".format(expanduser("~"))
        f.write(CONFIG_TMPL % dict(default_secret=default_secret,
                                   default_db=default_db))

    print("Example config generated in polaris.conf.py")
    print("Start server with:\n$ polaris serve")


def serve(host="0.0.0.0", port=6789, debug=False):
    from polaris.server import create_app
    app = create_app()
    app.run(host=host, port=port, debug=debug)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="choose from init or serve")
    parser.add_argument("-b", "--bind", default="0.0.0.0:6789",
                        help="bind to host:port")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable debug")
    args = parser.parse_args()
    if args.action == "init":
        return init()
    elif args.action == "serve":
        if ':' in args.bind:
            host, port = args.bind.split(':')
        else:
            host, port = args.bind, 6789
        return serve(host=host, port=int(port), debug=args.debug)
    else:
        parser.print_help()
