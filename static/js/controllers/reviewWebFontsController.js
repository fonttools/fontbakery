myApp.controller('reviewWebFontsController', ['$scope', '$http', 'reviewApi', function($scope, $http, reviewApi) {
    $scope.missing_chars_hidden = false;
    $scope.dataLoaded = false;
    $scope.toggleMissingGlyphs = function() {
        try {
            var glyphSpans = document.getElementById("glyphContainer").getElementsByTagName("span");
            for(var i=0; i < glyphSpans.length; i++) {
                var glyphSpan = glyphSpans[i];
                if(glyphSpan.getAttribute("class") == "missing-glyph") {
                    var parent_div = angular.element(glyphSpan.parentNode).parent();

                    if(glyphSpan.parentNode.style.display == "none") {

                        if (parent_div[0].style.display == "none") {
                            parent_div[0].style.display = "block";
                        }

                        glyphSpan.parentNode.style.display = "block";
                    } else {

                        if (parent_div[0].style.display == "block") {
                            parent_div[0].style.display = "none";
                        }

                        glyphSpan.parentNode.style.display = "none";
                    }
                }
            }
            $scope.missing_chars_hidden = !$scope.missing_chars_hidden;
        } catch(e){}
    };

    $scope.updateParentStyle = function(val) {
        return val ? 'none' : 'block'
    };

    reviewApi.getOrthography().then(function(response) {
        var orthography = response.data;
        $scope.dataLoaded = true;
        $scope.glyphs = [];
        angular.forEach(orthography, function(font) {
            angular.forEach(font.glyphs, function(glyph) {
                $scope.glyphs.push({
                    'glyph': glyph,
                    'is_missing': font.missing_glyphs.indexOf(glyph) != -1
                })
            });
        });
    });
}]);
