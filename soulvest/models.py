# coding: utf-8

from __future__ import absolute_import

import flask.ext.login as flask_login

from soulvest import config, secret_keys, login_manager
from itsdangerous import URLSafeTimedSerializer

import hashlib
import datetime
import requests
import logging

from google.appengine.ext import ndb

ts = URLSafeTimedSerializer(config.SALT)

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


class ActivationLink(Base):
  token = ndb.StringProperty(default='')
  expiry = ndb.DateTimeProperty(auto_now=True)
  valid = ndb.BooleanProperty(default=False)
  user = ndb.KeyProperty(kind='User')


def password_hash(user, password):
  m = hashlib.sha256()
  m.update(user.key.urlsafe())
  m.update(user.created.isoformat())
  m.update(m.hexdigest())
  m.update(password.encode('utf-8'))
  m.update(config.SALT)
  return m.hexdigest()


def get_user_by_email(email):
  return User.query(User.email == email).get()

def get_user_by_email_and_password(email, password):
  user = User.query(ndb.AND(User.email == email, User.verified == True)).get()
  if not user:
    return None
  if user.password_hash == password_hash(user, password):
    return user
  return None


def get_user_by_activation_token(token):
  try:
    email = ts.loads(token, salt="email-activation-link-key", max_age=86400)
  except:
    return None
  # only return a user if email matches and they haven't already been verified
  return User.query(ndb.AND(User.email == email, User.verified == False)).get()
  # return User.query(User.email == email).get()


def send_activation_link(user):
  token = ts.dumps(user.email, salt='email-activation-link-key')
  activation_url = 'http://{}/activate?token={}'.format(config.domain, token)
  request_url = 'https://api.mailgun.net/v3/{}/messages'.format(config.mailgun_domain)
  request = requests.post(
    request_url, auth=('api', secret_keys.mailgun_key), data={
      'from': 'activation@soulvest.net',
      'to': user.email,
      'subject': 'SOULVEST Activation Link',
      'text': 'Thanks for signing up for SOULVEST. Please click the link below to activate your account: {}'.format(activation_url)
    })
  return request

def get_user_by_password_reset_token(token):
  try:
    email = ts.loads(token, salt="password-reset-link-key", max_age=86400)
  except:
    return None
  # only return a user if email matches and they haven't already been verified
  return User.query(ndb.AND(User.email == email, User.verified == False)).get()
  # return User.query(User.email == email).get()


def send_password_reset_link(user):
  token = ts.dumps(user.email, salt='password-reset-link-key')
  activation_url = 'http://{}/reset-password?token={}'.format(config.domain, token)
  request_url = 'https://api.mailgun.net/v3/{}/messages'.format(config.mailgun_domain)
  request = requests.post(
    request_url, auth=('api', secret_keys.mailgun_key), data={
      'from': 'password@soulvest.net',
      'to': user.email,
      'subject': 'SOULVEST Password Reset Link',
      'text': 'Please click the link below to reset your password: {}'.format(activation_url)
    })
  return request


@login_manager.user_loader
def user_loader(email):
  return User.query(ndb.AND(User.email == email, User.verified == True)).get()


@login_manager.request_loader
def request_loader(request):
  email = request.form.get('sign_in_email')
  password = request.form.get('sign_in_password')
  return get_user_by_email_and_password(email, password)
