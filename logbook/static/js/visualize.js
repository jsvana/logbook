var makeRequest = function(path, onSuccess, onError) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', path);
  xhr.onload = function() {
    if (xhr.status === 200) {
      onSuccess(JSON.parse(xhr.responseText));
    } else {
      if (onError) {
        onError(xhr);
      }
    }
  };
  xhr.send();
};

var redraw = function() {
  var axis = document.querySelector('select[name="axis"]').value;
  var cumulative = document.querySelector('#cumulative_true').checked;

  makeRequest(
    '/flights',
    function(data) {
      var graphData = {
        x: [],
        y: [],
        type: 'scatter',
      };
      console.log(cumulative);

      var total = 0;
      for (var f in data) {
        graphData.x.push(data[f].date);
        var value = data[f][axis];
        if (cumulative) {
          total += value;
          value = total;
        }
        graphData.y.push(value);
      }

      Plotly.newPlot('graph', [graphData]);
    },
  );
};

redraw();
