(function() {
  var app = angular.module('FBReport', ['googlechart', 'ngTable']);

  app.controller('CheckTTFResultsController', ['$http', '$filter', 'ngTableParams', function($http, $filter, ngTableParams){
    var checkCtrl = this;
    this.results = [];
    this.dataLoaded = false;
    $http.get('/fontbakery-check-results.json').success(function(data){
      var resultMap = {'OK': 'success',
                       'WARNING': 'danger',
                       'ERROR': 'warning',
                       'HOTFIX': 'info'};

      var results_count = {
        "OK":  0,
        "WARNING": 0,
        "ERROR" : 0,
        "HOTFIX": 0
      };

      for (item in data){
        data[item].result_class = resultMap[data[item].result];
        results_count[data[item].result] ++;
      }

      checkCtrl.results = data;
      checkCtrl.dataLoaded = true;

      checkCtrl.testsTableParams = new ngTableParams({
            // show first page
            page: 1,
            // count per page
            count: data.length,
            // initial sorting
            sorting: {
                result_status: 'asc'
            }
        }, {
            // hide page counts control
            counts: [],
            // length of data
            total: data.length,
            getData: function($defer, params) {
                // use build-in angular filter
                var orderedData = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) :
                    data;
                params.total(orderedData.length);
                $defer.resolve(orderedData);
            }
        });


      var gdata = google.visualization.arrayToDataTable([
               ['Tests', '#'],
               ['OK', results_count["OK"]],
               ['WARNING', results_count["WARNING"]],
               ['ERROR', results_count["ERROR"]],
               ['HOTFIX', results_count["HOTFIX"]]
           ]),
           options = {
               title: "Check Results Stats",
               is3D: true,
               chartArea: {'width': '100%'},
               colors: ['#468847', '#3a87ad', '#b94a48', '#c09853']
           };
       checkCtrl.chart = {data: gdata, options: options, type: "PieChart", displayed: true};
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

google.load('visualization', '1', { packages: ['corechart'] });
