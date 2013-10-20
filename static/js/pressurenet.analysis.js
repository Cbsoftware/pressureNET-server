(function() {
    
    var global = this;

    var PressureNET = (global.PressureNET || (global.PressureNET = {}));

    var readingsUrl = '';

    var defaultQueryLimit = 20000;
    //var largeQueryIncrement = 10000;
    
    var map;
    
    var currentQueryLimit = defaultQueryLimit;

    PressureNET.initialize = function(config) {
        readingsUrl = config.readingsUrl;

        $(function() {
            $("#start_date").datepicker({changeMonth: true,dateFormat: "yy/mm/dd" });
            $("#end_date").datepicker({changeMonth: true,dateFormat: "yy/mm/dd"});
            PressureNET.initializeMap();

            // if there are query parameters, use them
            PressureNET.setDates(new Date(((new Date()).getTime() - (2*86400000))), new Date(((new Date()).getTime() + 86400000)));
            PressureNET.getLocation();
        });
    }

    PressureNET.loadMapWithUserLocation = function(position) {
        var latitude = position.coords.latitude;
        var longitude = position.coords.longitude;
        PressureNET.setMapPosition(latitude, longitude, 13, ((new Date()).getTime() - 86400000), ((new Date()).getTime() + 86400000));
    }
    
    PressureNET.getLocation = function() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(PressureNET.loadMapWithUserLocation);
        }
    }

    PressureNET.getUrlVars = function() {
        var vars = {};
        var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
          vars[key] = value;
        });
        return vars;
    }

    PressureNET.setMapPosition = function(latitude, longitude, zoomLevel, start_time, end_time) {
        PressureNET.setDates(new Date(start_time), new Date(end_time));
        map.setZoom(zoomLevel);
        var latLng = new google.maps.LatLng(latitude, longitude); //Makes a latlng
        map.panTo(latLng);
        PressureNET.loadAndUpdate();
    }    

    PressureNET.dateRange = function() {
        var start = new Date($('#start_date').val());
        var end = new Date($('#end_date').val());

        // end - start returns difference in milliseconds 
        var diff = end - start;
        
        // get days
        var days = diff/1000/60/60/24;
        return days;
    }
     
    PressureNET.setDates = function(start, end) {
        $('#start_date').datepicker('setDate',start);
        $('#end_date').datepicker('setDate',end);
        $('#start_date').val($.datepicker.formatDate('yy/mm/dd', start));
        $('#end_date').val($.datepicker.formatDate('yy/mm/dd', end));
    }

    PressureNET.loadAndUpdate = function(increment) {
        if(increment>0) {
            currentQueryLimit += defaultQueryIncrement;
        } else {
            currentQueryLimit = defaultQueryLimit;
        }

        $('#placeholder').html('');
        $("#query_results").html("Loading...");
        
        //start_time = $('#start_date').datepicker('getDate').getTime();
        //end_time = $('#end_date').datepicker('getDate').getTime();
        end_time = new Date().getTime(); 
        start_time = end_time - 3600000;
        
        var query_params = {
            format: 'json',
            //min_latitude: min_latitude,
            //max_latitude: max_latitude,
            //min_longitude: min_longitude,
            //max_longitude: max_longitude,
            start_time: start_time,
            end_time: end_time,
            limit: 100000 //currentQueryLimit
        };

        $.ajax({
            url: readingsUrl,
            data: query_params,
            dataType: 'json',
            success: function(readings, status) {
                var heatmap_bins = {};

                $(readings).each(function (index, reading) {
                    if (reading.reading < 700) {
                        return;
                    }
                    var latitude_bin = Math.round(reading.latitude);
                    var longitude_bin = Math.round(reading.longitude);

                    var bin_key = String(latitude_bin) + ',' + String(longitude_bin);

                    if (heatmap_bins[bin_key]) {
                        heatmap_bins[bin_key].readings.push(reading);
                    } else {
                        heatmap_bins[bin_key] = {
                            latitude: latitude_bin + 0.5,
                            longitude: longitude_bin + 0.5,
                            readings: [reading]
                        };
                    }
                });
               
                for (var bin_key in heatmap_bins) {
                    var bin_readings = heatmap_bins[bin_key].readings;
                    var bin_sum = 0.0;

                    $(bin_readings).each(function (index, bin_reading) {
                        bin_sum += bin_reading.reading; 
                    });

                    heatmap_bins[bin_key].average = bin_sum/bin_readings.length;

                }

                var min_pressure = 1000.0;
                var max_pressure = 1000.0;

                for (var bin_key in heatmap_bins) {
                    var bin_average = heatmap_bins[bin_key].average
                    min_pressure = Math.min(min_pressure, bin_average);
                    max_pressure = Math.max(max_pressure, bin_average);
                }

                var pressure_range = max_pressure - min_pressure;

                for (var bin_key in heatmap_bins) {
                    var bin_latitude = heatmap_bins[bin_key].latitude;
                    var bin_longitude = heatmap_bins[bin_key].longitude;
                    var position = new google.maps.LatLng(bin_latitude, bin_longitude)

                    var normalized_pressure = (heatmap_bins[bin_key].average - min_pressure) / pressure_range;

                    var green_value = Math.round(normalized_pressure * 255).toString(16);
                    var red_value = Math.round((1 - normalized_pressure) * 255).toString(16);
                    
                    //heatmap_points.push({
                    //    location: position,
                    //    weight: bin_average
                    //});

                    var populationOptions = {
                      map: map,
                      strokeWeight: 0,
                      fillColor: '#' + red_value + green_value + '00',
                      fillOpacity: 0.35,
                      bounds: new google.maps.LatLngBounds(
                          new google.maps.LatLng(bin_latitude, bin_longitude),
                          new google.maps.LatLng(bin_latitude + 1.0, bin_longitude + 1.0)
                      )
                    };
                    
                    // Add the circle for this city to the map.
                    new google.maps.Rectangle(populationOptions);
                }

                //var heatmap = new google.maps.visualization.HeatmapLayer({
                //    data: heatmap_points,
                //    dissipating: true,
                //    radius: 200,
                //    opacity: 0.5
                //});
                //
                //heatmap.setMap(map);
            }
        });
    }

    PressureNET.initializeMap = function() {
        var mapOptions = {
          zoom: 4,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);

        var weatherLayer = new google.maps.weather.WeatherLayer({
          temperatureUnits: google.maps.weather.TemperatureUnit.CELSIUS
        });
        weatherLayer.setMap(map);

        var cloudLayer = new google.maps.weather.CloudLayer();
        cloudLayer.setMap(map);
    }

}).call(this);
