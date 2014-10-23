(function(){

	angular.module('RouteStylesApp', ['ngRoute'])

		.constant('Routes', {
			route1: '/route-one',
			route2: '/route-two',
			route3: '/route-three'
		})

		.config(['$routeProvider', 'Routes', function($routeProvider, Routes){

			$routeProvider
				.when(Routes.route1, {
					controller: 'Route1Ctrl',
					templateUrl: 'partials/partial1.html',
                    css: 'partial-css/partial1.css'
				})
				.when(Routes.route2, {
					controller: 'Route2Ctrl',
					templateUrl: 'partials/partial2.html',
                    css: 'partial-css/partial2.css'
				})
				.when(Routes.route3, {
					controller: 'Route3Ctrl',
					templateUrl: 'partials/partial3.html',
                    css: ['partial-css/partial3a.css','partial-css/partial3b.css']
				})
                .otherwise({
                    redirectTo: Routes.route1
                });

		}])

		.controller('RouteStylesCtrl', ['$scope', 'Routes', function($scope, Routes){
			$scope.pageContent = '';
			$scope.routes = Routes;
		}])

		.controller('Route1Ctrl', ['$scope', function($scope){
			$scope.pageContent = 'This is the first route';
		}])

		.controller('Route2Ctrl', ['$scope', function($scope){
			$scope.pageContent = 'This is the second route';
		}])

		.controller('Route3Ctrl', ['$scope', function($scope){
			$scope.pageContent = 'This is the third route';
		}])

		.directive('head', ['$rootScope','$compile',
			function($rootScope, $compile){
				return {
					restrict: 'E',
					link: function(scope, elem){
						var html = '<link rel="stylesheet" ng-repeat="(routeCtrl, cssUrl) in routeStyles" ng-href="{{cssUrl}}" >';
						elem.append($compile(html)(scope));

                        scope.routeStyles = {};

						$rootScope.$on('$routeChangeStart', function (e, next, current) {

							if(current && current.$$route && current.$$route.css){
								if(!Array.isArray(current.$$route.css)){
									current.$$route.css = [current.$$route.css];
								}
								angular.forEach(current.$$route.css, function(sheet){
									delete scope.routeStyles[sheet];
								});
							}

							if(next && next.$$route && next.$$route.css){
								if(!Array.isArray(next.$$route.css)){
									next.$$route.css = [next.$$route.css];
								}
								angular.forEach(next.$$route.css, function(sheet){
									scope.routeStyles[sheet] = sheet;
								});
							}

						});

					}
				};
			}
		]);




})();