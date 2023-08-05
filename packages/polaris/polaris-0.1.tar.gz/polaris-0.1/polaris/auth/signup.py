import hashlib
import os

from polaris.models import db, User, OauthUser


def local_signup(email, password):
    user = db.session.query(User).filter(User.email == email).first()
    if user:
        return user

    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user


def oauth_signup(email, provider):
    oauth_user = db.session.query(OauthUser).\
        filter(OauthUser.email == email).\
        filter(OauthUser.provider == provider).\
        first()
    if oauth_user:
        return oauth_user.user

    user = db.session.query(User).filter(User.email == email).first()
    if not user:
        random_pwd = hashlib.sha1(os.urandom(64)).hexdigest()
        user = User(email=email, password=random_pwd, is_valid=True)
        oauth_user = OauthUser(user=user, email=email, provider=provider)
        db.session.add(oauth_user)
        db.session.commit()
        return user
    else:
        oauth_user = OauthUser(user=user, email=email, provider=provider)
        db.session.add(oauth_user)
        db.session.commit()
        return user
