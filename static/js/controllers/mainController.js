// This controller is used outside ng-view
angular.module('myApp').controller('mainController', ['$scope', '$rootScope', '$http', '$window', '$routeParams', '$route', '$location', '$filter', '$localStorage', '$sessionStorage', 'appApi', 'alertsFactory', 'appConfig', 'Mixins', 'githubService', function($scope, $rootScope, $http, $window, $routeParams, $route, $location, $filter, $localStorage, $sessionStorage, appApi, alertsFactory, appConfig, Mixins, githubService) {
    $scope.$storage = $sessionStorage;

    githubService.initializeOAuth();

    // current controller is on top level, so all http
    // errors should come through it
    $scope.alerts = alertsFactory;
    $scope.mixins = Mixins;
    $scope.config = appConfig;
    $scope.statusMap = appConfig.statusMap;
    $scope.resultMap = appConfig.resultMap;
    $scope.pangram = appConfig.pangram;

    $scope.repos_list = null;
    $scope.app_info = null;
    $scope.repo_info = null;
    $scope.build_info = null;
    $rootScope.metadata = null;

    $scope.repo_is_valid = false;
    $scope.repo_current = null;
    $rootScope.repo_selected = {name: null};

    $scope.initDone = function() {
        return $rootScope.metadata != null &&
            $scope.repos_list != null &&
            $scope.app_info != null &&
            $scope.repo_info != null &&
            $scope.build_info != null &&
            $scope.repo_current != null
    };

    $scope.isNormalFlow = function() {
        if ($scope.$storage.OAuth_passed && $scope.isRoot()) {return true;}
        if ($scope.initDone() && $scope.$storage.OAuth_passed) {return true;}
        if ($scope.initDone()) {
            if ($scope.app_info.build_passed || !$scope.repo_is_valid) {return true}
        }
        return false
    };

    $scope.filterWithQuicksilverRanking = function(val1, val2) {
        //#TODO make score configurable?
        // Add some control in search box
        // to use either strict search (score > 0.8),
        // flexible search (score > 0.3) ?
        try {
            if (!val2) {
                return true
            }
            return val1.score(val2) > 0.3;
        }
        catch (e) {return false;}
    };

    $scope.filterReposList = function(criteria) {
        return function(item) {
            return $scope.filterWithQuicksilverRanking(item.submodule, criteria);
        };
    };

    $scope.isRoot = function() {
        return $location.path() == '/';
    };

    $scope.isAboutPage = function() {
        return $location.path() == '/about';
    };

    $scope.onRepoSelect = function ($item, $model, $label) {
        //#TODO refactor this horror!!!
        var loc_path = $location.path(),
            hash_tag= '#';
        if (loc_path == '/') {
            $window.location.href = [hash_tag, 'librefonts', $item.submodule].join('/');
        } else {
            var parts = loc_path.split('/');
            parts[0] = hash_tag;
            parts[1] = 'librefonts';
            parts[2] = $item.submodule;
            $window.location.href = parts.join('/');
        }
//        $route.reload();
        $window.location.reload();
        if ($rootScope.metadata) {
            $rootScope.repo_selected.name = $rootScope.metadata.name;
        }
    };

    $scope.getMainFont = function() {
        var filtered = $rootScope.metadata.fonts.filter(function(font) {
            return font.style == 'normal' && font.weight == 400 ;
        });
        if (filtered.length > 0) {
            $rootScope.font_regular = filtered[0]
        } else {
            $rootScope.font_regular = $rootScope.metadata.fonts[0];
        }
        return $rootScope.font_regular;
    };

    $scope.getRepoTravisLink = function() {
        return ['http://travis-ci.org', $scope.repo_current.owner, $scope.repo_current.name].join('/');
    };

    $scope.getRepoTravisImageLink = function() {
        return ['https://travis-ci.org',  $scope.repo_current.owner, $scope.repo_current.name + '.svg'].join('/');
    };

    /* This parses a text_format Protocol Buffer
       message containing Font Family metadata */
    function parse_FamilyProto_Message(data) {
        var message = {};
        message.fonts = Array();
        var font_message = null;
        var lines = data.split('\n');
        for (l in lines) {
            var line = lines[l];
            try {
                var pair = line.split(':');
                var key = pair[0].strip();
                var value;
                if (pair[1].indexOf('"') >= 0) {
                    value = pair[1].split('"')[1];
                } else {
                    value = int(pair[1]);
                }

                if (font_message == null){
                    message[key] = value;
                } else {
                    font_message[key] = value;
                }
            }
            catch (e) {
                if (line.indexOf('font {') >= 0) {
                    font_message = {};
                }

                if (line.indexOf('}') >= 0) {
                    message.fonts.push(font_message);
                    font_message = null;
                }
            }
        }

        return message;
    }

    $scope.mainInit = function() {
        appApi.getRepos().then(function(dataResponse) {
            $scope.repos_list = dataResponse.data;
            if ($scope.repo_current.name === null ||
                $scope.repo_current.name === undefined ||
                $scope.repo_current.owner === null ||
                $scope.repo_current.owner === undefined) {
                $scope.repo_is_valid = false;
            }
            else {
                appApi.checkRepo($scope.repo_current).then(
                    function(dataResponse) {
                        $scope.repo_is_valid = true;
                        appApi.setActiveRepo($scope.repo_current);

                        appApi.getAppInfo().then(function(dataResponse) {
                            $scope.app_info = dataResponse.data;
                        });

                        appApi.getRepoInfo().then(function(dataResponse) {
                            $scope.repo_info = dataResponse.data;
                        });

                        appApi.getRepoBuildInfo().then(function(dataResponse) {
                            $scope.build_info = dataResponse.data;
                        });

                        appApi.getMetadataNew().then(
                            function(dataResponse) {
                                $rootScope.metadata = parse_FamilyProto_Message(dataResponse.data);
                                $rootScope.repo_selected.name = $rootScope.metadata.name;
                                $scope.getMainFont();
                            },
                            function(error) {
                                appApi.getMetadata().then(function(dataResponse) {
                                    $rootScope.metadata = parse_FamilyProto_Message(dataResponse.data);
                                    $rootScope.repo_selected.name = $rootScope.metadata.name;
                                    $scope.getMainFont();
                                });
                            });
                    },
                    function(error) {
                        $scope.repo_is_valid = false;
                        if ($location.path() != '/') {
                            $window.location.href = '/';
                        }
                    });
            }
        });
    };

    $scope.authenticateWithOAuth = function() {
        githubService.connectOAuth().then(function() {
            if ($scope.$storage.OAuth_passed) {
                $scope.mainInit();
            } else {
                $scope.alerts.addAlert($scope.$storage.OAuth_error)
            }
        })
    };

    $scope.$on('$routeChangeSuccess', function() {
        console.log("$location.path(): ", $location.path())
        $scope.repo_current = {
            owner: $routeParams.repo_owner,
            name: $routeParams.repo_name
        };

        if ($scope.$storage.OAuth_passed) {
            $scope.mainInit();
        } else {
            if ($scope.$storage.OAuth_redirect_done) {
                $scope.authenticateWithOAuth();
            }

        }
    });

    $scope.$watch('repo_current', function(newValue, oldValue) {
        if (newValue && oldValue){
            var filtered = Object.keys(newValue).filter(function(key) {
                return typeof newValue[key] === 'undefined';
            }).concat(Object.keys(oldValue).filter(function(key) {
                    return typeof oldValue[key] === 'undefined';
                }));
            if (newValue != oldValue && filtered.length == 0) {
                $window.location.reload();
            }
        }
    }, true)
}]);
