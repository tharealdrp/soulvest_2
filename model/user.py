# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

import model
import model.base

class User(model.Base):
  name = ndb.StringProperty(required=False)
  username = ndb.StringProperty(required=False)
  email = ndb.StringProperty(default='')
  auth_ids = ndb.StringProperty(repeated=True)
  active = ndb.BooleanProperty(default=True)
  admin = ndb.BooleanProperty(default=False)
  permissions = ndb.StringProperty(repeated=True)
  verified = ndb.BooleanProperty(default=False)
  token = ndb.StringProperty(default='')
  password_hash = ndb.StringProperty(default='')
  plaid_token = ndb.StringProperty(default='')
  plaid_meta = ndb.StringProperty(default='')
