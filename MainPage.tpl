    <html>
<head>
    <meta charset="UTF-8">
    <title>Prices Paid v. 0.1</title></head>
    <body>
<form action="/PricesPaid" method="post">
Text Search: <input type="text" name="search_string">  <br />
<input type="submit" value="Search" />
<input type="hidden" name="user" value="contractofficer" />
<input type="hidden" name="password" value="savegovmoney" />
</form>

<span class="majorlabel">You Searched for: {{search_string}}</span>
<span>Number returned:</span>
<span id="placeForNumberReturned"></span>

  
<div id="chartContainer">
    <section id="chartdiv" ></section>
    <section id="legenddiv" >
    <table id="legendtable">
       <tr><th>Vendor</th><th>Price</th></tr>
    </table>
</section>
</div>

 <div id="myGrid" style="width:100%;height:500px;"></div>
 <div id="detailArea">
</div>
    <script src="../js/jquery-1.10.2.min.js"></script>
      <link rel="stylesheet" href="../SlickGrid-master/slick.grid.css" type="text/css"/>
      <link rel="stylesheet" href="../SlickGrid-master/css/smoothness/jquery-ui-1.8.16.custom.css" type="text/css"/>
      <link rel="stylesheet" href="css/examples.css" type="text/css"/>


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
    .majorlabel {
        font-size: large;
        margin-right: 5%;
     }
     #tooltip1b {
        font-size: 12px;
        color: rgb(15%, 15%, 15%);
        padding:2px;
        background-color: rgba(95%, 95%, 95%, 0.8);
    }
    #legendtable td, #legendtable th {
        font-size: 10px;
        border: 1px solid #cdcdcd;
        padding: 1px 4px;
    }
    #chartcontainer {
       position: relative;
       width: 100%;
       height: 300px;
     }
     #legenddiv {
        height: 100%;
        position: absolute;
        margin-left: 70%;
        width: 30%;
        overflow: auto;
        height: 250px;
     }
     #legendtable {
        font-size: 12px;
        border: 1px solid #cdcdcd;
        border-collapse: collapse;
     }
    #chartdiv {
      position: absolute;
      width: 65%;
     }
    </style>

<script>
var transactionData = [];


function processAjaxSearch(dataFromSearch) {

    var i = 0;
    for (var key in dataFromSearch) {
        transactionData[i++] = dataFromSearch[key];
    }

    var numberDiv = document.getElementById('placeForNumberReturned');
    numberDiv.innerHTML = i;

// Now I'm going to try something weird, which seems justified by the nature 
// of our data--I'm only going to plot the lowest-prices 80%.  The upper 
// 20% is often something not really in the data set you are looking at 
// and it messes up the plot.  This should really be under the control 
// of the user, but that will have to wait.
// In order to do this we will sort on unitPrice, which is probably 
// a good way to present the data anyway.
transactionData.sort(
   function (a,b) {
      var ret;
      if (parseFloat(a["unitPrice"]) < parseFloat(b["unitPrice"])) {
	     ret = 1;
      } else if (parseFloat(a["unitPrice"]) > parseFloat(b["unitPrice"])) {
             ret = -1;
      } else {
             ret = 0;
      }
    return ret;
});

var sumOfUnitPrice = 0.0;
transactionData.forEach(function(d) { 
  var x = parseFloat(d["unitPrice"]);
  if (!isNaN(x))
    sumOfUnitPrice += x 
});

function medianSortedValues(values) {
 var half = Math.floor(values.length/2);
if(values.length % 2)
return parseFloat(values[half]["unitPrice"]);
else
return (parseFloat(values[half-1]["unitPrice"]) + 
        parseFloat(values[half]["unitPrice"])) / 2.0;
}

var medianUnitPrice = medianSortedValues(transactionData);

    var grid;
    var transactionColumns = [
        {id: "unitPrice", name: "Unit Price", field: "unitPrice", width: 100},
        {id: "unitsOrdered", name: "Units Ordered", field: "unitsOrdered", width: 60},
        {id: "vendor", name: "Vendor", field: "vendor", width: 200},
        {id: "productDescription", name: "Product Description", field: "productDescription", width: 400},
        {id: "contractingAgency", name: "Contracting Agency", field: "contractingAgency",
width: 200},
        {id: "awardIdIdv", name: "Award ID/IDV", field: "awardIdIdv", width: 100},
        {id: "commodityType", name: "Commodity Type", field: "commodityType", width: 100},
        {id: "psc", name: "PSC", field: "psc", width: 80}
    ];
    var controlColumns = [ {id: "starred",name: "Starred", field: "starred",width: 40 } ];
    
    var columns = controlColumns.concat(transactionColumns);

// Now I attempt to make every column sortable
   columns.forEach(function (c) {
           c.sortable = true;
});    

    var options = {
        editable: true,
        asyncEditorLoading: false,
        enableCellNavigation: true,
        enableColumnReorder: false,
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
// These strings really need to transferred to the server
// In order for us to have proper abstraction and language translation    
   function renderDetail(dataRow) {
      var html = "";
      html += "<table>";
      html += renderRow("Unit Price",dataRow.unitPrice);
      html += renderRow("Units Ordered",dataRow.unitsOrdered);
      html += renderRow("Product Description",dataRow.productDescription);
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

  // Define function used to get the data and sort it.
  function getItem(index) {
    return transactionData[index];
//    return isAsc ? data[indices[currentSortCol.id][index]] : data[indices[currentSortCol.id][(data.length - 1) - index]];
  }
  function getLength() {
    return transactionData.length;
  }

  $(function () {
    grid = new Slick.Grid("#myGrid", transactionData, columns, options);

// There's got to be a way to make this more compact!!!
    grid.onSort.subscribe(function (e, args) {
      var currentSortCol = args.sortCol;
      var isAsc = args.sortAsc;
      currentSortCol = args.sortCol.field;
      var stringSort = function(a,b) {
         var ret;
         if (a[currentSortCol] < b[currentSortCol]) {
	     ret = 1;
         } else if (a[currentSortCol] > b[currentSortCol]) {
             ret = -1;
         } else {
             ret = 0;
         }
         if (!isAsc) 
	     return -1*ret;
         else 
	     return ret;
      }
      var numberSort = function(a,b) {
         var ret;
         if (parseFloat(a[currentSortCol]) < parseFloat(b[currentSortCol])) {
	     ret = 1;
         } else if (parseFloat(a[currentSortCol]) > parseFloat(b[currentSortCol])) {
             ret = -1;
         } else {
             ret = 0;
         }
         if (!isAsc) 
	     return -1*ret;
         else 
	     return ret;
      }

      transactionData.sort(currentSortCol == "unitPrice" || currentSortCol == "unitsOrdered" ? numberSort : stringSort);

      grid.setData(transactionData);
      grid.invalidateAllRows();
      grid.render();
    });
  });

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

var plotData = [[]];
var i = 0;
var thingToPlot = data.forEach(function (e) {
// we don't want to plot it if it is more than 4 times the median price, 
// as it is probably erroneous

  if (e.unitPrice < (medianUnitPrice * 4.0)) {

    var newArray = [];

    newArray[0] = i++;
    newArray[1] = Math.ceil(e.unitPrice * 100) / 100;
    newArray[2] = Math.sqrt(Math.abs(e.unitsOrdered));
    newArray[3] = {
       label: e.vendor
    };
    plotData[0].push(newArray);
  }
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
}

$.post("api",
  { search_string: '{{search_string}}',
    user: '{{user}}',
    password: '{{password}}'
  },
  processAjaxSearch
);


</script>

</body>

</html>
