"""
    polaris.views.dashboard
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Polaris dashboards.
"""

import http.client as http

from flask import (
    Blueprint,
    abort,
    render_template,
)

from flask_login import current_user, login_required

from polaris.models import db, Dashboard
from polaris.auth.principal import DashboardEditPermission


dashboard = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard.route("/")
@login_required
def list():
    """Return all dashboards.
    """
    return render_template("dashboard_list.jinja", user=current_user)


@dashboard.route("/<string:uuid>", methods=["GET"])
@login_required
def view(uuid):
    """Return dashboard view.
    """
    dashboard = db.session.query(Dashboard).get(uuid)
    if not dashboard:
        abort(http.NOT_FOUND)
    return render_template("dashboard_view.jinja", user=current_user,
                           uuid=uuid)


@dashboard.route("/new", methods=["GET"])
@dashboard.route("/edit/<string:uuid>", methods=["GET"])
@login_required
def edit(uuid=None):
    """Edit or create new dashboard.
    """
    if uuid:
        edit_permission = DashboardEditPermission(uuid)
        if not edit_permission.can():
            abort(http.FORBIDDEN)

        dashboard = db.session.query(Dashboard).get(uuid)
        if not dashboard:
            abort(http.NOT_FOUND)
        return render_template("dashboard_edit.jinja",
                               **dashboard.to_dict())
    else:
        return render_template("dashboard_edit.jinja", user=current_user)
