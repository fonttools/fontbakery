define([
], function(
) {
    "use strict";
    var setup = {
        baseUrl: 'js'
      , paths: {
            'marked': 'bower_components/marked/marked.min'
          , 'opentype': 'bower_components/opentype.js/dist/opentype'
        }
    };
    require.config(setup);
    return require;
});
