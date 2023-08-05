"""
    polaris.views.chart
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Polaris charts.
"""

import http.client as http

from flask import (
    Blueprint,
    abort,
    current_app,
    render_template,
)

from flask_login import current_user, login_required

from polaris.models import db, Chart
from polaris.auth.principal import ChartEditPermission

chart = Blueprint("chart", __name__, url_prefix="/chart")


@chart.route("/")
@login_required
def list_chart():
    """Return all charts.
    """
    return render_template("chart_list.jinja", user=current_user)


@chart.route("/<string:uuid>", methods=["GET"])
@login_required
def view(uuid):
    """Return chart view.
    """
    chart = db.session.query(Chart).get(uuid)
    if not chart:
        abort(http.NOT_FOUND)
    return render_template("chart_view.jinja", user=current_user, uuid=uuid)


@chart.route("/new", methods=["GET"])
@chart.route("/edit/<string:uuid>", methods=["GET"])
@login_required
def edit(uuid=None):
    """Edit or create new chart.
    """
    if uuid:
        edit_permission = ChartEditPermission(uuid)
        if not edit_permission.can():
            abort(http.FORBIDDEN)

        chart = db.session.query(Chart).get(uuid)
        if not chart:
            abort(http.NOT_FOUND)
        return render_template("chart_edit.jinja", **chart.to_dict())
    else:
        return render_template("chart_edit.jinja",
                               user=current_user,
                               sources=list(current_app.config["source"]))
