myApp.controller('summaryController', ['$scope', '$rootScope', '$http', '$filter', '$document', 'summaryApi', 'Mixins', 'stemWeights', 'ngTableParams', function($scope, $rootScope, $http, $filter, $document, summaryApi, Mixins, stemWeights, ngTableParams) {
    $scope.overall_pie_chart = null;
    $scope.average_line_chart = null;
    $scope.deviation_line_chart = null;
    $scope.tests = null;
    $scope.metrics = null;
    $scope.stems = null;
    $scope.faces = {};
    $scope.table_sizes = null;
    $scope.autohint_sizes = null;
    $scope.fontaine_fonts = null;
    $scope.fonts_orthography = null;
    $scope.fonts_tables_grouped = null;
    $scope.fontSupportToStyle = {
        'full': 'success',
        'partial': 'info',
        'fragmentary': 'warning',
        'unsupported': 'danger'
    };
    $scope.distribute_font_family = [];
    $scope.distribute_equal = [];
    $scope.distribute_pablo = [];
    $scope.distribute_lucas = [];

    $scope.stemCalcParams = {min: 20, max: 220, steps: 9}; // set some defaults

    angular.forEach([100, 200, 300, 400, 500, 600, 700, 800, 900], function(weight) {
        $scope.faces[weight] = $rootScope.metadata.fonts.filter(function(face) {
            return face.weight == weight;
        });
    });

    summaryApi.getMetrics().then(function(response) {
        $scope.metrics = response.data;
    });

    $scope.getStemDiff = function(data, index) {
        if (index > 0) {
            return data[index] - data[index-1]
        }
        return null;
    };

    $scope.getDistributeFontFamily = function() {
        var data = [];
        angular.forEach($scope.stems, function(item) {
            data.push(item.stem);
        });
        data.sort();
        return data;
    };

    $scope.getDistributeEqual = function() {
        var distributeEqual = stemWeights.distributeEqual(
            $scope.stemCalcParams.min,
            $scope.stemCalcParams.max,
            $scope.stemCalcParams.steps
        );
        angular.forEach(distributeEqual, function(item, index) {
            distributeEqual[index] = mathjs.round(item);
        });
        return distributeEqual;
    };

    $scope.getDistributeLucas = function() {
        var distributeLucas = stemWeights.distributeLucas(
            $scope.stemCalcParams.min,
            $scope.stemCalcParams.max,
            $scope.stemCalcParams.steps
        );
        angular.forEach(distributeLucas, function(item, index) {
            distributeLucas[index] = mathjs.round(item);
        });
        return distributeLucas;
    };

    $scope.getDistributePablo = function() {
        var distributePablo = stemWeights.distributePablo(
            $scope.stemCalcParams.min,
            $scope.stemCalcParams.max,
            $scope.stemCalcParams.steps
        );
        angular.forEach(distributePablo, function(item, index) {
            distributePablo[index] = mathjs.round(item);
        });
        return distributePablo;
    };

    $scope.calculateStemWeightsDistributions = function() {
        $scope.distribute_equal = $scope.getDistributeEqual();
        $scope.distribute_pablo = $scope.getDistributePablo();
        $scope.distribute_lucas = $scope.getDistributeLucas();
        $scope.distribute_font_family = $scope.getDistributeFontFamily();
        if ($scope.stemTableParams) {
            $scope.stemTableParams.reload();
            $scope.stemTableParams.total($scope.distribute_equal.length);
            $scope.stemTableParams.counts = [];
            $scope.stemTableParams.count($scope.distribute_equal.length);
        }
    };

    summaryApi.getStems().then(function(response) {
        $scope.stems = response.data;
        $scope.calculateStemWeightsDistributions();

        $scope.stemTableParams = new ngTableParams({
            // show first page
            page: 1,
            // count per page
            sorting: {
                step: 'asc'
            },
            count: $scope.distribute_equal.length
        }, {
            // hide page counts control
            counts: [],
            // length of data
            total: $scope.distribute_equal.length,
            getData: function($defer, params) {
                var data = [];
                for(var i = 0; i < $scope.stemCalcParams.steps; i++) {
                    var item = {
                        step: i + 1,
                        distribute_equal: $scope.distribute_equal[i],
                        distribute_pablo: $scope.distribute_pablo[i],
                        distribute_lucas: $scope.distribute_lucas[i],
                        distribute_equal_stem_diff: $scope.getStemDiff($scope.distribute_equal, i),
                        distribute_pablo_stem_diff: $scope.getStemDiff($scope.distribute_pablo, i),
                        distribute_lucas_stem_diff: $scope.getStemDiff($scope.distribute_lucas, i)
                    };
                    data.push(item);
                }
                var orderedData = params.sorting() ?
                    $filter('orderBy')(data, params.orderBy()) :
                    data;
                params.total(orderedData.length);
                $defer.resolve(orderedData);
            }
        });
    });

    summaryApi.getTableSizes().then(function(response) {
        $scope.table_sizes = response.data;
    });
    summaryApi.getAutohintSizes().then(function(response) {
        $scope.autohint_sizes = response.data;
    });
    summaryApi.getFontaineFonts().then(function(response) {
        $scope.fontaine_fonts = response.data;
    });
    summaryApi.getFontsOrthography().then(function(response) {
        $scope.fonts_orthography = response.data;
    });
    summaryApi.getTests().then(function(response) {
        $scope.tests = response.data;
        var watch_list = ['error', 'failure', 'fixed'];
        var watch_tag = 'required';
        var data = [];
        // reformat data for table
        angular.forEach($scope.tests, function(test) {
            angular.forEach($scope.resultMap, function(result_val, result_key) {
                if (watch_list.indexOf(result_key) != -1) {
                    angular.forEach(test[result_key], function(test_obj) {
                        if (test_obj.tags.indexOf(watch_tag) != -1) {
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
                        }
                    })
                }
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
                error_len = test['error'].length;
            chartsum = {
                "success": chartsum.success + success_len,
                "error": error_len,
                "failure": chartsum.failure + failure_len,
                "fixed": chartsum.fixed + fixed_len
            }
        });
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
                    title: 'Overall Test Results',
                    chartArea: {'width': '50%'},
                    is3D: true,
                    colors: ['#468847', '#3a87ad', '#b94a48', '#c09853']
                };
            $scope.overall_pie_chart = {data: gdata, options: options, type: "PieChart", displayed: true};
        }
    });
    summaryApi.getFontsTableGrouped().then(function(response) {
        var colors_array = [
            '#3366CC', '#DC3912', '#FF9900', '#109618', '#990099',
            '#3B3EAC', '#0099C6', '#DD4477', '#66AA00', '#B82E2E',
            '#316395', '#994499', '#22AA99', '#AAAA11', '#6633CC',
            '#E67300', '#8B0707', '#329262', '#5574A6', '#3B3EAC'
        ];
        $scope.fonts_tables_grouped = response.data;
        var headings1 = ['Table', 'Average (dashed line)'].concat($scope.fonts_tables_grouped.grouped.fonts);
        var aggregated_table = [];
        aggregated_table.push(headings1);
        angular.forEach($scope.fonts_tables_grouped.grouped.tables, function(table) {
            aggregated_table.push(table)
        });

        var data1 = google.visualization.arrayToDataTable(aggregated_table);
        var colors_array1 = angular.copy(colors_array);
        colors_array1.unshift('#1a1a1a');
        var options1 = {
            series: {
                0: { lineDashStyle: [10, 2] }
            },

            colors: colors_array1,
            title: 'Fonts compared to average',
            is3D: true,
            vAxis: {
                title: 'Size (bytes)'
            },
            hAxis: {
                slantedText: true
            },
            height: 500
        };
        $scope.average_line_chart = {data: data1, options: options1, type: 'LineChart', displayed: true};

        var headings2 = ["Table"].concat($scope.fonts_tables_grouped.delta.fonts);
        var deviation_table = [];
        deviation_table.push(headings2);
        angular.forEach($scope.fonts_tables_grouped.delta.tables, function(table) {
            deviation_table.push(table);
        });

        var data2 = google.visualization.arrayToDataTable(deviation_table);

        var options2 = {
            colors: colors_array,
            bar: {groupWidth: "68%"},
            title: "Deviation from an average",
            is3D: true,
            vAxis: {
                title: "Deviation (bytes)"
            },
            hAxis: {
                slantedText: true
            },
            height: 500
        };
        $scope.deviation_line_chart = {data: data2, options: options2, type: 'ColumnChart', displayed: true};

    });

    $scope.isReady = function() {
        return !Mixins.checkAll(
            null, $scope.metrics, $scope.stems, $scope.tests, $scope.faces,
            $scope.table_sizes, $scope.autohint_sizes,
            $scope.fontaine_fonts, $scope.fonts_orthography
        )
    };

    $document
        .ready(function() {
            $document
                .on("click", "td.coverageStats", function() {
                    // show modal window on click in td
                    // in Font Coverage characters table
                    var hidden_td = angular.element(this).closest('td').next(),
                        missing_chars = hidden_td.html(),
                        subset = hidden_td.attr("data-subset"),
                        font = hidden_td.attr("data-fontname");
                    angular.element("#myModalInfo").html("<h5>"+font+"</h5><small>"+subset+"</small>");
                    angular.element(".modal-body").html(missing_chars);
                })
                .on("click", "td.coverageAverage", function() {
                    var parent_tr = angular.element(this).parent('tr'),
                        subset = angular.element(parent_tr).find('td.missing-chars:first').attr("data-subset"),
                        modal_body = angular.element(".modal-body");
                    modal_body.empty();
                    angular.element("#myModalInfo").html("<h5>"+subset+"</h5>");
                    angular.element(parent_tr).find('td.missing-chars').each(function(i){
                        var font = angular.element(this).attr("data-fontname"),
                            missing_chars = angular.element(this).html();
                        modal_body.append("<strong>"+font+"</strong>"+missing_chars+"<hr>")
                    });
                })
        })
}]);