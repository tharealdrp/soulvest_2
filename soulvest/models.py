# coding: utf-8

from __future__ import absolute_import

import flask.ext.login as flask_login

from soulvest import config, login_manager

import hashlib

from google.appengine.ext import ndb


class Base(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  version = ndb.IntegerProperty(default=1)


class User(Base, flask_login.UserMixin):
  name = ndb.StringProperty(required=False)
  username = ndb.StringProperty(required=False)
  email = ndb.StringProperty(default='')
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  permissions = ndb.StringProperty(repeated=True)
  verified = ndb.BooleanProperty(default=False)
  verification_token = ndb.StringProperty(default='')
  token = ndb.StringProperty(default='')
  password_hash = ndb.StringProperty(default='')
  password_reset_token = ndb.StringProperty(default='')
  plaid_token = ndb.StringProperty(default='')
  plaid_meta = ndb.StringProperty(default='')


def password_hash(user, password):
  m = hashlib.sha256()
  m.update(user.key.urlsafe())
  m.update(user.created.isoformat())
  m.update(m.hexdigest())
  m.update(password.encode('utf-8'))
  m.update(config.SALT)
  return m.hexdigest()


def get_user_by_email_and_password(email, password):
  user = User.query(ndb.AND(User.email == email, User.verified == True)).get()
  if not user:
    return None
  if user.password_hash == password_hash(user, password):
    return user
  return None


@login_manager.user_loader
def user_loader(email):
  return User.query(ndb.AND(User.email == email, User.verified == True)).get()


@login_manager.request_loader
def request_loader(request):
  email = request.form.get('sign_in_email')
  password = request.form.get('sign_in_password')
  return get_user_by_email_and_password(email, password)
