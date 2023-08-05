"""
    polaris.wsgi
    ~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    WSGI app.
"""

from polaris.server import create_app

app = create_app()
