"""`main` is the top level module for our Flask application."""
from uuid import uuid4
import hashlib
import requests
import flask
from functools import wraps
from flask import Flask, jsonify, abort, make_response, redirect, request, url_for
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from google.appengine.ext import ndb

import json

# plaid
from plaid import Client
Client.config({
    'url': 'https://tartan.plaid.com',
    'suppress_http_errors': True,
})

client = Client(client_id='test_id', secret='test_secret')

#import auth
import model.user

import logging

from validate_email import validate_email

SALT = 'development'

app = Flask(__name__, static_url_path="")
api = Api(app)


##########################################
# API Guards
##########################################
def get_user_by_authorization_token(args):
  data = args['Authorization'].encode('ascii','ignore')
  token = str.replace(str(data), 'Bearer ','')
  try:
    user = model.User.query(model.User.token == token).get()
    return user
  except:
    abort(422, 'Permission denied, please log in.')

def logged_in_redirect(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if not 'Authorization' in args:
      return f(*args, **kwargs)
    user = None
    data = args['Authorization'].encode('ascii','ignore')
    token = str.replace(str(data), 'Bearer ','')
    try:
      user = model.User.query(model.User.token == token).get()
      if not user:
        return f(*args, **kwargs)
    except:
      return f(*args, **kwargs)
    return redirect(url_for('static', filename='/account.html'))
  return decorated_function

# TODO Use JWT?
def login_required(args):
  if not 'Authorization' in args:
    abort(401)
  user = None
  data = args['Authorization'].encode('ascii','ignore')
  token = str.replace(str(data), 'Bearer ','')
  try:
    user = model.User.query(model.User.token == token).get()
    if not user:
      abort(401)
  except:
    abort(401)


@app.route('/')
def welcome():
  return app.send_static_file('index.html')

##########################################
# Sign in
##########################################
def valid_email(email_str):
  """Return email_str if valid, raise an exception otherwise."""
  if not validate_email(email_str):
    raise ValueError('{} is not a valid email'.format(email_str))
  return email_str


def password_hash(user, password):
  m = hashlib.sha256()
  m.update(user.key.urlsafe())
  m.update(user.created.isoformat())
  m.update(m.hexdigest())
  m.update(password.encode('utf-8'))
  m.update(SALT)
  return m.hexdigest()


def get_user_by_email_and_password(email, password):
  user = model.User.query(ndb.AND(model.User.email == email, model.User.verified == True)).get()
  if not user:
    return None
  if user.password_hash == password_hash(user, password):
    return user
  return None


def signin_user(user):
  user.token = uuid4().hex
  user.put()
  return user.token


class SignInAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument(
      'email', type = valid_email, required = True)
    self.reqparse.add_argument(
      'password', type = str, required = True,
      help = 'Password required')
    super(SignInAPI, self).__init__()

  def get(self):
    return {'result' : 'success'}

  def post(self):
    args = self.reqparse.parse_args()
    user = get_user_by_email_and_password(args['email'], args['password'])
    if not user:
      abort(422, 'Invalid email or password')
    token = signin_user(user)
    if not token:
      abort(422, 'Something went wrong')
    return {'result' : 'success', 'token' : token, 'email' : user.email}


api.add_resource(SignInAPI, '/api/v1/signin/', endpoint='signin')


##########################################
# Sign Up
##########################################
def create_name_from_email(email):
  return re.sub(r'_+|-+|\.+|\++', ' ', email.split('@')[0]).title()

def valid_password(password_str):
  """Return password if valid, raise an exception otherwise."""
  if not isinstance(password_str, basestring):
    raise ValueError('alphanumeric only please'.format(password_str))
  if len(password_str) < 8:
    raise ValueError('Password must be at least 8 characters long')
  return password_str


def valid_signup_email(email_str):
  """Return email_str if it , raise an exception otherwise."""
  if not valid_email(email_str):
    raise ValueError('{} is not a valid email'.format(email_str))
  user = model.User.query(model.User.email == email_str).get()
  if user:
    raise ValueError('Email already taken')
  return email_str


class SignUpAPI(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument(
      'email', type = valid_signup_email, required = True)
    self.reqparse.add_argument(
      'password', type = valid_password, required = True)
    self.reqparse.add_argument(
      'confirm_password', type = valid_password, required = True,
      help = 'Please confirm your password')

    super(SignUpAPI, self).__init__()

  def get(self):
    return {'result' : 'success'}

  def post(self):
    args = self.reqparse.parse_args()
    email = args['email'].lower()
    # this should rarely, if ever, occur
    if email == '':
      abort(422, 'Invalid email, failed converting to lowercase.')

    if args['password'] != args['confirm_password']:
      abort(400, "Passwords don't match")

    # TODO: require email verification
    user = model.User(email=email, verified=True)
    user.put()
    user.password_hash = password_hash(user, args['password'])
    user.put()
    token = signin_user(user)
    return {'result' : 'success', 'token' : token}


api.add_resource(SignUpAPI, '/api/v1/signup/', endpoint='signup')


##########################################
# Sign Out
##########################################
def signout_user(user):
  user.token = None
  user.put()


class SignOutAPI(Resource):

  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('Authorization', location='headers')
    super(SignOutAPI, self).__init__()

  # log this user out! ie. null user token
  def get(self):
    args = self.reqparse.parse_args()
    login_required(args)
    user = get_user_by_authorization_token(args)
    signout_user(user)
    return {'result' : 'success'}


api.add_resource(SignOutAPI, '/api/v1/signout/', endpoint='signout')


##########################################
# Account Info - Plaid
##########################################
def set_plaid_info_for_user(user, plaid_token, plaid_meta):
  user.plaid_token = plaid_token
  user.plaid_meta = plaid_meta
  user.put()

class PlaidAccountInfoAPI(Resource):
  """ use plaid to connect a user's account. Plaid will return a token
  for the account they have selected. We use that token to access
  their account information via the Plaid connect api """
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('Authorization', location='headers')
    self.reqparse.add_argument(
      'plaid_token', type = str, required = False)
    self.reqparse.add_argument(
      'plaid_meta', type = str, required = False)
    super(PlaidAccountInfoAPI, self).__init__()

  def get(self):
    args = self.reqparse.parse_args()
    user = get_user_by_authorization_token(args)

    url = 'https://tartan.plaid.com/auth/get'
    r = requests.post(url, data={'client_id': 'test_id', 'secret': 'test_secret', 'access_token': 'test', 'type': 'bofa'})
    logging.info(r.status_code)
    logging.info(r.reason)
    logging.info(r.text)

    #client = Client(client_id='test_id', secret='test_secret', access_token='test')
    #client.credentials.account_type='bofa'
    #accounts = json.loads(client.auth_get().content)
    #logging.info(accounts)

    return {
      'result' : 'success',
      'plaid_meta' : user.plaid_meta,
      'plaid_token' : user.plaid_token,
      'plaid_account_info' : r.text
    }
    """
    response = client.connect('bofa', {
        'username': 'plaid_test',
        'password': 'plaid_good'
    })

    if response.ok:
      content = json.loads(response.content)
      print content
      return content

    return {'result' : 'success'}
    """

  def post(self):
    args = self.reqparse.parse_args()
    user = get_user_by_authorization_token(args)
    logging.info(args)
    logging.info(args['plaid_token'])
    set_plaid_info_for_user(user, args['plaid_token'], args['plaid_meta'])
    return {'result' : 'success', 'plaid_meta' : user.plaid_meta, 'plaid_token' : user.plaid_token}


api.add_resource(PlaidAccountInfoAPI, '/api/v1/account_info/', endpoint='account_info')


##########################################
# Select an amount - Plaid / Our db
##########################################
class SelectAmountAPI(Resource):
  """ Allow the user to specify an amount that will be periodically debited from their account.
  Again, we use the plaid provided token and the plaid api to get account and routing number.
  Then we use a cron job to transfer the user specified amount from this account to the user-
  specified fund via Dwolla and the TD Ameritrade API."""
  def __init__(self):
    super(SelectAmountAPI, self).__init__()

  def get(self):
    return {'result' : 'success'}

  def post(self):
    return {'result' : 'success'}


api.add_resource(SelectAmountAPI, '/api/v1/select_amount/', endpoint='select_amount')


##########################################
# One Time Transfer - Funds to TD API
##########################################
class OneTimeDepositAPI(Resource):
  """ Allow the user to make a one time payment."""
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument(
    'account_id', type = Integer, required = True,
    help = 'The account to debit')
    self.reqparse.add_argument(
    'amount', type = Integer, required = True,
    help = 'The amount to transfer')

    super(OneTimeDepositAPI, self).__init__()

  def get(self):
    return {'result' : 'success'}

  def post(self):
    return {'result' : 'success'}


api.add_resource(OneTimeDepositAPI, '/api/v1/one_time_deposit/', endpoint='one_time_deposit')


@app.errorhandler(404)
def page_not_found(e):
  """Return a custom 404 error."""
  return "This is not the page you're looking for.", 404


@app.errorhandler(500)
def application_error(e):
  """Return a custom 500 error."""
  return 'Oops, our bad: {}'.format(e), 500
