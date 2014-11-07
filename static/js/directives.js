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
    return {
        link: function(scope, element, attrs) {
            var resort = true,
                callback = function(table){},
                config = {};
            element.tablesorter();
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
            }, 2000);
        }
    }
}]);

angular.module('myApp').directive('transposeTable', ['$timeout', function($timeout) {
    return {
        replace: true,
        link: function(scope, element, attr) {
            var arrows = '<span class="pull-right"><i class="fa fa-caret-left"></i> <i class="fa fa-caret-right"></i></span>',
                arrow_left = '<span class="pull-right"><i class="fa fa-caret-left"></i></span>',
                arrow_right = '<span class="pull-right"><i class="fa fa-caret-right"></i></span>',
                sorting_attr = 'data-sorting',
                td_class_locator = 'fixed-col',
                hidden_class_locator= '.hidden',
                fixed_td_locator = 'td.'+td_class_locator,
                asc = 'asc',
                dsc = 'dsc';

            function getDirection(direction) {
                return direction === asc ? {asc: 1, dsc: -1} : {asc: -1, dsc: 1};
            }

            function toggleDirection(td) {
                element.find(fixed_td_locator).find('span').remove();
                element.find(fixed_td_locator).append(arrows);
                $(td).find('span').remove();
                if ($(td).attr(sorting_attr) === asc) {
                    $(td).attr(sorting_attr, dsc);
                    $(td).append(arrow_right)
                } else {
                    $(td).attr(sorting_attr, asc);
                    $(td).append(arrow_left)
                }
            }

            function sortTableCols(row_num, compare_by, direction) {
                var drc = getDirection(direction);
                //Get all the rows
                var rows = element.find('tr');
                var vals = [];
                //Start sorting column along with data
                var tds = rows.eq(row_num).find('td').not('.'+td_class_locator);
                //compare_by outerText
                angular.forEach(tds, function(td) { vals.push(td[compare_by]) });
                var filtered = vals.sort();
                tds.sort(function(a, b) {
                    return filtered.indexOf($.text([a])) > filtered.indexOf($.text([b])) ? drc.asc : drc.dsc;
                }).each(function(new_Index) {
                        //Original Index
                        var original_Index = $(this).index();
                        //Reorder Header Text
                        rows.each(function() {
                            var th = $(this).find('th');
                            if (original_Index !== new_Index)
                                th.eq(original_Index).insertAfter(th.eq(new_Index));
                        });
                        //Reorder Column Data
                        rows.each(function() {
                            var td = $(this).find('td');
                            if (original_Index !== new_Index)
                                td.eq(original_Index).insertAfter(td.eq(new_Index));
                        });
                    });
                return false;
            }
            $(element).find(attr.transposeTable).on('click', function() {
                element.trigger('destroy');
                element.find(fixed_td_locator).find('span').remove();
                element.find('thead tr').detach().prependTo(element.find('tbody'));
                var t = element.find('tbody').eq(0);
                var r = t.find('tr');
                var cols = r.length;
                var rows = r.eq(0).find('td,th').not(hidden_class_locator).length;
                var cell, next, tem, i = 0;
                var tb= $('<tbody></tbody>');

                while (i < rows){
                    cell = 0;
                    tem= $('<tr></tr>');
                    while(cell < cols){
                        next = r.eq(cell++).find('td,th').not(hidden_class_locator).eq(0);
                        tem.append(next);
                    }
                    tb.append(tem);
                    ++i;
                }
                element.find('tbody').remove();
                $(tb).appendTo(element);
                element
                    .find('tbody tr:eq(0)')
                    .detach()
                    .appendTo(element.find('thead'))
                    .children()
                    .each(function(){
                        $(this).replaceWith('<th scope="col">'+$(this).html()+'</th>');
                    });
                element
                    .find('tbody tr th:first-child')
                    .each(function(){
                        $(this).replaceWith('<td class="'+td_class_locator+'" scope="row" ' + sorting_attr + '="' + asc +'">'+$(this).html()+'</td>');
                    });
                element.show();
                //element.trigger('resetToLoadState');
                element.trigger('destroy');
                element.tablesorter();
                element.trigger("updateAll", [true]);
                element.find(fixed_td_locator).append(arrows);
                element.find(fixed_td_locator).on('click', function() {
                    toggleDirection(this);
                    var colIndex = $(this).index();
                    var trIndex = $(this).closest('tr').index();
                    sortTableCols(trIndex+1, 'outerText', $(this).attr(sorting_attr));
                });
            });
            element.find(fixed_td_locator).on('click', function() {
                toggleDirection(this);
                var colIndex = $(this).index();
                var trIndex = $(this).closest('tr').index();
                sortTableCols(trIndex+1, 'outerText', $(this).attr(sorting_attr));
            });
            //#TODO trigger on specific event
            $timeout(function() {
                element.find(fixed_td_locator).on('click', function() {
                    toggleDirection(this);
                    var colIndex = $(this).index();
                    var trIndex = $(this).closest('tr').index();
                    sortTableCols(trIndex+1, 'outerText', $(this).attr(sorting_attr));
                });
            }, 5000)
        }
    }
}]);

angular.module('myApp').directive('barsChart', ['$parse', function($parse) {
    var drawChart = function(element, data) {
        //in D3, any selection[0] contains the group
        //selection[0][0] is the DOM node
        //but we won't need that this time
        var chart = d3.select(element);
        var max_data = d3.max(data),
            mean_data = d3.mean(data),
            scale = mean_data * 1.8;
        if (scale > 300) {
            scale = 300;
        }
        var x = d3.scale.linear()
            .domain([0, max_data])
            .range([0, scale]);
        //to our original directive markup bars-chart
        //we add a div with out chart stling and bind each
        //data entry to the chart
        chart.append("div")
            .attr("class", "d3chart")
            .selectAll('div')
            .data(data).enter().append("div")
            .style({'opacity': function(d) {
                if (d == 0) {
                    return 0;
                }
                return 1;
            }
            })
            .transition().ease("elastic")
            .style("width", function(d) { return x(d) + "px"; })
            .text(function(d) { return d; });
    };
    return {
        restrict: 'E',
        scope: {data: '=chartData'},
        replace: false,
        link: function (scope, element, attrs) {
            var changed = false;
            scope.$watch("data", function(newValue, oldValue) {
                if (newValue != oldValue) {
                    changed = true;
                    angular.element(element).empty();
                    drawChart(element[0], scope.data);
                }
            });
            if (!changed) {
                drawChart(element[0], scope.data);
            }
        }
    };
}]);

angular.module('myApp').directive('lineChart', ['$parse', 'stemWeights', function($parse, stemWeights) {
    var drawChart = function(element, data, steps_x, steps_y) {

        var margin = {top: 30, right: 20, bottom: 70, left: 50},
            width = 800 - margin.left - margin.right,
            height = 400 - margin.top - margin.bottom;

        // Set the ranges
        var x = d3.scale.linear().range([0, width]);
        var y = d3.scale.linear().range([height, 0]);

        // Define the axes
        var xAxis = d3.svg.axis().scale(x)
            .orient("bottom").ticks(steps_x).tickSize(-height, 0, 0);

        var yAxis = d3.svg.axis().scale(y)
            .orient("left").ticks(steps_y).tickSize(-width, 0, 0);

        // Define the line
        var distributeline = d3.svg.line()
            .x(function(d) { return x(d.step); })
//            .y(function(d) { return y(d.distribute); }).defined(function(d) { return d.distribute > 0; });
            .y(function(d) { return y(d.distribute); });
        // Adds the svg canvas

        var svg = d3.select(element)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");

        // Scale the range of the data
        x.domain(d3.extent(data, function(d) { return d.step; }));
        y.domain([0, d3.max(data, function(d) { return d.distribute; })]);

        // Nest the entries by symbol
        var dataNest = d3.nest()
            .key(function(d) {return d.symbol;})
            .entries(data);

        var color = d3.scale.category10(); // set the colour scale

        legendSpace = width/dataNest.length; // spacing for the legend

        // Loop through each symbol / key
        dataNest.forEach(function(d, i) {
            svg.append("path")
                .attr("class", "line")
                // Add the colours dynamically
                .style("stroke", function() { return d.color = color(d.key); })
                .attr("id", 'tag'+d.key.replace(/\s+/g, '')) // assign ID
                .attr("d", distributeline(d.values));

            // Add the Legend
            svg.append("text")
                .attr("x", (legendSpace/2)+i*legendSpace) // space legend
                .attr("y", height + (margin.bottom/2)+ 5)
                .attr("class", "d3legend noselect") // style the legend
                .style("fill", function() { // Add the colours dynamically
                    return d.color = color(d.key); })
                .on("click", function(){
                    // Determine if current line is visible
                    var active = d.active ? false : true,
                        newOpacity = active ? 0 : 1;
                    // Hide or show the elements based on the ID
                    d3.select("#tag"+d.key.replace(/\s+/g, ''))
                        .transition().duration(100)
                        .style("opacity", newOpacity);
                    // Update whether or not the elements are active
                    d.active = active;
                })
                .text(d.key);
        });

        // Add the X Axis
        svg.append("g")
            .attr("class", "x d3axis grid")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

        // Add the Y Axis
        svg.append("g")
            .attr("class", "y d3axis grid")
            .call(yAxis);
    };
    return {
        restrict: 'E',
        scope: {data: '=chartData', stepsX: '=stepsX', stepsY: '=stepsY'},
        replace: false,
        link: function (scope, element, attrs) {
            var changed = false;
            scope.$watch("data", function(newValue, oldValue) {
                if (newValue != oldValue) {
                    changed = true;
                    angular.element(element).empty();
                    drawChart(element[0], scope.data, scope.stepsX, scope.stepsY);
                }
            });
            if (!changed) {
                drawChart(element[0], scope.data, scope.stepsX, scope.stepsY);
            }
        }
    };
}]);
