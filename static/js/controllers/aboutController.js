angular.module('myApp').controller('aboutController', ['$scope', 'aboutApi', function($scope, aboutApi) {
    $scope.authors = [];
    $scope.contributors = [];

    var parseTestData = function(data) {
        var results = [];
        var lines = data.split('\n');
        var re = new RegExp("^[^#].*");
        angular.forEach(lines, function(line) {
            var author_line = line.match(re);
            if (author_line) {
                var info = {name: null,  email: null};
                var name_and_email = author_line[0].split("<");
                if (name_and_email.length > 1) {
                    var name = name_and_email[0].trim();
                    var email = name_and_email[1].replace(/^<+|>+$/g,'');
                    info = {name: name,  email: email}
                } else {
                    info = {name: name_and_email[0],  email: null}
                }
                results.push(info)
            }
        });
        return results;
    };

    aboutApi.getAuthors().then(function(dataResponse) {
        $scope.authors = parseTestData(dataResponse.data);
    });

    aboutApi.getContributors().then(function(dataResponse) {
        $scope.contributors = parseTestData(dataResponse.data);
    });
}]);