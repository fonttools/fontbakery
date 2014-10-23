angular.module('myApp').controller('reposController', ['$scope', '$rootScope', '$routeParams', '$filter', '$q', '$http', '$window', '$queue', 'reposApi', 'ngTableParams', function($scope, $rootScope, $routeParams, $filter, $q, $http, $window, $queue, reposApi, ngTableParams) {
    $scope.dataLoaded = false;
    $scope.OAuth_passed = false;
    $scope.reqCounter = 0;
    $scope.filteredTreeData = 0;
    $scope.itemsLoaded = false;
    $scope.tableInitialized = false;

    var data = [],
        build_date_errors = [],
        tests_passing_errors = [];

    $scope.getItemsLoaded = function() {
        // there are 2 additional requests
        // per row - 1st for build date, 2nd - for tests results
        var current = parseFloat($scope.reqCounter/2);
        var total = $scope.filteredTreeData.length;
        $scope.itemsLoaded = current >= total-1 ? true:false;
        return parseInt(current)+'/'+parseInt(total);
    };

    var getBuildCallback = function(item) {
            if (!item.hasOwnProperty('buildIsResolved')) {
                item.getBuildInfoCallback({'build': item})
            }
        },
        getTestsInfoCallback = function(item) {
            if (!item.hasOwnProperty('testsIsResolved')) {
                item.getTestsInfoCallback({'build': item})
            }
        },
        options = {
            //delay 200ms seconds between processing items
            delay: 200,
            paused: true
            //complete: function() { console.log('queue is empty!'); }
        };

    $rootScope.itemsQueue = {
        build: $queue.queue(getBuildCallback, options),
        tests: $queue.queue(getTestsInfoCallback, options)
    };

    var getBuildInfo = function(scope) {
        $http.get('https://api.travis-ci.org/repos/fontdirectory/' + scope.build.repoName, {headers: { 'Accept': 'application/vnd.travis-ci.2+json' }, nointercept: true}).then(function(dataResponse) {
            //dataResponse.data.repo has attrs
            // description: null
            // github_language: null
            // id: 2678960
            // last_build_duration: 598
            // last_build_finished_at: "2014-10-06T13:00:19Z"
            // last_build_id: 37177838
            // last_build_language: null
            // last_build_number: "11"
            // last_build_started_at: "2014-10-06T12:50:21Z"
            // last_build_state: "passed"
            // slug: "fontdirectory/arimo"
            scope.build['buildDateOrig'] = dataResponse.data.repo.last_build_finished_at;
            scope.build['buildStatus'] = dataResponse.data.repo.last_build_state;
            scope.build['buildIsResolved'] = true;
            $scope.reqCounter++;
        }, function(error) {
            $scope.reqCounter++;
            build_date_errors.push(error.status + ' - ' + error.statusText + ': ' + error.config.url);
            scope.build['buildDateOrig'] = null;
            scope.build['buildStatus'] = null;
            scope.build['buildIsResolved'] = false;
        });
    };

    var getTestsInfo = function(scope) {
        $http.get('https://rawgit.com/fontdirectory/' + scope.build.repoName + '/gh-pages/summary.tests.json', {nointercept: true}).then(function(dataResponse) {
            var tests_data = dataResponse.data,
                totalTests = 0,
                successTests = 0,
                failureTests = 0,
                fixedTests = 0,
                errorTests = 0;
            $scope.reqCounter++;
            for (d in tests_data) {
                totalTests += tests_data[d].success + tests_data[d].error + tests_data[d].failure;
                successTests += tests_data[d].success;
                failureTests += tests_data[d].failure;
                errorTests += tests_data[d].error;
                fixedTests += tests_data[d].fixed;
            }
            scope.build['totalTests'] = totalTests;
            scope.build['successTests'] = successTests;
            scope.build['passingTestsPercentage'] = Math.round((successTests / totalTests) * 100);

            scope.build['failureTests'] = failureTests;
            scope.build['failureTestsPercentage'] = Math.round((failureTests / totalTests) * 100);

            scope.build['fixedTests'] = fixedTests;
            scope.build['fixedTestsPercentage'] = Math.round((fixedTests / totalTests) * 100);

            scope.build['errorTests'] = errorTests;
            scope.build['errorTestsPercentage'] = Math.round((errorTests / totalTests) * 100);

            scope.build['testsIsResolved'] = true;
        }, function(error) {
            $scope.reqCounter++;
            tests_passing_errors.push(error.status + ' - ' + error.statusText + ': ' + error.config.url);
            scope.build['totalTests'] = null;
            scope.build['successTests'] = null;
            scope.build['passingTestsPercentage'] = null;

            scope.build['failureTests'] = null;
            scope.build['failureTestsPercentage'] = null;

            scope.build['fixedTests'] = null;
            scope.build['fixedTestsPercentage'] = null;

            scope.build['errorTests'] = null;
            scope.build['errorTestsPercentage'] = null;

            scope.build['noTestsInfo'] = {status: error.status + ' - ' + error.statusText, url: error.config.url};
            scope.build['testsIsResolved'] = false;
        });
    };

    $scope.init = function() {
        reposApi.getCollection($scope.$storage.OAuth_result['access_token']).then(function(dataResponse) {
            $scope.filteredTreeData = dataResponse.data.tree.filter(function(item) {
                return "160000" == item.mode && "commit" == item.type && item.path.split('/')[1] != 'fontbakery';
            });

            $scope.buildsTableParams = new ngTableParams({
                // show first page
                page: 1,
                // count per page
                count: $scope.filteredTreeData.length,
                // initial sorting
                sorting: {
                    repoPath: 'asc'
                }
            }, {
                // hide page counts control
                counts: [],
                // length of data
                total: $scope.filteredTreeData.length,
                getData: function($defer, params) {
                    if ($scope.filteredTreeData.length != data.length) {
                        angular.forEach($scope.filteredTreeData, function(item, index) {
                            var info = {};

                            var path = item.path.split('/')[1];

                            info['repoPath'] = item.path;
                            info['repoName'] = path;
                            info['repoLink'] = 'https://github.com/fontdirectory/' + path;
                            info['travisLink'] = 'http://travis-ci.org/fontdirectory/' + path;
                            info['travisImg'] = 'https://travis-ci.org/fontdirectory/' + path + '.svg';
                            info['reportLink'] = 'https://fontdirectory.github.io/' + path;
                            info['getBuildInfoCallback'] = getBuildInfo;
                            info['getTestsInfoCallback'] = getTestsInfo;
                            data.push(info);
                            $rootScope.itemsQueue.build.add(info);
                            $rootScope.itemsQueue.tests.add(info);
                        });
                    }
                    var filteredData = $filter('filter')(data, $rootScope.repo_selected.name, function(val1, val2) {
                        return $scope.filterWithQuicksilverRanking(val1, val2)
                    });

                    var orderedData = params.sorting() ?
                        $filter('orderBy')(filteredData, params.orderBy()) :
                        data;
                    $defer.resolve(orderedData);
                    $scope.dataLoaded = true;
                    $rootScope.itemsQueue.build.start();
                    $rootScope.itemsQueue.tests.start();
                }
            });
        }, function(error) {
            $scope.alerts.addAlert(error.message);
        });

    };

    $rootScope.$watch('repo_selected', function(repo_selected) {
        if ($scope.buildsTableParams) {
            $scope.buildsTableParams.reload();
        }
    }, true);

    $scope.$watch('reqCounter', function(reqCounter) {
        // force default sorting when all data is in table
        if (!$scope.tableInitialized && $scope.itemsLoaded && $scope.filteredTreeData.length == data.length) {
            $scope.tableInitialized = true;
            if ($scope.buildsTableParams) {
                $scope.buildsTableParams.sorting();
            }
            if (build_date_errors.length > 0) {
                $scope.alerts.addAlert('Build dates for '+build_date_errors.length+' projects could not be found, so those projects have no date in the table below. Try rebuliding them.', 'warning');
            }
            if (tests_passing_errors.length > 0) {
                $scope.alerts.addAlert('Test results for '+tests_passing_errors.length+' projects could not be found, so those projects have an orange N/A result in the table below. Try rebuliding them.', 'warning');
            }
        }
    });
    $scope.init();

}]);
