import json
import uuid
import datetime

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash


##########
# Models
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "pl_user"

    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, nullable=False, unique=True)
    nickname = db.Column(db.String, default='', nullable=False)
    _password = db.Column("password", db.String, nullable=False)
    is_valid = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.now,
                           nullable=False)

    # foreign key ref
    charts = db.relationship("Chart",
                             backref=db.backref("user", lazy="joined"))
    dashboards = db.relationship("Dashboard",
                                 backref=db.backref("user", lazy="joined"))

    # for flask-login
    is_authenticated = lambda self: True
    is_active = lambda self: self.is_valid
    is_anonymous = lambda self: False
    get_id = lambda self: self.id

    def __repr__(self):
        return "<User(id={}, email={})>".format(self.id, self.email)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, pwd):
        self._password = generate_password_hash(pwd)

    def auth(self, pwd):
        return check_password_hash(self.password, pwd)


class OauthUser(db.Model):
    __tablename__ = "pl_oauth_user"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.UUID, db.ForeignKey('pl_user.id'), nullable=False)
    email = db.Column(db.String, nullable=False)
    provider = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.now,
                           nullable=False)

    user = db.relationship("User")


class Dashboard(db.Model):
    __tablename__ = "pl_dashboard"

    # column definitions
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, default='', nullable=False)
    description = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.UUID, db.ForeignKey('pl_user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.now,
                           nullable=False)

    def __repr__(self):
        return "Dashboard({})".format(str(self))

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {"id": str(self.id), "name": self.name, "slug": self.slug,
                "description": self.description, "is_public": self.is_public,
                "user_id": self.user.id, "user": self.user.email}


class Chart(db.Model):
    __tablename__ = "pl_chart"

    # column definitions
    id = db.Column(db.UUID, primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, default='', nullable=False)
    approved = db.Column(db.Boolean, default=False, nullable=False)
    source = db.Column(db.String, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.UUID, db.ForeignKey('pl_user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.now,
                           nullable=False)

    def __repr__(self):
        return "Chart({})".format(str(self))

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {"id": str(self.id), "name": self.name,
                "slug": self.slug, "source": self.source,
                "options": self.options, "is_public": self.is_public,
                "user_id": self.user.id, "user": self.user.email}
