// directive to handle class attr of navigation menu items (eg, set/rm "active")
// #TODO make navigation menu as a separate component
function isElementInViewport (el) {

    //special bonus for those using jQuery
    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /*or $(window).height() */
            rect.right <= (window.innerWidth || document.documentElement.clientWidth) /*or $(window).width() */
        );
}
angular.module('myApp').directive('navMenu', ['$location', function($location) {
    function activeLink(scope, element, attrs) {
        var links = element.find('a'),
            activeClass = attrs.navMenu || 'active',
            routePattern,
            link,
            url,
            currentLink,
            urlMap = {},
            i;
        if (!$location.$$html5) {
            routePattern = /^#[^/]*/;
        }

        for (i = 0; i < links.length; i++) {
            link = angular.element(links[i]);
            url = link.attr('href');

            if ($location.$$html5) {
                urlMap[url] = link;
            } else {
                urlMap[url.replace(routePattern, '')] = link;
            }
        }

        scope.$on('$routeChangeStart', function() {
            var pathLink = urlMap[$location.path()];
            if (pathLink) {
                if (currentLink) {
                    currentLink.parent('li').removeClass(activeClass);
                }
                currentLink = pathLink;
                currentLink.parent('li').addClass(activeClass);
            }
        });
    }
    return {
        link: activeLink
    }
}]);

angular.module('myApp').directive('insertGlyph', ['$compile', function($compile) {
    var getTemplate = function(is_missing) {
        return is_missing ? '<div style="display: none;"><span class="defaultCharacter">{{ glyph_decoded }}</span><span class="missing-glyph">X</span></div>' : '<div ng-style="{\'font-family\': font_regular.postScriptName, \'font-style\': font_regular.style}"><span class="defaultCharacter">{{ glyph_decoded }}</span><span>{{ glyph_decoded }}</span></div>';
    };
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var el = $compile(getTemplate(scope.is_missing))(scope);
            element.replaceWith(el);
        }
    };
}]);

angular.module('myApp').directive('getBuildInfo', ['$compile', '$window', '$rootScope', function($compile, $window, $rootScope) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var isResolved = 'buildIsResolved';
            var eventsListener;
            if (!scope.build.hasOwnProperty(isResolved)) {
                eventsListener = $rootScope.$watch('repo_selected', function () {
                    if (isElementInViewport(element) && !scope.build.hasOwnProperty(isResolved)) {
                        scope.build.getBuildInfoCallback(scope);
                    }
                }, true);
            }
            if (scope.build.hasOwnProperty(isResolved)) {
                if (angular.isFunction(eventsListener)) {
                    eventsListener(); //de-register
                }
                if (scope.build[isResolved]) {
                    $rootScope.itemsQueue.build.unset(scope.build);
                }
            }
        }
    };
}]);

angular.module('myApp').directive('getTestsInfo', ['$compile', '$window', '$rootScope', function($compile, $window, $rootScope) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var isResolved = 'testsIsResolved';
            var eventsListener;
            if (!scope.build.hasOwnProperty(isResolved)) {
                eventsListener = $rootScope.$watch('repo_selected', function () {
                    if (isElementInViewport(element) && !scope.build.hasOwnProperty(isResolved)) {
                        scope.build.getTestsInfoCallback(scope);
                    }
                });
            }
            if (scope.build.hasOwnProperty(isResolved)) {
                if (angular.isFunction(eventsListener)) {
                    eventsListener(); //de-register
                }
                if (scope.build[isResolved]) {
                    $rootScope.itemsQueue.tests.unset(scope.build);
                }
            }
        }
    };
}]);


angular.module('myApp').directive('loadingContainer', function () {
    return {
        restrict: 'A',
        scope: false,
        link: function(scope, element, attrs) {
            var loadingLayer = angular.element('<div class="loading"></div>');
            element.append(loadingLayer);
            element.addClass('loading-container');
            scope.$watch(attrs.loadingContainer, function(value) {
                loadingLayer.toggleClass('ng-hide', !value);
            });
        }
    };
});

angular.module('myApp').directive('applySorting', ['$timeout', function($timeout) {
    return function(scope, element, attrs) {
        var resort = true,
            callback = function(table){},
            config = {};
        if (attrs.applySorting) {
            if (angular.isFunction(attrs.applySorting)) {
                config = attrs.applySorting(element);
            }
            callback = function(table){
                element.tablesorter(config);
            };
        }
        //#TODO what event can be considered as event
        // of finished rendering & updating of all cells?
        $timeout(function() {
            element.trigger("updateAll", [ resort, callback ]);
        }, 5000);
    };
}]);
