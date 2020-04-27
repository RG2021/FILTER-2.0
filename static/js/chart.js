google.load("visualization", "1", {packages:["corechart"]});
google.charts.load('current', {'packages':['bar']});
google.setOnLoadCallback(drawChart1);
function drawChart1() {

  var divdata1 = document.getElementById('chart_div1');
  var ratingdata = divdata1.getAttribute('data-reviews1');
  var ratingdata = google.visualization.arrayToDataTable(JSON.parse(ratingdata));

  var options1 = {
    title: 'Ratings Count',
    hAxis: {title: 'Rating', titleTextStyle: {color: 'black'}},
    height: 400,
};

  var ratingchart = new google.visualization.ColumnChart(document.getElementById('chart_div1'));
  ratingchart.draw(ratingdata, options1);

  var divdata2 = document.getElementById('chart_div2');
  var tagdata = divdata2.getAttribute('data-reviews2');
  var tagdata = google.visualization.arrayToDataTable(JSON.parse(tagdata))

  var options2 = {
    title: 'Categories Rating',
    hAxis: {title: 'Count', titleTextStyle: {color: 'black'}},
    bars: 'horizontal',
    height: 400,
};

  var tagchart = new google.charts.Bar(document.getElementById('chart_div2'));
  tagchart.draw(tagdata, google.charts.Bar.convertOptions(options2));


}
