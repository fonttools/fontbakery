angular.module('myApp').controller('logController', ['$scope', '$http', 'buildApi', function($scope, $http, buildApi) {
    $scope.dataLoaded = false;

    buildApi.getBuildLog().then(function(response) {
        $scope.data = response.data;
        $scope.dataLoaded = true;
    });
}]);