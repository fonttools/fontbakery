myApp.controller('setupController', ['$scope', '$http', 'bakeryYamlApi', 'PathBuilder', function($scope, $http, bakeryYamlApi, PathBuilder) {
    $scope.dataLoaded = false;

    bakeryYamlApi.getYamlFile().then(function(response) {
        $scope.data = response.data;
        $scope.dataLoaded = true;
    });

    $scope.aceLoaded = function(_editor) {
    };

    $scope.aceChanged = function(_editor) {
    };

    $scope.view_url = PathBuilder.buildPath($scope.repo_info.url, 'blob', 'master', 'bakery.yaml');
    $scope.edit_url = PathBuilder.buildPath($scope.repo_info.url, 'edit', 'master', 'bakery.yaml');
}]);
