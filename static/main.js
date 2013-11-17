/*
Copyright 2013 The Font Bakery Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.

http://github.com/xen/fontbakery/

*/

$(document).delegate('.toggle', 'click', function () {
  event.stopPropagation();
  $(this).next().slideToggle();
  $(this).children().toggleClass("icon-collapse").toggleClass("icon-expand");
});

$(document).ready(function() {

$('.toggle').children().addClass("icon-collapse");
$('.toggleCollapseFirst').next().hide();
$('.toggleCollapseFirst').children().addClass("icon-expand").removeClass("icon-collapse");;

$(".tablesorter").tablesorter();

$("[rel='tooltip']").tooltip();

var dataConfirmModalHtml = '<div id="dataConfirmModal" class="modal" role="dialog" aria-labelledby="dataConfirmLabel" aria-hidden="true"><div class="modal-header"><h3 id="dataConfirmLabel">Are you sure?</h3></div><div class="modal-body"></div><div class="modal-footer"><button class="btn pull-left" data-dismiss="modal" aria-hidden="true">Cancel</button><a class="btn btn-success" id="dataConfirmYes">Yes</a><a class="btn btn-danger" data-dismiss="modal">No</a></div></div>'

// Confirm Modal used to confirm license/name permissions
$('a[data-confirm]').click(function(ev) {
    var href = $(this).attr('href');
    if (!$('#dataConfirmModal').length) {
        $('body').append(dataConfirmModalHtml);
    }
    $('#dataConfirmModal').find('.modal-body').text($(this).attr('data-confirm'));
    $('#dataConfirmYes').attr('href', href);
    $('#dataConfirmModal').modal({show:true});
    return false;
});

$('button[data-confirm]').click(function(ev) {
  var form = $(this).closest('form');
  if (!$('#dataConfirmModal').length) {
        $('body').append(dataConfirmModalHtml);
  }
  $('#dataConfirmModal').find('.modal-body').text($(this).attr('data-confirm'));
  $('#dataConfirmYes').click(function(ev){form.submit();});
  $('#dataConfirmModal').modal({show:true});
  return false;
});

// #notify is in navbar, showing worker state
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
    $('#notify').removeClass();
    $('#notify').addClass('icon-circle text-success');
    socket.emit('status', true);
    $('#notify').popover('hide')
});

socket.on("disconnect", function(e) {
    $('#notify').removeClass();
    $('#notify').addClass('icon-circle muted');
});

socket.on('gone', function (data) {
    $('#notify').removeClass();
    $('#notify').addClass('icon-warning-sign text-error');
    $('#notify').popover('show');
    // TODO add a wait() here then hide it after a second
});

socket.on('start', function (data) {
    $('#notify').removeClass();
    $('#notify').addClass('icon-refresh icon-spin text-success');
    $('#notify').popover('hide');
});

socket.on('stop', function (data) {
    $('#notify').removeClass();
    $('#notify').addClass('icon-circle text-success');
    $('#notify').popover('hide');
});

// apopover class used on dashboard
$('.apopover').each(function (index, item) {
    $(item).popover();
});

// mother* classes used on filestree() trees
$('.mothership').click(function(){
  $(this).children('ul').slideToggle();
});
$('.mother_of_glyphs').click(function(){
  event.stopPropagation();
  $(this).children('ul').slideToggle();
});

});

