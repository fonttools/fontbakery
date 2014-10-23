angular.module('myApp').controller('metadataController', ['$scope', '$http', '$q', '$filter', 'metadataApi', 'PathBuilder', 'appConfig', 'ngTableParams', function($scope, $http, $q, $filter, metadataApi, PathBuilder, appConfig, ngTableParams) {
    $scope.charts = [];
    $scope.dataLoaded = false;
    $scope.editor1 = null;
    $scope.editor2 = null;

    $scope.view_url = PathBuilder.buildPath($scope.repo_info.url, 'blob', 'master', appConfig.metadata);
    $scope.edit_url = PathBuilder.buildPath($scope.repo_info.url, 'edit', 'master', appConfig.metadata);

    var doDiff = function(editor1, editor2, result_of_diff) {
        return function () {
            try {
                var left = JSON.parse(editor1.getValue());
                var right = JSON.parse(editor2.getValue());

                var instance = jsondiffpatch.create({
                    objectHash: function (obj) {
                        return '';
                    }
                });

                var delta = instance.diff(left, right);

                var visualdiff = document.getElementById(result_of_diff);
                if (visualdiff) {
                    visualdiff.innerHTML = jsondiffpatch.formatters.html.format(delta, left);

                    var scripts = visualdiff.querySelectorAll('script');
                    for (var i = 0; i < scripts.length; i++) {
                        var s = scripts[i];
                        /* jshint evil: true */
                        eval(s.innerHTML);
                    }
                }
                if (!delta) {
                    $scope.alerts.addAlert('Two files are equal.', 'info');
                }
                angular.element(visualdiff).find('div').first().find('pre')
                    .each(function (i) {
                        angular.element(this).css("background-color", "transparent").css("border", "0");
                    })

            } catch (e) {
                $scope.alerts.addAlert(e.name+": "+ e.message);
            }
        };
    };

    $scope.$watch('dataLoaded', function() {
        if ($scope.dataLoaded) {
            if ($scope.editor1 && $scope.editor2) {
                $scope.doDiff = doDiff($scope.editor1.getSession(), $scope.editor2.getSession(), 'visualdiff');
//                $scope.doDiff();
            }
        }
    });

    metadataApi.getTests().then(function(response) {
        $scope.tests = response.data;
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
                        result_class: result_val
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

        angular.forEach($scope.tests, function(test) {
            var success_len = test['success'].length;
            var fixed_len = test['fixed'].length;
            var failure_len = test['failure'].length;
            var error_len = test['error'].length;
            var data = google.visualization.arrayToDataTable([
                ['Tests', '#'],
                ['Success '+success_len, success_len],
                ['Fixed '+fixed_len, fixed_len],
                ['Failed '+failure_len, failure_len],
                ['Error '+error_len, error_len]
            ]);
            var options = {
                title: test.name,
                is3D: true,
                colors: ['#468847', '#3a87ad', '#b94a48', '#c09853']
            };
            $scope.charts.push({data: data, options: options, type: "PieChart", displayed: true});
        });
    });

    metadataApi.getRawFiles().then(function(responses) {
        $scope.metadata1 = responses[0].data;
        $scope.metadata2 = responses[1].data;
        $scope.dataLoaded = true;
//        $scope.doDiff();
    });

    $scope.aceLoaded1 = function(_editor) {
        $scope.editor1 = _editor;
    };

    $scope.aceChanged1 = function(_editor) {
    };

    $scope.aceLoaded2 = function(_editor) {
        $scope.editor2 = _editor;
    };

    $scope.aceChanged2 = function(_editor) {
    };
}]);