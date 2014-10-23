/**
 * Created by Zack Boman on 1/31/14.
 * http://www.zackboman.com or tennisgent@gmail.com
 *
 * Patched by Andriy Hrytskiv
 */

(function(){

    var mod = angular.module('routeStyles', ['ngRoute']);

    mod.directive('head', ['$rootScope','$compile',
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
                                if (angular.isFunction(current.$$route.css)) {
                                    current.$$route.css = current.$$route.css(current.params);
                                } else {
                                    current.$$route.css = [current.$$route.css];
                                }
                            }
                            angular.forEach(current.$$route.css, function(sheet){
                                delete scope.routeStyles[sheet];
                            });
                        }
                        if(next && next.$$route && next.$$route.css){
                            if(!Array.isArray(next.$$route.css)){
                                if (angular.isFunction(next.$$route.css)) {
                                    next.$$route.css = next.$$route.css(next.params);
                                } else {
                                    next.$$route.css = [next.$$route.css];
                                }
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
