// $(document).ready(function() {
//     $("#searchfield").typeahead({
//         minLength: 2,
//         source: function(query, process) {
//             $.post('/quicksearch', { q: query, limit: 8 }, function(data) {
//                 process(JSON.parse(data));
//             });
//         },
//         updater: function (item) {
//             document.location = "/" +item;
//             return item;
//         },
//         matcher: function (item) {
//             return true;
//         }
//     });
// });

$(document).ready(function() {
    $('a[data-confirm]').click(function(ev) {
        var href = $(this).attr('href');
        if (!$('#dataConfirmModal').length) {
            $('body').append('<div id="dataConfirmModal" class="modal" role="dialog" aria-labelledby="dataConfirmLabel" aria-hidden="true"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button><h3 id="dataConfirmLabel">Please Confirm</h3></div><div class="modal-body"></div><div class="modal-footer"><button class="btn" data-dismiss="modal" aria-hidden="true">Cancel</button><a class="btn btn-primary" id="dataConfirmOK">OK</a></div></div>');
        } 
        $('#dataConfirmModal').find('.modal-body').text($(this).attr('data-confirm'));
        $('#dataConfirmOK').attr('href', href);
        $('#dataConfirmModal').modal({show:true});
        return false;
    });
});

$(document).ready(function () {

var $notify = $('#notify');
io.transports = ["websocket", "xhr-polling", "jsonp-polling"];
var socket = io.connect("/build");
window.buildsocket = socket;

socket.emit('hello', 'Browser'); 

socket.on("connect", function(e) {
    console.log("Connected", arguments);
});

socket.on("disconnect", function(e) {
    console.log("Disconnected", arguments);
});

socket.on('ping', function (data) {
    $('#notify').addClass('text-success');
    $('#notify').addClass('icon-spin');
    
    $('#notify').removeClass('muted');
    console.log(data);
    console.log(arguments);
});


socket.on('start', function (data) {
    $('#notify').addClass('text-success');
    $('#notify').removeClass('muted');
    console.log(data);
    console.log(arguments);
});

socket.on('stop', function (data) {
    $('#notify').removeClass('text-success');
    $('#notify').addClass('muted');
    console.log(data);
    console.log(arguments);
});

});
