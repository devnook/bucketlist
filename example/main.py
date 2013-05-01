# -*- coding: utf-8 -*-
import sys
from secrets import SESSION_KEY

from webapp2 import WSGIApplication, Route
import handlers

# inject './lib' dir in the path so that we can simply do "import ndb"
# or whatever there's in the app lib dir.
if 'lib' not in sys.path:
    sys.path[0:0] = ['lib']

# webapp2 config
app_config = {
  'webapp2_extras.sessions': {
    'cookie_name': '_simpleauth_sess',
    'secret_key': SESSION_KEY
  },
  'webapp2_extras.auth': {
    'user_attributes': []
  }
}

# Map URLs to handlers
routes = [
  Route('/', handler='handlers.RootHandler'),

  Route('/login', handler='handlers.LoginHandler', name='login'),
  Route('/profile', handler='handlers.ProfileHandler', name='profile'),

  Route('/logout', handler='handlers.AuthHandler:logout', name='logout'),
  Route('/auth/<provider>',
    handler='handlers.AuthHandler:_simple_auth', name='auth_login'),
  Route('/auth/<provider>/callback',
    handler='handlers.AuthHandler:_auth_callback', name='auth_callback'),

  Route('/api/cities', handler='async.Cities', name='cities'),
  Route('/api/cities/<city_name>/activity', handler='async.Activity', name='activity'),
  Route('/api/activity/<activity_id>', handler='async.Activity', name='activity'),
  Route(r'/api/cities/<:\w+>/activity/<activity_id>/vote', handler='async.Vote', name='vote'),
  Route(r'/api/cities/<:\w+>/activity/<activity_id>/fav', handler='async.Fav', name='fav'),
  Route(r'/api/cities/<:\w+>/activity/<activity_id>/done', handler='async.Done', name='done'),
  #Route('/api/cities/<city_name>/activities', handler='async.Activities', name='activities'),
  Route('/api/user/<user_id>', handler='async.UserHandler', name='user'),

  Route(r'/city/<city_name>/activity', handler='async.Activity', name='activity'),
  Route(r'/city/<city_name>/activity', handler='async.Activity', name='activity'),
  Route(r'/city/<city_name>/activity/<activity_id>', handler='async.Activity', name='activity', handler_method="getItem"),
  Route(r'/city/<city_name>/activity/<activity_id>/vote', handler='async.Activity', name='vote', handler_method="vote"),
  Route(r'/city/<city_name>/activity/<activity_id>/fav', handler='async.Activity', name='fav', handler_method="fav"),
  Route(r'/city/<city_name>/activity/<activity_id>/done', handler='async.Activity', name='done', handler_method="done"),
]

app = WSGIApplication(routes, config=app_config, debug=True)
