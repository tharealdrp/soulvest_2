# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

class Base(ndb.Model):
  created = ndb.DateTimeProperty(auto_now_add=True)
  modified = ndb.DateTimeProperty(auto_now=True)
  version = ndb.IntegerProperty(default=1)
