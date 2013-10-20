(function() {

    var global = this;

    var PressureNET = (global.PressureNET || (global.PressureNET = {}));

    // Globals
    PressureNET.readings_url = '';
    PressureNET.map = null;
    PressureNET.geohash_key_length = 3;
    PressureNET.heatmap_bins = {};
    PressureNET.gradient = new Rainbow();
    PressureNET.gradient.setSpectrum('#FF0000', '#0000FF', '#00FF00');

    var reading_marker_colour = 'FF0000';
    PressureNET.reading_marker_image = new google.maps.MarkerImage(
        'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|' + reading_marker_colour,
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34)
    );

    var bin_marker_colour = '0000FF';
    PressureNET.bin_marker_image = new google.maps.MarkerImage(
        'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|' + bin_marker_colour,
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34)
    );

    // Initialization
    PressureNET.initialize = function(config) {
        PressureNET.readings_url = config.readings_url;

        PressureNET.init_map();
        PressureNET.get_location();
        PressureNET.load_data();
    }

    PressureNET.init_map = function() {
        var map_options = {
            mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        PressureNET.map = new google.maps.Map(document.getElementById('map_canvas'), map_options);

        var weatherLayer = new google.maps.weather.WeatherLayer({
          temperatureUnits: google.maps.weather.TemperatureUnit.CELSIUS
        });
        weatherLayer.setMap(PressureNET.map);

        var cloudLayer = new google.maps.weather.CloudLayer();
        cloudLayer.setMap(PressureNET.map);
    }

    PressureNET.get_location = function() {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(function (position) {
                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;
                PressureNET.set_map_position(latitude, longitude, 10);
            });
        }
    }

    PressureNET.set_map_position = function(latitude, longitude, zoom_level) {
        PressureNET.map.setZoom(zoom_level);
        PressureNET.map.panTo(new google.maps.LatLng(latitude, longitude));
    }

    PressureNET.add_marker = function(image, body, position) {
        var infowindow = new google.maps.InfoWindow({
            content: body
        });

        var marker = new google.maps.Marker({
            map: PressureNET.map,
            icon: image,
            position: position,
        });

        google.maps.event.addListener(marker, 'click', function() {
            infowindow.open(
                PressureNET.map,
                marker
            );
        });
    }

    // Load data
    PressureNET.load_data = function() {
        end_time = new Date().getTime();
        start_time = end_time - 3600000;

        var query_params = {
            format: 'json',
            start_time: start_time,
            end_time: end_time,
            limit: 100000
        };

        $.ajax({
            url: PressureNET.readings_url,
            data: query_params,
            dataType: 'json',
            success: function(readings, status) {

                $(readings).each(function (index, reading) {
                    if (reading.reading < 700) {
                        return;
                    }
                    var bin_key = encodeGeoHash(reading.latitude, reading.longitude).substring(0, PressureNET.geohash_key_length);

                    if (PressureNET.heatmap_bins[bin_key]) {
                        PressureNET.heatmap_bins[bin_key].readings.push(reading);
                    } else {
                        PressureNET.heatmap_bins[bin_key] = {
                            readings: [reading]
                        };
                    }

                    //var marker_body = 'Latitude: ' + reading.latitude + '<br>Longitude: ' + reading.longitude + '<br>Bin: ' + bin_key + '<br>Reading: ' + reading.reading;

                    //PressureNET.add_marker(
                    //    PressureNET.reading_marker_image,
                    //    marker_body,
                    //    new google.maps.LatLng(reading.latitude, reading.longitude)
                    //)

                });

                for (var bin_key in PressureNET.heatmap_bins) {
                    var bin_readings = PressureNET.heatmap_bins[bin_key].readings;
                    var bin_sum = 0.0;

                    $(bin_readings).each(function (index, bin_reading) {
                        bin_sum += bin_reading.reading;
                    });

                    PressureNET.heatmap_bins[bin_key].average = bin_sum/bin_readings.length;

                }

                var min_pressure = 1000.0;
                var max_pressure = 1000.0;

                for (var bin_key in PressureNET.heatmap_bins) {
                    var bin_average = PressureNET.heatmap_bins[bin_key].average
                    min_pressure = Math.min(min_pressure, bin_average);
                    max_pressure = Math.max(max_pressure, bin_average);
                }

                var pressure_range = max_pressure - min_pressure;

                for (var bin_key in PressureNET.heatmap_bins) {
                    var bin = PressureNET.heatmap_bins[bin_key];

                    var normalized_pressure = Math.round(((bin.average - min_pressure) / pressure_range) * 100);

                    var bin_colour = PressureNET.gradient.colourAt(normalized_pressure);

                    //heatmap_points.push({
                    //    location: position,
                    //    weight: bin.average
                    //});


                    var decoded_key = decodeGeoHash(bin_key);
                    var bottom_left = new google.maps.LatLng(decoded_key.latitude[1], decoded_key.longitude[0]);
                    var top_right = new google.maps.LatLng(decoded_key.latitude[0], decoded_key.longitude[1]);

                    var rectangle_options = {
                        map: PressureNET.map,
                        strokeWeight: 0,
                        fillColor: bin_colour,
                        fillOpacity: 0.35,
                        bounds: new google.maps.LatLngBounds(
                            bottom_left,
                            top_right
                        )
                    };

                    // Add the circle for this city to the map.
                    new google.maps.Rectangle(rectangle_options);

                    //var marker_body = 'Key: ' + bin_key + '<br>Average: ' + bin.average + '<br>Points: ' + bin.readings.length + '<br>Colour: ' + bin_colour;;

                    //PressureNET.add_marker(
                    //    PressureNET.bin_marker_image,
                    //    marker_body,
                    //    bottom_left
                    //)
                }

                //var heatmap = new google.maps.visualization.HeatmapLayer({
                //    data: heatmap_points,
                //    dissipating: true,
                //    radius: 200,
                //    opacity: 0.5
                //});
                //
                //heatmap.setMap(PressureNET.map);
            }
        });
    }

}).call(this);
