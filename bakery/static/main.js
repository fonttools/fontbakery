$(document).ready(function() {
    $("#searchfield").typeahead({
        minLength: 3,
        source: function(query, process) {
            $.post('/quicksearch', { q: query, limit: 8 }, function(data) {
                process(JSON.parse(data));
            });
        },
        updater: function (item) {
            document.location = "/" +item;
            return item;
        }
    });
});