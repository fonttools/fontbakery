myApp.controller('testsController', ['$scope', '$http', '$filter', 'PathBuilder', 'testsApi', 'ngTableParams', function($scope, $http, $filter, PathBuilder, testsApi, ngTableParams) {
    $scope.charts = [];
    $scope.average_chart = null;
    $scope.dataLoaded = false;

    testsApi.getTests().then(function(response) {
        $scope.tests = response.data;
        $scope.dataLoaded = true;

        var data = [];
        // reformat data for table
        angular.forEach($scope.tests, function(test) {
            angular.forEach($scope.resultMap, function(result_val, result_key) {
                angular.forEach(test[result_key], function(test_obj) {
                    var item = {
                        font: test.name,
                        orig_data: test_obj, // keep original data
                        categories: test_obj.tags.join(', '),
                        description: test_obj.methodDoc,
                        result_msg: test_obj.err_msg,
                        result_status: $scope.statusMap[result_key],
                        result_class: result_val,
                        gh_link: PathBuilder.buildPath($scope.repo_info.fontbakery.master_url, $filter('replace')(test_obj.name, '.', '/')+".py")
                    };
                    data.push(item);
                })
            });
        });

        $scope.testsTableParams = new ngTableParams({
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

        var chartsum = {"success": 0, "failure": 0, "fixed": 0, "error": 0};
        angular.forEach($scope.tests, function(test) {
            var success_len = test['success'].length,
                fixed_len = test['fixed'].length,
                failure_len = test['failure'].length,
                error_len = test['error'].length,
                gdata = google.visualization.arrayToDataTable([
                    ['Tests', '#'],
                    ['Success '+success_len, success_len],
                    ['Fixed '+fixed_len, fixed_len],
                    ['Failed '+failure_len, failure_len],
                    ['Error '+error_len, error_len]
                ]),
                options = {
                    title: test.name,
                    is3D: true,
                    chartArea: {'width': '100%'},
                    colors: ['#468847', '#3a87ad', '#b94a48', '#c09853']
                };
            $scope.charts.push({data: gdata, options: options, type: "PieChart", displayed: true});
            chartsum = {
                "success": chartsum.success + success_len,
                "error": error_len,
                "failure": chartsum.failure + failure_len,
                "fixed": chartsum.fixed + fixed_len
            }
        });
        // build chart of average values if we have more than 1 font
        if ($scope.tests.length > 1) {
            var success_len = chartsum.success,
                fixed_len = chartsum.fixed,
                failure_len = chartsum.failure,
                error_len = chartsum.error,
                gdata = google.visualization.arrayToDataTable([
                    ['Tests', '#'],
                    ['Success '+success_len, success_len],
                    ['Fixed '+fixed_len, fixed_len],
                    ['Failed '+failure_len, failure_len],
                    ['Error '+error_len, error_len]
                ]),
                options = {
                    title: "Average",
                    is3D: true,
                    chartArea: {'width': '100%'},
                    colors: ['#468847', '#3a87ad', '#b94a48', '#c09853']
                };
            $scope.average_chart = {data: gdata, options: options, type: "PieChart", displayed: true};
        }
    });
}]);

