# flake8: noqa

# Flask related configs
#
# Secret key is used for flask session and must be set, make it something
# unique and secret.
SECRET_KEY = "itsnosecret"
#
# Config whether the app served under http or https.
# This is used in oauth redirect uri construction.
SERVER_SCHEME = "http"
# Config server name, must be provided for oauth to work.
#SERVER_NAME = "polaris.eleme.io"
#
# Session protection for Flask-Login extension.
SESSION_PROTECTION = "basic"

# RDB configs
#
# The same as Flask-SQLAlchemy configs
# The default config will create a '.polaris.db' sqlite file in home directory.
SQLALCHEMY_DATABASE_URI = "sqlite:///polaris.db"
SQLALCHEMY_ECHO = False

# Cache configs
#
# Region configs for dogpile.cache
#
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
#
# For more information, refer to http://dogpilecache.readthedocs.org/en/latest/api.html#backend-api
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
#        }
#    }
#}
SOURCES = {}

# CDN configs
#
# CDN_JS is a dict defines js/css assets url.
# This config use cdnjs provided by cloudflare by default, if you want to host
# some of these libs on other CDN, just modify this config.
CDN_JS = {
    # css libs
    "bootstrap.min.css": "//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.0.3/css/bootstrap.min.css",
    "font-awesome.min.css": "//cdnjs.cloudflare.com/ajax/libs/font-awesome/4.0.3/css/font-awesome.min.css",
    "jquery.powertip.css": "//cdnjs.cloudflare.com/ajax/libs/jquery-powertip/1.2.0/css/jquery.powertip.css",
    "jquery.gridster.css": "//cdnjs.cloudflare.com/ajax/libs/jquery.gridster/0.2.1/jquery.gridster.min.css",
    "pace-theme-minimal.css": "//cdnjs.cloudflare.com/ajax/libs/pace/0.4.10/themes/pace-theme-minimal.css",

    # js libs
    "angular.js": "//cdnjs.cloudflare.com/ajax/libs/angular.js/1.2.1/angular.js",
    "bootstrap.min.js": "//cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.0.3/js/bootstrap.min.js",
    "bootstrap-switch.js": "//cdnjs.cloudflare.com/ajax/libs/bootstrap-switch/2.0.0/js/bootstrap-switch.min.js",
    "d3.js": "//cdnjs.cloudflare.com/ajax/libs/d3/3.3.11/d3.min.js",
    "d3.layout.cloud.js": "//www.jasondavies.com/wordcloud/d3.layout.cloud.js",
    "draggabilly.pkgd.js": "//cdnjs.cloudflare.com/ajax/libs/draggabilly/1.0.2/draggabilly.pkgd.js",
    "jquery.min.js": "//cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js",
    "jquery.powertip.js": "//cdnjs.cloudflare.com/ajax/libs/jquery-powertip/1.2.0/jquery.powertip.js",
    "jquery.gridster.js": "//cdnjs.cloudflare.com/ajax/libs/jquery.gridster/0.2.1/jquery.gridster.min.js",
    "pace.min.js": "//cdnjs.cloudflare.com/ajax/libs/pace/0.4.15/pace.min.js",
    "packery.pkgd.min.js": "//cdnjs.cloudflare.com/ajax/libs/packery/1.1.2/packery.pkgd.min.js",
    "script.min.js": "//cdnjs.cloudflare.com/ajax/libs/script.js/2.4.0/script.min.js",
    "vega.js": "//cdnjs.cloudflare.com/ajax/libs/vega/1.3.3/vega.min.js",
    "URI.min.js": "//cdnjs.cloudflare.com/ajax/libs/URI.js/1.11.2/URI.min.js",

    # flat-ui libs
    "flat-ui.css": "/static/flatui/css/flat-ui.css",
    "bootstrap-select.js": "/static/flatui/js/bootstrap-select.js",

    # polaris libs
    "polaris.css": "/static/css/polaris.css",
    "polaris.js": "/static/js/polaris.js",
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

# Logging configs
#
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'polaris': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'general',
        },
    },
    'formatters': {
        'general': {
            'format': "%(asctime)s %(levelname)-6s [%(name)s][%(process)d]"
                      " %(message)s"
        },
    }
}
