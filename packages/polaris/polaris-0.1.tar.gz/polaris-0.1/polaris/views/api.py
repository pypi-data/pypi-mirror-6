"""
    polaris.views.api
    ~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Polaris RESTful APIs.
"""

import http.client as http
import urllib

import sqlalchemy

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
)

from flask_login import login_required, current_user
from flask_principal import Identity, identity_changed

from polaris.models import (
    db,
    Chart,
    Dashboard
)
from polaris.convert import to_df, to_data, to_vega
from polaris.auth.principal import (
    ChartViewPermission,
    ChartEditPermission,
    DashboardViewPermission,
    DashboardEditPermission,
)

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/vega/<string:vega_type>/<string:uuid>")
@login_required
def api_vega(vega_type, uuid):
    """Vega api.
    """
    if not ChartViewPermission(uuid).can():
        abort(http.FORBIDDEN)

    chart = db.session.query(Chart).get(uuid)
    if not chart:
        abort(http.NOT_FOUND)

    options = {k: v for k, v in request.args.items()}
    vega = to_vega(to_df(chart, **options), vega_type)
    return jsonify(vega), http.OK


@api.route("/view/<string:vega_type>/<string:uuid>")
@login_required
def api_view(vega_type, uuid):
    """Vega view api.
    This will render the vega js to simple chart.
    """
    if not ChartViewPermission(uuid).can():
        abort(http.FORBIDDEN)

    url_args = urllib.parse.urlencode(request.args)
    return render_template("vega.jinja", vega_type=vega_type, uuid=uuid,
                           url_args=url_args)


@api.route("/data/<string:data_type>/<string:uuid>")
@login_required
def api_data(data_type, uuid):
    """Data api.
    """
    if not ChartViewPermission(uuid).can():
        abort(http.FORBIDDEN)

    chart = db.session.query(Chart).get(uuid)
    if not chart:
        abort(http.NOT_FOUND)

    options = {k: v for k, v in request.args.items()}
    return to_data(to_df(chart, **options), data_type), http.OK


@api.route("/dashboard/<string:uuid>", methods=["GET", "PUT", "DELETE"])
@login_required
def api_dashboard(uuid):
    """Dashboard REST api.
    """
    view_permission = DashboardViewPermission(uuid)
    edit_permission = DashboardEditPermission(uuid)
    if request.method == 'GET' and not view_permission.can():
        abort(http.FORBIDDEN)
    if request.method in ("PUT", "DELETE") and not edit_permission.can():
        abort(http.FORBIDDEN)

    dashboard = db.session.query(Dashboard).get(uuid)
    if not dashboard:
        abort(http.NOT_FOUND)

    if request.method == "GET":
        return jsonify({"dashboard": dashboard.to_dict()}), http.OK

    elif request.method == "PUT":
        dashboard.name = request.json["name"]
        dashboard.slug = request.json["slug"]
        dashboard.is_public = request.json["is_public"]
        dashboard.description = request.json["description"]
        try:
            db.session.commit()
            return jsonify({"dashboard": dashboard.to_dict()}), http.OK
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            abort(http.INTERNAL_SERVER_ERROR)

    elif request.method == "DELETE":
        db.session.delete(dashboard)
        try:
            db.session.commit()
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(current_user.id))
            return jsonify({"result": True}), http.OK
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            abort(http.INTERNAL_SERVER_ERROR)


@api.route("/dashboards", methods=["GET", "PUT", "POST"])
@login_required
def api_dashboards():
    """Dashboards REST api.
    """
    if request.method == "GET":
        dashboards = [
            d.to_dict()
            for d in db.session.query(Dashboard).
            filter((Dashboard.user_id == current_user.id) |
                   (Dashboard.is_public))]
        return jsonify({"dashboards": dashboards}), http.OK

    elif request.method == "POST":
        if not request.json or not "description" in request.json:
            abort(http.BAD_REQUEST)

        kwargs = dict(user_id=current_user.id, **request.json)
        dashboard = Dashboard(**kwargs)
        db.session.add(dashboard)
        try:
            db.session.commit()
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(current_user.id))
            return jsonify({"dashboard": dashboard.to_dict()}), http.OK
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            abort(http.INTERNAL_SERVER_ERROR)


@api.route("/chart/<string:uuid>", methods=["GET", "PUT", "DELETE"])
@login_required
def api_chart(uuid):
    """Chart REST api.
    """
    view_permission = ChartViewPermission(uuid)
    edit_permission = ChartEditPermission(uuid)
    if request.method == 'GET' and not view_permission.can():
        abort(http.FORBIDDEN)
    if request.method in ("PUT", "DELETE") and not edit_permission.can():
        abort(http.FORBIDDEN)

    chart = db.session.query(Chart).get(uuid)
    if not chart:
        abort(http.NOT_FOUND)

    if request.method == "GET":
        return jsonify({"chart": chart.to_dict()}), http.OK

    elif request.method == "PUT":
        # Only allow update for name, slug and options.
        chart.name = request.json["name"]
        chart.slug = request.json["slug"]
        chart.is_public = request.json["is_public"]
        chart.options = request.json["options"]

        try:
            db.session.commit()
            return jsonify({"chart": chart.to_dict()}), http.OK
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            abort(http.INTERNAL_SERVER_ERROR)

    elif request.method == "DELETE":
        db.session.delete(chart)
        try:
            db.session.commit()
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(current_user.id))
            return jsonify({"result": True}), http.OK
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            abort(http.INTERNAL_SERVER_ERROR)


@api.route("/charts", methods=["GET", "POST"])
@login_required
def api_charts():
    """Charts REST api.
    """
    if request.method == "GET":
        charts = [
            c.to_dict()
            for c in db.session.query(Chart).
            filter((Chart.user_id == current_user.id) | (Chart.is_public))
        ]
        return jsonify({"charts": charts}), http.OK

    elif request.method == "POST":
        if not request.json or not "source" in request.json or \
                not "options" in request.json:
            abort(http.BAD_REQUEST)

        if "id" in request.json:
            request.json.pop("id")

        kwargs = dict(user_id=current_user.id, **request.json)
        chart = Chart(**kwargs)
        db.session.add(chart)
        try:
            db.session.commit()
            identity_changed.send(current_app._get_current_object(),
                                  identity=Identity(current_user.id))
            return jsonify({"chart": chart.to_dict()}), http.OK
        except sqlalchemy.exc.SQLAlchemyError:
            db.session.rollback()
            abort(http.INTERNAL_SERVER_ERROR)


@api.route("/sources")
@login_required
def api_sources():
    """List all available polaris sources.
    """
    sources = list(current_app.config["source"])
    return jsonify({"sources": sources}), http.OK
