angular.module('myApp').service('Mixins', [function() {
    this.checkAll = function() {
        var compare_to = arguments[0];
        function boolFilter(element, index, array) {
            return element === compare_to;
        }
        var args = Array.prototype.slice.call(arguments, 1);
        return args.every(boolFilter);
    };

    //<div ng-bind-html="&#item;"></div>
    //fails because of
    //https://github.com/angular/angular.js/pull/4747
    //https://github.com/angular/angular.js/pull/7485#issuecomment-43722719
    //https://github.com/angular/angular.js/issues/2174

    // encode(decode) html text into html entity
    this.decodeHtmlEntity = function(str) {
        return str.replace(/&#(\d+);/g, function(match, dec) {
            return String.fromCharCode(dec);
        });
    };

    this.updateChartTitle = function(title, attrs) {
        $("svg > g > text:contains('" + title + "')").attr(attrs || {x:50});
    };

    this.encodeHtmlEntity = function(str) {
        var buf = [];
        for (var i=str.length-1;i>=0;i--) {
            buf.unshift(['&#', str[i].charCodeAt(), ';'].join(''));
        }
        return buf.join('');
    };
}]);

//#TODO Angular fails on generators
//angular.module('myApp').service('stemWeights', [function() {
//    function zip() {
//        var args = [].slice.call(arguments);
//        var longest = args.reduce(function(a,b){
//            return a.length>b.length ? a : b
//        }, []);
//
//        return longest.map(function(_,i){
//            return args.map(function(array){return array[i]})
//        });
//    }
//
//    function* range(n) {
//        for (var i = 0; i < n; i++)
//            yield i;
//    }
//
//    this.distributeEqual = function(min_val, max_val, n){
//        var d = mathjs.divide((max_val - min_val), (n-1));
//        return [min_val + i*d for (i of range(n))];
//    };
//
//    this.distributeLucas = function(min_val, max_val, n){
//        var q = mathjs.divide(max_val, min_val);
//        return [mathjs.multiply(min_val, mathjs.pow(q, (mathjs.divide(i, n-1)))) for (i of range(n))];
//    };
//
//    this.distributePablo = function(min_val, max_val, n){
//        var results = [];
//        var es = this.distributeEqual(min_val, max_val, n);
//        var ls = this.distributeLucas(min_val, max_val, n);
//        var zipped = zip([i for (i of range(n))], es, ls);
//        for(var j = 0; j < zipped.length; j++) {
//            var i= zipped[j][0],
//                e = zipped[j][1],
//                l = zipped[j][2];
//            var res = mathjs.multiply(l, (mathjs.subtract(1, mathjs.divide(i, mathjs.subtract(n, 1))))) + mathjs.multiply(e, (mathjs.divide(i, (mathjs.subtract(n, 1)))));
//            results.push(res);
//        }
//    };
//}]);

angular.module('myApp').service('stemWeights', [function() {
    function zip() {
        var args = [].slice.call(arguments);
        var longest = args.reduce(function(a,b){
            return a.length>b.length ? a : b
        }, []);

        return longest.map(function(_,i){
            return args.map(function(array){return array[i]})
        });
    }

    function range(start, stop, step){
        if (typeof stop=='undefined'){
            // one param defined
            stop = start;
            start = 0;
        }
        if (typeof step=='undefined'){
            step = 1;
        }
        if ((step>0 && start>=stop) || (step<0 && start<=stop)){
            return [];
        }
        var result = [];
        for (var i=start; step>0 ? i<stop : i>stop; i+=step){
            result.push(i);
        }
        return result;
    }

    this.distributeEqual = function(min_val, max_val, n){
        var d = mathjs.divide((mathjs.subtract(max_val, min_val)), mathjs.subtract(n, 1)),
            items = range(n),
            results = [];
        for(var i = 0; i < items.length; i++) {
            var result = mathjs.add(min_val, mathjs.multiply(i, d));
            results.push(result);
        }
        return results;
    };

    this.distributeLucas = function(min_val, max_val, n){
        var q = mathjs.divide(max_val, min_val),
            items = range(n),
            results = [];
        for(var i = 0; i < items.length; i++) {
            var result = mathjs.multiply(min_val, mathjs.pow(q, (mathjs.divide(i, n-1))));
            results.push(result);
        }
        return results;
    };

    this.distributePablo = function(min_val, max_val, n){
        var items = range(n),
            results = [],
            es = this.distributeEqual(min_val, max_val, n),
            ls = this.distributeLucas(min_val, max_val, n),
            zipped = zip(items, es, ls);
        for(var j = 0; j < zipped.length; j++) {
            var i= zipped[j][0],
                e = zipped[j][1],
                l = zipped[j][2];
            var res = mathjs.multiply(l, (mathjs.subtract(1, mathjs.divide(i, mathjs.subtract(n, 1))))) + mathjs.multiply(e, (mathjs.divide(i, (mathjs.subtract(n, 1)))));
            results.push(res);
        }
        return results;
    };
}]);

// helper service to build paths
angular.module('myApp').service('PathBuilder', ['appConfig', function(appConfig) {
    //#TODO should be some built-in solution
    this._repo = {owner: null, name: null};
    this.buildPath = function() {
        var args = [];
        angular.forEach(arguments, function(item) {
            args.push(item);
        });
        return args.join('/')
    };

    this.buildDataPath = function() {
        var args = [appConfig.data_dir];
        angular.forEach(arguments, function(item) {
            args.push(item);
        });
        return args.join('/');
    };
    this.buildPagesPath = function() {
        var args = [appConfig.data_dir, appConfig.pages_dir];
        angular.forEach(arguments, function(item) {
            args.push(item);
        });
        return args.join('/');
    };

    this.buildGhPagesUrl = function() {
        var args = [appConfig.base_url, this._repo.owner, this._repo.name, 'gh-pages'];
        angular.forEach(arguments, function(item) {
            args.push(item);
        });
        return args.join('/');
    };

    this.buildDataUrl = function() {
        var args = [appConfig.base_url, this._repo.owner, this._repo.name, 'gh-pages', 'build_info', appConfig.data_dir];
        angular.forEach(arguments, function(item) {
            args.push(item);
        });
        return args.join('/');
    };

    this.buildPagesUrl = function() {
        var args = [appConfig.base_url, this._repo.owner, this._repo.name, 'gh-pages', 'build_info', appConfig.data_dir, appConfig.pages_dir];
        angular.forEach(arguments, function(item) {
            args.push(item);
        });
        return args.join('/');
    };

    this.buildTravisUrl = function() {
        return ['https://api.travis-ci.org/repos', this._repo.owner, this._repo.name].join('/');
    };
}]);

//API services
angular.module('myApp').service('appApi', ['$http', '$q', 'PathBuilder', 'appConfig', function($http, $q, PathBuilder, appConfig) {
    this.setActiveRepo = function(repo) {
        PathBuilder._repo = repo;
    };

    this.getAppInfo = function() {
        return $http.get(PathBuilder.buildDataUrl(appConfig.app));
    };

    this.getRepoInfo = function() {
        return $http.get(PathBuilder.buildDataUrl(appConfig.repo));
    };

    this.getMetadata = function() {
        return $http.get(PathBuilder.buildGhPagesUrl(appConfig.metadata));
    };

    this.getMetadataNew = function() {
        return $http.get(PathBuilder.buildGhPagesUrl(appConfig.metadata_new));
    };

    this.getRepos = function() {
        return $http.get(appConfig.git_modules_url);
    };

    this.checkRepo = function(repo) {
        var url = [appConfig.base_url, repo.owner, repo.name, 'gh-pages', appConfig.metadata].join('/');
        return $http.get(url);
    };

    this.getRepoBuildInfo = function() {
        return $http.get(PathBuilder.buildTravisUrl(), {headers: { 'Accept': 'application/vnd.travis-ci.2+json' }});
    };
}]);

angular.module('myApp').service('reposApi', ['$http', '$q', 'appConfig', function($http, $q, appConfig) {
    this.getRepos = function() {
        return $http.get(appConfig.git_modules_url);
    };

    this.getCollection = function(access_token) {
        // https://api.github.com/repos/fontdirectory/collection/git/trees/HEAD?access_token=00b736654b0b607a630d457f9ab89acc7293f61b&recursive=1
        return $http.get('https://api.github.com/repos/google/fonts/git/trees/HEAD', {params: {'access_token': access_token, 'recursive': 1} })
    };
}]);

angular.module('myApp').service('metadataApi', ['$http', '$q', 'PathBuilder', 'appConfig', function($http, $q, PathBuilder, appConfig) {
    var name = 'metadata';

    this.getMetadata = function() {
        return $http.get(PathBuilder.buildGhPagesUrl(appConfig.metadata));
    };

    this.getMetadataNew = function() {
        return $http.get(PathBuilder.buildGhPagesUrl(appConfig.metadata_new));
    };

    this.getMetadataRaw = function() {
        return $http.get(PathBuilder.buildGhPagesUrl(appConfig.metadata), {transformResponse: []});
    };

    this.getMetadataNewRaw = function() {
        return $http.get(PathBuilder.buildGhPagesUrl(appConfig.metadata_new), {transformResponse: []});
    };
    this.getRawFiles = function(urls_list) {
        var urls = urls_list || [{url: PathBuilder.buildGhPagesUrl(appConfig.metadata)},
            {url: PathBuilder.buildGhPagesUrl(appConfig.metadata_new)}];
        var deferred = $q.defer();
        var urlCalls = [];
        angular.forEach(urls, function(url) {
            urlCalls.push($http.get(url.url, {transformResponse: []}));
        });
        // they may, in fact, all be done, but this
        // executes the callbacks in then, once they are
        // completely finished.
        $q.all(urlCalls).then(
            function(results) {
                deferred.resolve(results)
            },
            function(errors) {
                deferred.reject(errors);
            },
            function(updates) {
                deferred.update(updates);
            });
        return deferred.promise;
    };

    this.getTests = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'tests.json'));
    };
}]);

angular.module('myApp').service('testsApi', ['$http', '$q', 'PathBuilder', function($http, $q, PathBuilder) {
    var name = 'tests';

    this.getTests = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'tests.json'));
    };

}]);

angular.module('myApp').service('summaryApi', ['$http', '$q', 'PathBuilder', function($http, $q, PathBuilder) {
    var name = 'summary';
    this.getStems = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'stems.json'));
    };
    this.getMetrics = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'metrics.json'));
    };
    this.getTableSizes = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'table_sizes.json'));
    };
    this.getAutohintSizes = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'autohint_sizes.json'));
    };
    this.getFontaineFonts = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'fontaine_fonts.json'));
    };
    this.getFontsOrthography = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'fonts_orthography.json'));
    };
    this.getTests = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'tests.json'));
    };
    this.getFontsTableGrouped = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'fonts_tables_grouped.json'));
    };
}]);

angular.module('myApp').service('checksApi', ['$http', '$q', 'PathBuilder', function($http, $q, PathBuilder) {
    var name = 'checks';
    this.getTests = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'tests.json'));
    };

    this.getUpstreamYamlFile = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'upstream.yaml'));
    };
}]);

angular.module('myApp').service('buildApi', ['$http', '$q', 'PathBuilder', function($http, $q, PathBuilder) {
    var name = 'build';
    this.getBuildLog = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'buildlog.html'), {transformResponse: []});
    };
}]);

angular.module('myApp').service('bakeryYamlApi', ['$http', '$q', 'PathBuilder', function($http, $q, PathBuilder) {
    var name = 'bakery-yaml';
    this.getYamlFile = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'bakery_yaml.json'), {transformResponse: []});
    };
}]);

angular.module('myApp').service('descriptionApi', ['$http', '$q', 'PathBuilder', function($http, $q, PathBuilder) {
    var name = 'description';
    this.getDescriptionFile = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'DESCRIPTION.en_us.html'), {transformResponse: []});
    };
}]);

angular.module('myApp').service('reviewApi', ['$http', '$q', 'PathBuilder', function($http, $q, PathBuilder) {
    var name = 'review';
    this.getOrthography = function() {
        return $http.get(PathBuilder.buildPagesUrl(name, 'orthography.json'));
    };
}]);

angular.module('myApp').service('aboutApi', ['$http', '$q', function($http, $q) {
    var name = 'about';

    this.getAuthors = function() {
        return $http.get('AUTHORS.txt', {transformResponse: []});
    };

    this.getContributors = function() {
        return $http.get('CONTRIBUTORS.txt', {transformResponse: []});
    };

}]);

angular.module('myApp').service('githubService', ['$q', '$location', '$localStorage', '$sessionStorage', function($q, $location, $localStorage, $sessionStorage) {
    var $storage = $sessionStorage.$default({
            OAuth_result: {access_token: null, token_type: null},
            OAuth_error: null,
            OAuth_passed: false,
            OAuth_redirect_done: false
        }
    );

    this.initializeOAuth = function() {
        //initialize OAuth.io with public key of the application
        OAuth.initialize('t5jdh3VeWpRP2zg0tkRSen4N66Y', {cache:true});
        //try to create an authorization result when the page loads,
        $storage.OAuth_result = OAuth.create(
            'github',
            {
                access_token: $storage.OAuth_result.access_token,
                token_type: $storage.OAuth_result.token_type
            }
        );
    };

    this.isReadyOAuth = function() {
        return ($storage.OAuth_result.access_token);
    };

    this.connectOAuth = function() {
        var deferred = $q.defer();
        var promise = OAuth.callback('github');
        if (promise) {
            promise.done(function(result) {
                deferred.resolve();
                $storage.OAuth_result = result;
                $storage.OAuth_error = null;
                $storage.OAuth_passed = true;
                $storage.OAuth_redirect_done = false;
            });
            promise.fail(function(error) {
                $storage.OAuth_result = {access_token: null, token_type: null};
                $storage.OAuth_error = error;
                $storage.OAuth_passed = false;
                $storage.OAuth_redirect_done = false;
            });
        } else {
            $storage.OAuth_redirect_done = true;
            OAuth.redirect('github', {cache:true}, '#' + $location.path());
        }
        return deferred.promise;
    };

    this.resetOAuth = function() {
        OAuth.clearCache('github');
        $storage.OAuth_result = {access_token: null, token_type: null};
        $storage.OAuth_error = null;
        $storage.OAuth_passed = false;
        $storage.OAuth_redirect_done = false;
    }

}]);
