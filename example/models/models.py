import json
simplejson = json

from google.appengine.ext import db

from webapp2_extras.appengine.auth.models import User

from google.appengine.api import users 
from google.appengine.ext import ndb



import datetime
import time

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def to_dict(model):
  output = {}

  for key, prop in model.properties().iteritems():
    value = getattr(model, key)

    if value is None or isinstance(value, SIMPLE_TYPES):
      output[key] = value
    elif isinstance(value, datetime.date):
      # Convert date/datetime to ms-since-epoch ("new Date()").
      ms = time.mktime(value.utctimetuple())
      ms += getattr(value, 'microseconds', 0) / 1000
      output[key] = int(ms)
    elif isinstance(value, db.GeoPt):
      output[key] = {'lat': value.lat, 'lon': value.lon}
    elif isinstance(value, db.Model):
      output[key] = to_dict(value)
    else:
      raise ValueError('cannot encode ' + repr(prop))

  return output


class City(ndb.Model):
  name = ndb.StringProperty(required=True)


class Activity(ndb.Model):
  name = ndb.StringProperty(required=True)
  city = ndb.KeyProperty(kind=City)
  creator = ndb.KeyProperty(kind=User)
  upvoters = ndb.IntegerProperty(repeated=True)
  downvoters = ndb.IntegerProperty(repeated=True)

  def to_dict(self, user_id=None):

    result = {
      'id': self.key.id(),
      'name': self.name,
      'city': self.city.get().to_dict(),
      'upvotes': len(self.upvoters),
      'downvotes': len(self.downvoters),
      'is_upvoted': user_id in self.upvoters,
      'is_downvoted': user_id in self.downvoters,
    }
    if self.creator:
      creator = self.creator.get()
      result['creator'] = {
        'name': creator.name,
        'avatar_url': creator.avatar_url,
        'id': creator.get_id()
      }
    return result





  
 