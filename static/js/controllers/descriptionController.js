angular.module('myApp').controller('descriptionController', ['$scope', 'descriptionApi', function($scope, descriptionApi) {
    $scope.dataLoaded = false;

    descriptionApi.getDescriptionFile().then(function(response) {
        $scope.data = response.data;
        $scope.dataLoaded = true;
    });

    $scope.aceLoaded = function(_editor) {
        $scope.editor = _editor;
        $scope.data = $scope.editor.getSession().getValue();
    };

    $scope.aceChanged = function(_editor) {
        $scope.data = $scope.editor.getSession().getValue();
    };
}]);