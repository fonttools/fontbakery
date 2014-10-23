angular-route-styles
====================

This is a simple module for AngularJS that provides the ability to have route-specific CSS stylesheets, by integrating with Angular's built-in `$routeProvider` service.

What does it do?
---------------

It allows you to declare partial-specific or route-specific styles for your app using
Angular's built-in `$routeProvider` service.  For example, if you are already using
`$routeProvider`, you know that it allows you to easily setup your SPA routes by declaring
a `.when()` block and telling Angular what template (or templateUrl) to use for each
route, and also which controller to associate with that route.  Well, up until now, Angular
did not provide a way to add specific CSS stylesheets that should be dynamically loaded
when the given route is hit.  This solves that problem by allowing you to do something like this:

```javascript
app.config(['$routeProvider', function($routeProvider){
    $routeProvider
        .when('/some/route/1', {
            templateUrl: 'partials/partial1.html', 
            controller: 'Partial1Ctrl',
            css: 'css/partial1.css'
        })
        .when('/some/route/2', {
            templateUrl: 'partials/partial2.html',
            controller: 'Partial2Ctrl'
        })
        .when('/some/route/3', {
            templateUrl: 'partials/partial3.html',
            controller: 'Partial3Ctrl',
            css: ['css/partial3_1.css','css/partial3_2.css']
        })
        .when('/some/route/4', {
            templateUrl: 'partials/partial4.html',
            controller: 'Partial4Ctrl',
            css: function(params) {
                if (params.some_param) {
                    return ['//example.com/static/css/' + params.some_param];
                } else {
                    return [];
                }
            }
        })
        // more routes can be declared here
}]);
```

How to install:
---------------

**Using bower:**
> `bower install angular-route-styles`

**OR**

**Using GitHub:**
> git clone https://github.com/tennisgent/angular-route-styles

**1) Include the `route-styles.js` file to your `index.html` file**

```html
<!-- should be added at the end of your body tag -->
<body>
    ...
    <script scr="path/to/route-styles.js"></script>
</body>
```

**2) Declare the `'routeStyles'` module as a dependency in your main app**

```javascript
angular.module('myApp', ['ngRoute','routeStyles' /* other dependencies here */]);
```
**NOTE**: you must also include the `ngRoute` service module from angular, or at least make the
module available by adding the `angular-route.js` (or `angular-route.min.js`) script
to your html page.

**NOTE:** this code also requires that your Angular app has access to the `<head>` element.  Typically this
requires that your `ng-app` directive is on the `<html>` element.  For example: `<html ng-app="myApp">`.

**3) Add your route-specific styles to the `$routeProvider` in your app's config**

```javascript
var app = angular.module('myApp', []);
app.config(['$routeProvider', function($routeProvider){
    $routeProvider
        .when('/some/route/1', {
            templateUrl: 'partials/partial1.html', 
            controller: 'Partial1Ctrl',
            css: 'css/partial1.css'
        })
        .when('/some/route/2', {
            templateUrl: 'partials/partial2.html',
            controller: 'Partial2Ctrl'
        })
        .when('/some/route/3', {
            templateUrl: 'partials/partial3.html',
            controller: 'Partial3Ctrl',
            css: ['css/partial3_1.css','css/partial3_2.css']
        })
        // more routes can be declared here
}]);
```
**Things to notice:**
* Specifying a css property on the route is completely optional, as it was omitted from the `'/some/route/2'` example. If the route doesn't have a css property, the service will simply do nothing for that route.
* You can even have multiple page-specific stylesheets per route, as in the `'/some/route/3'` example above, where the css property is an **array** of relative paths to the stylesheets needed for that route.


How does it work?
-----------------
###Route Setup:

This config adds a custom css property to the object that is used to setup each page's route. That object gets passed to each `'$routeChangeStart'` event as `.$$route`. So when listening to the `'$routeChangeStart'` event, we can grab the css property that we specified and append/remove those `<link />` tags as needed.

###Custom Head Directive:

```javascript
app.directive('head', ['$rootScope','$compile',
    function($rootScope, $compile){
        return {
            restrict: 'E',
            link: function(scope, elem){
                var html = '<link rel="stylesheet" ng-repeat="(routeCtrl, cssUrl) in routeStyles" ng-href="{{cssUrl}}" />';
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
```

This directive does the following things:

* It compiles (using `$compile`) an html string that creates a set of <link /> tags for every item in the `scope.routeStyles` object using `ng-repeat` and `ng-href`.
* It appends that compiled set of `<link />` elements to the `<head>` tag.
* It then uses the `$rootScope` to listen for `'$routeChangeStart'` events. For every `'$routeChangeStart'` event, it grabs the "current" `$$route` object (the route that the user is about to leave) and removes its partial-specific css file(s) from the `<head>` tag. It also grabs the "next" `$$route` object (the route that the user is about to go to) and adds any of its partial-specific css file(s) to the `<head>` tag.
* And the `ng-repeat` part of the compiled `<link />` tag handles all of the adding and removing of the page-specific stylesheets based on what gets added to or removed from the `scope.routeStyles` object.