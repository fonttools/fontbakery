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

$("#notify").popover({
	title: "Worker is not running!",
	content: "Run 'make worker' to start it",
	trigger: 'click',
	placement: 'bottom'
});

io.transports = ["websocket", "xhr-polling", "jsonp-polling"];
var socket = io.connect("/status", {'force new connection': true});
window.buildsocket = socket;

socket.on("connect", function(e) {
    $notify.removeClass();
    $notify.addClass('icon-circle text-success');
    socket.emit('status', true);
    $('#notify').popover('hide')
});

socket.on("disconnect", function(e) {
    $notify.removeClass();
    $notify.addClass('icon-circle muted');
});

socket.on('gone', function (data) {
    $notify.removeClass();
    $notify.addClass('icon-warning-sign text-error');
    $('#notify').popover('show')
});


socket.on('start', function (data) {
    $notify.removeClass();
    $notify.addClass('icon-refresh icon-spin text-success');
    $('#notify').popover('hide')
});

socket.on('stop', function (data) {
    $notify.removeClass();
    $notify.addClass('icon-circle text-success');
    $('#notify').popover('hide')
});

});
