angular.module('myApp').controller('logController', ['$scope', '$http', '$sce', 'buildApi', function($scope, $http, $sce, buildApi) {
    $scope.dataLoaded = false;

    $scope.skipValidation = function(value) {
        return $sce.trustAsHtml(value);
    };

    buildApi.getBuildLog().then(function(response) {
        $scope.data = response.data;
        $scope.dataLoaded = true;
    });
}]);