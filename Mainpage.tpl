    <html>
    <meta charset="UTF-8">
    <head><title>Prices Paid</title></head>
    <body>
    <script src="../js/jquery-1.10.2.min.js"></script>
      <link rel="stylesheet" href="../SlickGrid-master/slick.grid.css" type="text/css"/>
      <link rel="stylesheet" href="../SlickGrid-master/css/smoothness/jquery-ui-1.8.16.custom.css" type="text/css"/>
      <link rel="stylesheet" href="../examples.css" type="text/css"/>


    <script src="../SlickGrid-master/lib/jquery-1.7.min.js"></script>
    <script src="../SlickGrid-master/lib/jquery.event.drag-2.2.js"></script>

    <script src="../SlickGrid-master/slick.core.js"></script>
    <script src="../SlickGrid-master/slick.editors.js"></script>
    <script src="../SlickGrid-master/slick.grid.js"></script>
    <!-- jqplot stuff -->
    
    <!--[if lt IE 9]><script language="javascript" type="text/javascript" src="excanvas.js"></script><![endif]-->
    <script language="javascript" type="text/javascript" src="../js/jquery.min.js"></script>
    <script language="javascript" type="text/javascript" src="../js/jquery.jqplot.min.js"></script>
    
    <link rel="stylesheet" type="text/css" href="../js/jquery.jqplot.css" />
    
    <script type="text/javascript" src="../js/plugins/jqplot.canvasTextRenderer.min.js"></script>
    <script type="text/javascript" src="../js/plugins/jqplot.canvasAxisLabelRenderer.min.js"></script>
    <script type="text/javascript" src="../js/plugins/jqplot.highlighter.min.js"></script>
    <script type="text/javascript" src="../js/plugins/jqplot.cursor.min.js"></script>
    <script type="text/javascript" src="../js/plugins/jqplot.bubbleRenderer.min.js"></script>

    <link rel="stylesheet" type="text/css" href="../js/jquery.jqplot.css" />    
<style type="text/css">
     .note {
        font-size: 0.8em;
    }
     #tooltip1b {
        font-size: 12px;
        color: rgb(15%, 15%, 15%);
        padding:2px;
        background-color: rgba(95%, 95%, 95%, 0.8);
    }
     #legendtable {
        font-size: 12px;
        border: 1px solid #cdcdcd;
        border-collapse: collapse;
    }
    #legendtable td, #legendtable th {
        font-size: 10px;
        border: 1px solid #cdcdcd;
        padding: 1px 4px;
    }
    </style>

<script>
alert("starting!");
alert("got data back");
var transactionData = [];
$.ajax({
      url: "api"
    }).done(function(dataFromSearch) {

    var i = 0;
    for (var key in dataFromSearch) {
        transactionData[i++] = dataFromSearch[key];
    }
    var grid;
    var transactionColumns = [
        {id: "contractingAgency", name: "Contracting Agency", field: "contractingAgency"},
        {id: "awardIdIdv", name: "Award ID/IDV", field: "awardIdIdv"},
        {id: "vendor", name: "Vendor", field: "vendor"},
        {id: "commodityType", name: "Commodity Type", field: "commodityType"},
        {id: "psc", name: "PSC", field: "psc"},
        {id: "modelNumberDescription", name: "Model Number Description", field: "modeberDescription"},
        {id: "modelNumberDescription2", name: "Model Number Description 2", field: "mNumberDescription2"},
        {id: "unitsOrdered", name: "Units Ordered", field: "unitsOrdered"},
        {id: "unitPrice", name: "Unit Price", field: "unitPrice"}
    ];
    var controlColumns = [ {id: "starred",name: "Starred", field: "starred" } ];
    
    var columns = controlColumns.concat(transactionColumns);
    var options = {
        editable: true,
        asyncEditorLoading: false,
        enableCellNavigation: true,
        enableColumnReorder: false
     };

     var data = [];
    transactionData.forEach(function (e,i,a) {
        var obj = e;
        e["starred"] = "";
        data[i] = obj;
    });
    
   function renderRow(label,content) {
     var row = "";
      row += "<tr>";
      row += "<td>";
      row += label;
      row += "</td>";
      row += "<td>";
      row += content;
      row += "</td>";
      row += "</tr>";
     return row;
    }
    
   function renderDetail(dataRow) {
      var html = "";
      html += "<table>";
      html += renderRow("Unit Price",dataRow.unitPrice);
      html += renderRow("Units Ordered",dataRow.unitsOrdered);
      html += renderRow("Model Number/Description",dataRow.modelNumberDescription);
      html += renderRow("Model Number/Description 2",dataRow.modelNumberDescription2);
      html += renderRow("Contracting Agency",dataRow.contractingAgency);
      html += renderRow("Award ID/IDV",dataRow.awardIdIdv);
       html += renderRow("PSC",dataRow.psc);
      html += "</table>";
      return html;
  }
    
  function renderStarredTransactionsInDetailArea() {
    var div = document.getElementById('detailArea');
    div.innerHTML = "";
    data.forEach(function (e) {
        if (e.starred == "Starred") {
        div.innerHTML += renderDetail(e);
        div.innerHTML += "<p></p>";
    }
    });
  }
  $(function () {
    grid = new Slick.Grid("#myGrid", transactionData, columns, options);
  grid.onClick.subscribe(function (e) {
      var cell = grid.getCellFromEvent(e);
      if (grid.getColumns()[cell.cell].id == "starred") {
        if (!grid.getEditorLock().commitCurrentEdit()) {
          return;
        }
        var states = { "": "Starred", "Starred": ""};
        data[cell.row].starred = states[data[cell.row].starred];
        grid.updateRow(cell.row);
        e.stopPropagation();
        renderStarredTransactionsInDetailArea();
      }
    });
  });

    
var plotData = [[]];
var i = 0;
var thingToPlot = data.forEach(function (e) {
  var newArray = [];
  // This is an attempt to make a bubble plot...
  newArray[0] = i++;
  newArray[1] = Math.ceil(e.unitPrice * 100) / 100;
  newArray[2] = Math.sqrt(e.unitsOrdered);
  newArray[3] = {
     label: e.vendor
  };
  plotData[0].push(newArray);
});
 var plot1b = $.jqplot('chartdiv', plotData, {
      title: 'Unit Prices',
      seriesDefaults:{
            renderer: $.jqplot.BubbleRenderer,
            rendererOptions: {
              bubbleAlpha: 0.6,
              highlightAlpha: 0.8,
              showLabels: false
            },
            shadow: true,
            shadowAlpha: 0.05
        },
      axes:{
        xaxis:{
          label: 'Number'
        },
        yaxis:{
          label: 'Dollars',
          tickOptions:{
            formatString:'$%.2f'
          }
        }
      },
      highlighter: {
        show: true,
        sizeAdjust: 7.5
      },
      cursor: {
        show: true,
        tooltipLocation:'sw'
      }
    }
      );

   // Legend is a simple table in the html.
  // Dynamically populate it with the labels from each data value.
  $.each(plotData[0], function(index, val) {
    $('#legendtable').append('<tr><td>'+val[3].label+'</td><td>'+val[1]+'</td></tr>');
  }
    );
    
     // Now bind function to the highlight event to show the tooltip
  // and highlight the row in the legend.
  $('#chartdiv').bind('jqplotDataHighlight',
    function (ev, seriesIndex, pointIndex, data, radius) {   
      var chart_left = $('#chartdiv').offset().left,
        chart_top = $('#chartdiv').offset().top,
        x = plot1b.axes.xaxis.u2p(data[0]),  // convert x axis unita to pixels
        y = plot1b.axes.yaxis.u2p(data[1]);  // convert y axis units to pixels
      var color = 'rgb(50%,50%,100%)';
      $('#tooltip1b').css({left:chart_left+x+radius+5, top:chart_top+y});
    
      $('#tooltip1b').html('<span style="font-size:14px;font-weight:bold;color: ' + color + ';">' + data[3] + '</span><br />' + 'x: ' + data[0] +
      '<br />' + 'y: ' + data[1] + '<br />' + 'r: ' + data[2]);
    
      $('#tooltip1b').show();
      $('#legendtable tr').css('background-color', '#ffffff');
      $('#legendtable tr').eq(pointIndex+1).css('background-color', color);
    });
   // Bind a function to the unhighlight event to clean up after highlighting.
  $('#chartdiv').bind('jqplotDataUnhighlight',
      function (ev, seriesIndex, pointIndex, data) {
          $('#tooltip1b').empty();
          $('#tooltip1b').hide();
          $('#legendtable tr').css('background-color', '#ffffff');
      });
});

</script>

<h2>You Searched for: {{search_string}}</h2>
 <h1> Prices Paid </h1>
<form action="/PricesPaid" method="get">
Text Search: <input type="text" name="search_string">  <br />
<input type="submit" value="Submit" />
</form>
<h3>
</h3>
  <div style="width:100%;">
<table>
  <tr>
    <td ><div id="chartdiv" style="width:65%;" ></div></td>
    <td ><div style="overflow:scroll;height:340px;width:35%;overflow:auto">
        <table id="legendtable";  >
          <tr><th>Vendor</th><th>Price</th></tr></tr></table></div></td>
          </tr>
        </table>
    </td>
 </tr>
</table>
</div>
 <div id="myGrid" style="width:100%;height:500px;"></div>
 <div id="detailArea">
</div>
<script>
</script>
</body>
</html>
