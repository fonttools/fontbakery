(function() {
  var app = angular.module('FBDashboard', []);

  app.controller('FontListController', ['$http', function($http){
    var FListCtrl = this;
    $http.get('json/dashboard_config.json').success(function(data){
      FListCtrl.families = [];
      for (t in data["targets"]){
        var target = data["targets"][t];
        var family = {};
        family.url = target;
        family.name = target.split("/").pop().split(".")[0];
        family.num_checks = 100;
        family.num_passed = null;
        FListCtrl.families.push(family);
      };
    });

    this.load_progress = function(family){
      function get_newest_entry(f){
        var ret_val = null;
        for (var e in f["entries"]){
          var entry = f["entries"][e];
          var this_date = Date.parse(entry["date"]);
          if (ret_val == null || this_date > most_recent){
            most_recent = this_date;
            ret_val = entry;
          }
        }
        return ret_val;
      }

      $http.get(family.url).success(function(json_data){
        var num_passed = 0,
            num_checks = 0;
        for (var file in json_data){
          var summary = get_newest_entry(json_data[file])["summary"];
          num_passed += summary["Passed"];
          num_checks += summary["Passed"] +
                        summary["Errors"] +
                        summary["Hotfixes"] +
                        summary["Warnings"] +
                        summary["Skipped"];
        }
        family.num_passed = num_passed;
        family.num_checks = num_checks;
        family.percentage = (100.0 * num_passed / num_checks).toFixed(2);
      });
    };

    this.load_details = function(url){
      $http.get(url).success(function(json_data){
        FListCtrl.details = json_data;
      });
/*
        var chart_lines = [],
            familyname = null;
        let stats = [];
        for (var f in json_data){
          if (f != "CrossFamilyChecks")
            familyname = f.split("-")[0];
          var font_data = json_data[f],
              data = [],
              min_date = null,
              max_date = null,
              max_percent = 0;

          //We expect the first entry to be the latest one:
          stats.push(font_data["entries"][0]["summary"]);

          for (var e in font_data["entries"]){
            var entry = font_data["entries"][e],
                s = entry["summary"],
                total = s["Errors"] + s["Hotfixes"] + s["Passed"] + s["Skipped"] + s["Warnings"],
                error_percent = (100.0 * s["Errors"]) / total,
                _date = Date.parse(entry["date"]);

            if (error_percent < max_percent)
              max_percent = error_percent;
            if ((min_date == null) || _date < min_date)
              min_date = _date;
            if ((max_date == null) || _date > max_date)
              max_date = _date;

            data.push({
              "Errors": error_percent,
              "date": entry["date"]});
            }
            chart_lines.push(data);
          }
          InitChart(stats, familyname, chart_lines, min_date, max_date, max_percent);
        });
      }
*/
    };
  }]);
})();

/*
var cur_color = 0;
function random_color(){
  var color_names = ['green', 'blue', 'red', 'magenta', 'grey', 'black', 'cyan', 'green'];
  cur_color++;
  if (cur_color > 8) cur_color = 0;
  return color_names[cur_color];
}

function InitChart(stats, familyname, data, mindate, maxdate, max_percent) {
    var font_div = $("<div></div>")
      .text(familyname)
      .click(function(){
        RenderChart(familyname, data, mindate, maxdate, max_percent);
      });
    $("#fontlist").append(font_div);
}

function RenderChart(familyname, data, mindate, maxdate, max_percent) {
  $("#visualisation").empty();
  var WIDTH = 1000,
      HEIGHT = 500,
      MARGINS = {
        top: 20,
        right: 20,
        bottom: 20,
        left: 50
      },
      vis = d3.select("#visualisation")
              .attr("width", WIDTH + MARGINS.left + MARGINS.right)
              .attr("height", HEIGHT + MARGINS.top + MARGINS.bottom)
              .append("g")
              .attr("transform",
                    "translate(" + MARGINS.left + "," + MARGINS.top + ")"),
      xScale = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right]).domain([mindate, maxdate]),
      yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([0, Math.min(100, max_percent+30)]),
      xAxis = d3.svg.axis().scale(xScale),
      yAxis = d3.svg.axis().scale(yScale).orient("left");

      vis.append("text")
        .attr("x", (WIDTH / 2))             
        .attr("y", 0 + (MARGINS.top))
        .attr("text-anchor", "middle")  
        .style("font-size", "24px") 
        .text(familyname);

//      focus = vis.append("g")
//                 .attr("class", "focus")
//                 .style("display", "block");
//      focus.append("circle").attr("r", 7.5);
      vis.append("svg:g")
         .attr("class", "x axis")
         .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
         .call(xAxis);

      vis.append("svg:g")
         .attr("class", "y axis")
         .attr("transform", "translate(" + (MARGINS.left) + ",0)")
         .call(yAxis);
      lineGen = d3.svg.line()
                      .x(function(d) {
                        return xScale(Date.parse(d.date));
                      })
                      .y(function(d) {
                        return yScale(d.Errors);
                      })
                      .interpolate("basis");
  for (var d in data){
    vis.append('svg:path')
       .attr('d', lineGen(data[d]))
       .attr('stroke', random_color())
       .attr('stroke-width', 2)
       .attr('fill', 'none');
  }
}

$(document).ready(function(){
  var targets = [
    "json/burndown_samples/Cabin.burndown.json", //GREAT!
    "json/burndown_samples/chonburi.burndown.json",
    "json/burndown_samples/QuicksandFamily.burndown.json",
    "json/burndown_samples/sarala.burndown.json",
//  "json/burndown_samples/Alike.burndown.json", //weird loop
    "json/burndown_samples/poiretone.burndown.json",
    "json/burndown_samples/Varela-Round-Hebrew.burndown.json"
  ];

  
  for (var t in targets){
    $.getJSON(targets[t], function(json_data){
    var chart_lines = [],
        familyname = null;
    let stats = [];
    for (var f in json_data){
      if (f != "CrossFamilyChecks")
        familyname = f.split("-")[0];
      var font_data = json_data[f],
          data = [],
          min_date = null,
          max_date = null,
          max_percent = 0;

      //We expect the first entry to be the latest one:
      stats.push(font_data["entries"][0]["summary"]);

      for (var e in font_data["entries"]){
        var entry = font_data["entries"][e],
            s = entry["summary"],
            total = s["Errors"] + s["Hotfixes"] + s["Passed"] + s["Skipped"] + s["Warnings"],
            error_percent = (100.0 * s["Errors"]) / total,
            _date = Date.parse(entry["date"]);

        if (error_percent < max_percent)
          max_percent = error_percent;
        if ((min_date == null) || _date < min_date)
          min_date = _date;
        if ((max_date == null) || _date > max_date)
          max_date = _date;

        data.push({
          "Errors": error_percent,
          "date": entry["date"]});
        }
        chart_lines.push(data);
      }
      InitChart(stats, familyname, chart_lines, min_date, max_date, max_percent);
    });
  }
});

*/
