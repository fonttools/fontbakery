(function() {
  var app = angular.module('FBReport', []);
  app.controller('CheckTTFResultsController', ['$http', function($http){
    var checks = this;
    checks.results = [];
    checks.dataLoaded = false;
    $http.get('/fontbakery-check-results.json').success(function(data){
      var resultMap = {'OK': 'success',
                       'WARNING': 'danger',
                       'ERROR': 'warning',
                       'HOTFIX': 'info'};
      for (item in data){
        data[item].result_class = resultMap[data[item].result];
      }
      checks.results = data;
      checks.dataLoaded = true;
    });
  }]);

  // configure our app
/*  app.config(['$routeProvider', function($routeProvider) {
    // configure routes
    $routeProvider
        .when('/', {
            controller : 'testsController',
            title: 'test results',
            templateUrl : 'pages/tests.html',
            activetab: 'checks'
        })

        .when('/summary', {
//            controller : '?',
            title: 'Summary',
            templateUrl : 'pages/summary.html',
            activetab: 'summary'
        })

        .when('/about', {
            controller : 'aboutController',
            title: 'About',
            templateUrl : 'pages/about.html',
            activetab: 'about'
        });
  }]); */

})();
