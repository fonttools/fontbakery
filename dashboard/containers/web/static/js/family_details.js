google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(draw_pie_chart);

function draw_pie_chart() {
  var pie_data = google.visualization.arrayToDataTable(_chart_data);
  var pie_chart = new google.visualization.PieChart(document.getElementById('piechart'));
  pie_chart.draw(pie_data, {title: _chart_title});
}

function init(){
  var msg_colouring = {
    "ERROR": "#C22",
    "WARNING": "#22C",
    "SKIP": "#AA4",
    "INFO": "#AAF"
  };
  for (var log_type in msg_colouring){
    $('table tr td:first-child').filter(function() {
      return $(this).text().indexOf(log_type) === 0;
    }).parent().css("color", msg_colouring[log_type]);
  }

  $("#tabs").tabs().show();
}
