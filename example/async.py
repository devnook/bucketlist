import datetime
import logging
import json
import random

simplejson = json

from google.appengine.api import channel
from google.appengine.api import users

from google.appengine.ext import db
from google.appengine.ext import ndb

from webapp2_extras.appengine.auth.models import User



from models import models
import handlers

def user_required(handler):
  """
    Decorator for checking if there's a user associated with the current session.
    Will also fail if there's no session present.
  """
  def check_login(self, *args, **kwargs):
    if not self.auth.get_user_by_session():
      # If handler has no login_url specified invoke a 403 error
      try:
        self.redirect(self.uri_for('login'), abort=True)
      except (AttributeError, KeyError), e:
        self.abort(403)
    else:
      return handler(self, *args, **kwargs)
  return check_login


class Error(Exception):
  """Base error class"""

"""
class GetStateHandler(abstract_handler.AbstractHandler):

  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return


    message = 'hello'

    client_id = user.user_id() + 'aaa'
    channel.send_message(client_id, message)


class OpenChannel(abstract_handler.AbstractHandler):

  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return


    client_id = user.nickname()
    token = channel.create_channel(client_id)
    response = {
      'token': token,
      'me': user.user_id(),
      'client_id': client_id
    }

    message = 'Connected to server as %s...' % client_id
    channel.send_message(client_id, message)

    self.RenderJson(response)
"""


class Tag(handlers.BaseRequestHandler):

  def get(self):
    query = models.Tag.query()
    tags = [tag.name for tag in tags]
    self.RenderJson(tags)


class Cities(handlers.BaseRequestHandler):

  def get(self):
    #city = models.City(name='Warsaw')
    #city.put()
    #category = models.Category(name='Sport')
    #category.put()
    #tag = models.Tag(name='food')
    #tag.put()
    query = models.City.query()
    cities = [city.to_dict() for city in  query]
    response = {'cities': cities}
    self.RenderJson(response)

  def post(self):
    city_name = self.request.get('city')
    existing_city = models.City.query(models.City.name == city_name).get()
    logging.info(city_name)
    logging.info(existing_city)
    if not existing_city:
      city = models.City(name=city_name)
      city.put()
      response = {'city': city.to_dict()}
    else:
      response = {'error': 'City already exists.'}
    self.RenderJson(response)


class Activity(handlers.BaseRequestHandler):

  def get(self, city_name, activity_id):
    activity = models.Activity.get_by_id(int(activity_id))
    user_id = self.current_user.get_id() if self.current_user else None
    response = activity.to_dict(user_id=user_id)
    self.RenderJson(response)

  @user_required
  def edit(self, city_name, activity_id):
    request = simplejson.loads(self.request.body)
    city = models.City.query(models.City.name == city_name).get()
    category = models.Category.query(models.Category.name == request.get('category')['name']).get()
    tags = None
    if request.get('tags'):
      tags = [models.Tag.query(models.Tag.name == tag).get().key for tag in request.get('tags')]
    activity = models.Activity.get_by_id(int(activity_id))
    activity.name = request['name']
    activity.description = request['description']
    activity.city = city.key
    activity.creator = self.current_user.key
    if category:
      activity.category = category.key
    if tags:
      activity.tags = tags
    logging.info(activity)
    activity.put()
    self.RenderJson(activity.to_dict())

  @user_required
  def post(self, city_name):
    request = simplejson.loads(self.request.body)
    logging.info(request)
    logging.info(self.current_user)
    city = models.City.query(models.City.name == city_name).get()
    category = models.Category.query(models.Category.name == request.get('category')).get()
    tags = None
    if request.get('tags'):
      tags = [models.Tag.query(models.Tag.name == tag).get().key for tag in request.get('tags')]
    new_activity = models.Activity(name=request['name'],
                                   description=request['description'],
                                   city=city.key,
                                   creator=self.current_user.key)
    if category:
      new_activity.category = category.key
    #if tags:
    #  new_activity.tags = category.key
    logging.info(new_activity)
    new_activity.put()
    self.RenderJson(new_activity.to_dict())

  @user_required
  def vote(self, city_name, activity_id):
    activity = models.Activity.get_by_id(int(activity_id))
    vote = int(self.request.get('vote'))
    # check for deduping
    user_id = self.current_user.get_id()

    if vote > 0:
      if user_id in activity.downvoters:
        activity.downvoters.remove(user_id)
      elif user_id not in activity.upvoters:
        activity.upvoters.append(self.current_user.get_id())
    elif vote < 0:
      if user_id in activity.upvoters:
        activity.upvoters.remove(user_id)
      elif user_id not in activity.downvoters:
        activity.downvoters.append(self.current_user.get_id())
    activity.put()
    response = activity.to_dict(user_id=self.current_user.get_id())
    self.RenderJson(response)

  @user_required
  def fav(self, city_name, activity_id):
    activity = models.Activity.get_by_id(int(activity_id))
    add_to_fav = self.request.get('add_to_fav') == 'true'
    logging.info(add_to_fav)
    # check for deduping
    user_id = self.current_user.get_id()

    if add_to_fav:
      if user_id not in activity.followers:
        activity.followers.append(user_id)
    else:
      if user_id in activity.followers:
        activity.followers.remove(user_id)

    activity.put()
    self.RenderJson(activity.to_dict(user_id=self.current_user.get_id()))

  @user_required
  def done(self, city_name, activity_id):
    activity = models.Activity.get_by_id(int(activity_id))
    add_to_done = self.request.get('add_to_done') == 'true'
    # check for deduping
    user_id = self.current_user.get_id()

    if add_to_done and user_id not in activity.doers:
        activity.doers.append(user_id)
    elif not add_to_done and user_id in activity.doers:
        activity.doers.remove(user_id)

    activity.put()
    self.RenderJson(activity.to_dict(user_id=self.current_user.get_id()))

  def list(self, city_name):
    logging.info('listdddddddddddddddddd')
    city = models.City.query(models.City.name == city_name).get()
    activities_query = models.Activity.query(models.Activity.city==city.key)
    activities = [activity.to_dict(user_id=self.current_user.get_id()) for activity in activities_query]
    logging.info(city)
    logging.info(activities)
    self.RenderJson(activities)


class UserHandler(handlers.BaseRequestHandler):

  def get(self, user_id):
    if user_id == 'me':
      user = self.current_user
    else:
      user = self.auth.store.user_model.get_by_id(int(user_id))
    if user:

      activities_query = models.Activity.query(ndb.OR(
        models.Activity.creator==user.key,
        models.Activity.upvoters == user.get_id(),
        models.Activity.downvoters == user.get_id(),
        models.Activity.followers == user.get_id(),
        models.Activity.doers == user.get_id()
        )
      )
      activities = [activity.to_dict(user_id=user.get_id()) for activity in activities_query]

      response = {'user': {
        'id': user.get_id(),
        'avatar_url': user.avatar_url,
        'name': user.name,
        'activities': activities
      }}
    else:
      response = {'error': 'User not found'}
    self.RenderJson(response)


class Category(handlers.BaseRequestHandler):

  def get(self):
    query = models.Category.query()
    categories = [category.to_dict() for category in  query]
    self.RenderJson(categories)

  def post(self):
    request = simplejson.loads(self.request.body)
    category = models.Category(name=request['name'])
    category.put()
    self.RenderJson(category)

class Tag(handlers.BaseRequestHandler):

  def get(self):
    query = models.Tag.query()
    tags = [tag.to_dict() for tag in  query]
    self.RenderJson(tags)

