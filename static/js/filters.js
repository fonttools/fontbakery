angular.module('myApp').filter('replace', [function () {
    return function (target, arg1, arg2) {
        return target.split(arg1).join(arg2);
    };
}]);

angular.module('myApp').filter( 'default', [ '$filter', function($filter) {
    return function( input, defaultValue ) {
        if ( !input ) return defaultValue;
        return input;
    };
}]);