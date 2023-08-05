import collections
import functools

from flask_login import current_user
from flask_principal import Principal, identity_loaded, Permission, UserNeed

from polaris.models import db, Chart, Dashboard

principal = Principal()

Need = collections.namedtuple('Need', ['method', 'type', 'value'])
ChartViewNeed = functools.partial(Need, 'view', 'chart')
ChartEditNeed = functools.partial(Need, 'edit', 'chart')

DashboardViewNeed = functools.partial(Need, 'view', 'dashboard')
DashboardEditNeed = functools.partial(Need, 'edit', 'dashboard')


class ChartViewPermission(Permission):
    def __init__(self, id):
        need = ChartViewNeed(str(id))
        super(ChartViewPermission, self).__init__(need)


class ChartEditPermission(Permission):
    def __init__(self, id):
        need = ChartEditNeed(str(id))
        super(ChartEditPermission, self).__init__(need)


class DashboardViewPermission(Permission):
    def __init__(self, id):
        need = DashboardViewNeed(str(id))
        super(DashboardViewPermission, self).__init__(need)


class DashboardEditPermission(Permission):
    def __init__(self, id):
        need = DashboardEditNeed(str(id))
        super(DashboardEditPermission, self).__init__(need)


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    # do nothing to anonymous user
    if not hasattr(current_user, "id"):
        return

    identity.user = current_user

    # Add the UserNeed to the identity
    identity.provides.add(UserNeed(str(current_user.id)))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, "charts"):
        for chart in current_user.charts:
            identity.provides.add(ChartEditNeed(str(chart.id)))
    view_charts = db.session.query(Chart).\
        filter((Chart.user_id == current_user.id) | (Chart.is_public))
    for chart in view_charts:
        identity.provides.add(ChartViewNeed(str(chart.id)))

    # Assuming the User model has a list of posts the user
    # has authored, add the needs to the identity
    if hasattr(current_user, "dashboards"):
        for dashboard in current_user.dashboards:
            identity.provides.add(DashboardEditNeed(str(dashboard.id)))

    view_dashboards = db.session.query(Dashboard).\
        filter((Dashboard.user_id == current_user.id) | (Dashboard.is_public))
    for dashboard in view_dashboards:
        identity.provides.add(DashboardViewNeed(str(dashboard.id)))
