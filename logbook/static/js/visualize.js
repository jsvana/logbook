var getRequest = function(path, onSuccess, onError) {
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
  if (!window.flights) {
    return;
  }

  var selected = document.querySelectorAll('select[name="axis"] option:checked');
  var axes = Array.from(selected).map((el) => el.value);
  var cumulative = document.querySelector('#cumulative_true').checked;

  var lines = [];
  for (var a in axes) {
    var axis = axes[a];
    var line = {
      x: [],
      y: [],
      type: 'scatter',
      name: axis,
    };

    var total = 0;
    for (var f in window.flights) {
      line.x.push(window.flights[f].date);
      var value = window.flights[f][axis];
      if (cumulative) {
        total += value;
        value = total;
      }
      line.y.push(value);
    }
    lines.push(line);
  }

  var layout = {
    title: 'Logbook Data',
    xaxis: {
      title: 'Date',
      showgrid: false,
      zeroline: false,
    },
    yaxis: {
      title: 'Hours',
      showline: false,
    },
  };

  Plotly.newPlot('graph', lines, layout);
};

getRequest(
  '/flights',
  function(data) {
    window.flights = data;
  },
);

var getLatLong = function(airport, onSuccess, onFailure) {
  getRequest(
    '/airport/' + airport,
    onSuccess,
    function(xhr) {
      onFailure(airport, xhr);
    },
  );
};

var getAllAirports = function(airports, onSuccess) {
  var counter = 0;
  for (var a in airports) {
    airports[a] = airports[a].toUpperCase();
  }
  var uniqueAirports = Array.from(new Set(airports));
  var failedAirports = [];
  var airportData = {};
  console.log(uniqueAirports);
  for (var i in uniqueAirports) {
    getLatLong(
      uniqueAirports[i],
      function(data) {
        airportData[data.icao] = data;
        counter++;
        if (counter === uniqueAirports.length) {
          onSuccess(airportData);
        }
      },
      function(airport, xhr) {
        failedAirports.push(airport);
        console.log('failed ' + airport);
        counter++;
        if (counter === uniqueAirports.length) {
          onSuccess(airportData);
        }
      },
    );
  }
};

var mapFlights = function(flights, airports) {
  var data = [];

  for (var f in flights) {
    flight = flights[f];
    var from = airports[flight._from];
    var to = airports[flight.to];

    if (!from || !to) {
      console.log('Skipping ' + flight._from + ' to ' + flight.to);
      continue;
    }

    var startLat = from.x;
    var startLong = from.y;
    var endLat = to.x;
    var endLong = to.y;

    var result = {
      type: 'scattergeo',
      locationmode: 'USA-states',
      lon: [startLong, endLong],
      lat: [startLat, endLat],
      mode: 'lines',
      line: {
        width: 1,
        color: 'red'
      },
      opacity: 1,
    };
    data.push(result);
  }

  var layout = {
    title: 'asdf',
    showlegend: false,
    geo:{
      scope: 'north america',
      projection: {
        type: 'azimuthal equal area'
      },
      showland: true,
      landcolor: 'rgb(243,243,243)',
      countrycolor: 'rgb(204,204,204)'
    }
  };

  Plotly.plot('map', data, layout, {showLink: false});
};

redraw();
