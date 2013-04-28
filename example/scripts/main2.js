
var CitiesApp = angular.module('CitiesApp', ['ngSanitize', 'localization']);

CitiesApp
  .config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/connect', {templateUrl: 'partials/connect.html', controller: CitiesController}).
        when('/home', {templateUrl: 'partials/home.html', controller: CitiesController}).
        when('/cities/:cityName', {templateUrl: 'partials/city.html',  controller: CityController}).
        when('/activity/:activityId', {templateUrl: 'partials/activity.html',  controller: ActivityController}).
        when('/user/:userId', {templateUrl: 'partials/user.html',  controller: UserController}).
        otherwise({redirectTo: '/home'});
  }])
  .config(
    function($interpolateProvider) {
      $interpolateProvider.startSymbol('{*');
      $interpolateProvider.endSymbol('*}');
  });


  // define a value
CitiesApp.value('myThing', 'weee');

// use it in a service

CitiesApp.factory('myService', ['myThing', function(myThing){

   var aVar = 'aaa';
   return {
       whatsMyThing: function() {
          return 'myThing'; //weee
       },
       setMyThing: function() {
          return myThing; //weee
       }
    }
}]);


function UserController ($scope, $http, $routeParams) {
  var sc = $scope;
  sc.userId = $routeParams.userId;
  sc.user = null;

  $http.get('/api/user/' + sc.userId).success(function(response) {
    console.log(response)
    if (response.user) {
      sc.user = response.user;
    }
  });

  sc.isUpvoted = function(activity) {
    return activity.is_upvoted == 'true';
  }

};


function LocaleController ($scope, $rootScope, $locale, localize, myThing, myService) {
  var sc = $scope;
  sc.locales = [
    {'id': 'en-US', 'name': 'English'},
    {'id': 'pl-pl', 'name': 'Polski'}
  ];
  sc.localeId = $locale.id;
  localize.setLanguage(sc.localeId);
  sc.selectLocale = function() {
    localize.setLanguage(sc.localeId);
  }
};

function GeoController ($scope, $http) {
  var sc = $scope;
  sc.test = '';
  var apiUrl = 'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&latlng=';
  /*
  navigator.geolocation.getCurrentPosition(function (position) {
    console.log(position);
    var url = apiUrl + position.coords.latitude + ',' + position.coords.longitude;
    console.log(url);
    $http.get(url).success(function(data) {
      console.log(data);
    })
  });
  */
};


function ActivityController ($scope, $routeParams, $http, $locale) {
  var sc = $scope;

  $http.get('/api/activity/' + $routeParams.activityId).success(function(data) {
    console.log(data);
    sc.activity = data['activity'];
  });


};


function CitiesController ($scope, $rootScope, $location, $http, $locale) {
  var sc = $scope;

  $http.get('/api/cities').success(function(data) {
    console.log(data);
    sc.cities = data['cities'];
  });

  sc.isCurrentRoute = function(route) {
    return route === $location.path().substring(1);
  };


  sc.addCity = function(city) {
    $http({
        method: 'POST',
        url: '/api/cities',
        data: $.param({'city': city}),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    }).success(function(response) {
      console.log(response);
      sc.cities.push(response.city);

    });

  };

  sc.selectCity = function(city) {
    $location.path('/cities/' + city);
  }
};


function CityController ($scope, $routeParams, $http) {
  var sc = $scope;

  sc.city = $routeParams.cityName;
  sc.activities = [];

  $http.get('/api/cities/' + sc.city + '/activities').success(function(response) {
    console.log(response);
    sc.activities = response.activities;
  });

  sc.addActivity = function() {
    data = {
      'city': sc.city,
      'activity': sc.newActivity,
      'activity_description': sc.newActivityDesc,
    }
    $http({
        method: 'POST',
        url: '/api/cities/' + sc.city + '/activity',
        data: $.param(data),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    }).success(function(response) {
      console.log(response);
      sc.activities.push(response.activity);

    });

  };

  sc.vote = function(activityId, up) {
    console.log(activityId);
    var vote = up ? 1 : -1;
    data = {
      'vote': vote
    }
    $http({
        method: 'POST',
        url: '/api/cities/' + sc.city + '/activity/' + activityId + '/vote',
        data: $.param(data),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    }).success(function(response) {
      console.log(response);
      for (var i = 0, activity; activity = sc.activities[i]; i++) {
        if (activity.id === response.activity.id) {
          sc.activities[i] = response.activity;
        }
      }
    });
  };

  sc.fav = function(activityId, addToFav) {
    console.log(activityId);
    data = {
      'add_to_fav': addToFav
    };
    $http({
        method: 'POST',
        url: '/api/cities/' + sc.city + '/activity/' + activityId + '/fav',
        data: $.param(data),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    }).success(function(response) {
      console.log(response);
      for (var i = 0, activity; activity = sc.activities[i]; i++) {
        if (activity.id === response.activity.id) {
          sc.activities[i] = response.activity;
        }
      }
    });
  }

  sc.done = function(activityId, addToDone) {
    console.log(activityId);
    data = {
      'add_to_done': addToDone
    };
    $http({
        method: 'POST',
        url: '/api/cities/' + sc.city + '/activity/' + activityId + '/done',
        data: $.param(data),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    }).success(function(response) {
      console.log(response);
      for (var i = 0, activity; activity = sc.activities[i]; i++) {
        if (activity.id === response.activity.id) {
          sc.activities[i] = response.activity;
        }
      }
    });
  }
};


var cities = {};

cities.helper = (function() {
  var BASE_API_PATH = 'plus/v1/';

  return {
    /**
     * Hides the sign in button and starts the post-authorization operations.
     *
     * @param {Object} authResult An Object which contains the access token and
     *   other authentication information.
     */
    onSignInCallback: function(authResult) {
      gapi.client.load('plus','v1', function(){
        console.log(onSignInCallback);
        console.log('authResult', authResult);
        cities.helper.profile();
      });
    },

    /**
     * Calls the OAuth2 endpoint to disconnect the app for the user.
     */
    disconnect: function() {
      // Revoke the access token.
      $.ajax({
        type: 'GET',
        url: 'https://accounts.google.com/o/oauth2/revoke?token=' +
            gapi.auth.getToken().access_token,
        async: false,
        contentType: 'application/json',
        dataType: 'jsonp',
        success: function(result) {
          console.log('revoke response: ' + result);
          $('#authOps').hide();
          $('#profile').empty();
          $('#visiblePeople').empty();
          $('#authResult').empty();
          $('#gConnect').show();
        },
        error: function(e) {
          console.log(e);
        }
      });
    },

    /**
     * Gets and renders the list of people visible to this app.
     */
    people: function() {
      var request = gapi.client.plus.people.list({
        'userId': 'me',
        'collection': 'visible'
      });
      request.execute(function(people) {
        $('#visiblePeople').empty();
        $('#visiblePeople').append('Number of people visible to this app: ' +
            people.totalItems + '<br/>');
        for (var personIndex in people.items) {
          person = people.items[personIndex];
          $('#visiblePeople').append('<img src="' + person.image.url + '">');
        }
      });
    },

    /**
     * Gets and renders the currently signed in user's profile data.
     */
    profile: function(){
      var request = gapi.client.plus.people.get( {'userId' : 'me'} );
      request.execute( function(profile) {
        console.log(profile);

        $.post('/user/google:' + profile.id, function(response) {
          console.log(response);
        });
        $('#profile').empty();
        if (profile.error) {
          $('#profile').append(profile.error);
          return;
        }
        $('#profile').append(
            $('<p><img src=\"' + profile.image.url + '\"></p>'));
        $('#profile').append(
            $('<p>Hello ' + profile.displayName + '!'));

      });
    }
  };
})();


