(function() {

    var global = this;

    var PressureNET = (global.PressureNET || (global.PressureNET = {}));

    // Globals
    PressureNET.readings_url = '';
    PressureNET.map = null;

    PressureNET.gradient = new Rainbow();
    PressureNET.gradient.setSpectrum('#00FF00', '#FF0000');

    PressureNET.rectangles = [];

    PressureNET.min_pressure = 0;
    PressureNET.max_pressure = 1500;

    PressureNET.min_hash_length = 3;
    PressureNET.max_hash_length = 5;
    PressureNET.geohash_key_length = PressureNET.max_has_length;
    PressureNET.interpolation_enabled = true;
    PressureNET.interpolation_passes = 10;
    PressureNET.max_opacity = 0.65;

    PressureNET.min_zoom = 3;
    PressureNET.max_zoom = 14;

    PressureNET.reading_marker_image = new google.maps.MarkerImage(
        'http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|FF0000',
        new google.maps.Size(21, 34),
        new google.maps.Point(0,0),
        new google.maps.Point(10, 34)
    );

    // Initialization
    PressureNET.initialize = function(config) {
        PressureNET.readings_url = config.readings_url;

        PressureNET.setup_controls();
        PressureNET.init_map();
        PressureNET.get_location();
        PressureNET.load_data();
    }

    PressureNET.setup_controls = function () {
        $('#control_panel_interpolation_enabled').on('change', function (event) {
            PressureNET.interpolation_enabled = $(event.target).is(':checked');
            PressureNET.update_map();
        });

        $('#control_panel_interpolation_passes').on('change', function (event) {
            PressureNET.interpolation_passes = parseInt($(event.target).val());
            PressureNET.update_map();
        });
    }

    PressureNET.init_map = function() {
        var map_options = {
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            minZoom: 3,
            maxZoom: 14
        };
        PressureNET.map = new google.maps.Map(document.getElementById('map_canvas'), map_options);

        //var weatherLayer = new google.maps.weather.WeatherLayer({
        //  temperatureUnits: google.maps.weather.TemperatureUnit.CELSIUS
        //});
        //weatherLayer.setMap(PressureNET.map);

        //var cloudLayer = new google.maps.weather.CloudLayer();
        //cloudLayer.setMap(PressureNET.map);
        google.maps.event.addListener(PressureNET.map, 'zoom_changed', function() {
            PressureNET.update_map();
        });
        google.maps.event.addListener(PressureNET.map, 'dragend', function() {
            PressureNET.update_map();
        });

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

    PressureNET.clear_rectangles = function () {
        _(PressureNET.rectangles).each(function (rectangle) {
            rectangle.setMap(null);
        });
    }

    PressureNET.is_visible = function (latitude, longitude) {
        var visible_bounds = PressureNET.map.getBounds();
        var position = new google.maps.LatLng(latitude, longitude);
        return visible_bounds.contains(position);
    }

    PressureNET.filter_outlying_readings = function (readings) {
        return _(readings).filter(function (reading) {
            return (reading.reading > PressureNET.min_pressure) && (reading.reading < PressureNET.max_pressure);
        });
    }

    PressureNET.filter_visible_readings = function (readings) {
        return _(readings).filter(function (reading) {
            return PressureNET.is_visible(reading.latitude, reading.longitude);
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
                PressureNET.readings = PressureNET.filter_outlying_readings(readings);
                PressureNET.update_map();
            }
        });
    }

    PressureNET.update_visible_scale = function () {
        var zoom = PressureNET.map.getZoom();
        var zoom_ratio = (zoom - PressureNET.min_zoom) / PressureNET.max_zoom;

        var hash_length_scale = PressureNET.max_hash_length - PressureNET.min_hash_length;
        var rectangle_scale = Math.round((zoom_ratio * hash_length_scale)) + PressureNET.min_hash_length;
        PressureNET.geohash_key_length = rectangle_scale;
    }

    PressureNET.update_map = function () {
        console.log('updating map');
        PressureNET.clear_rectangles();
        PressureNET.update_visible_scale();


        var visible_readings = PressureNET.filter_visible_readings(PressureNET.readings);

        PressureNET.calculate_bins(visible_readings);
        PressureNET.calculate_neighbours();
        PressureNET.render_bins(visible_readings);
    }

    PressureNET.calculate_bins = function (readings) {
        PressureNET.reading_bins = {};

        _(readings).each(function (reading) {
            var bin_key = encodeGeoHash(reading.latitude, reading.longitude).substring(0, PressureNET.geohash_key_length);

            if (PressureNET.reading_bins[bin_key]) {
                PressureNET.reading_bins[bin_key].readings.push(reading);
            } else {
                PressureNET.reading_bins[bin_key] = {
                    readings: [reading]
                };
            }
        });

        _(PressureNET.reading_bins).each(function (bin) {
            bin.average = Stats.median(_(bin.readings).map(function (reading) { return reading.reading; }));
        });
    }

    PressureNET.calculate_neighbours = function () {
        var directions = ['top', 'bottom', 'left', 'right'];

        if (!PressureNET.interpolation_enabled) {
            return;
        }

        for (var pass=0; pass < PressureNET.interpolation_passes; pass++) {
            console.log('interpolation pass ' + pass);
            _(PressureNET.reading_bins).each(function (bin, bin_key) {
                _(directions).each(function (direction) {
                    var adjacent_key = calculateAdjacent(bin_key, direction);
                    var adjacent_position = decodeGeoHash(adjacent_key);
                    var adjacent_latitude = adjacent_position.latitude[2];
                    var adjacent_longitude = adjacent_position.longitude[2];
                    var adjacent_visible = PressureNET.is_visible(adjacent_latitude, adjacent_longitude);

                    if (PressureNET.reading_bins[adjacent_key] || !adjacent_visible) {
                        return;
                    }

                    var neighbour_averages = _(directions).map(function (neighbour_direction) {
                        var neighbour_key = calculateAdjacent(adjacent_key, neighbour_direction);
                        var neighbour = PressureNET.reading_bins[neighbour_key];

                        if (neighbour) {
                            return neighbour.average;
                        }
                    });

                    var filtered_averages = _(neighbour_averages).filter(function (neighbour_average) {
                        return neighbour_average;
                    });

                    var adjacent_pressure = Stats.mean(filtered_averages);
                    PressureNET.reading_bins[adjacent_key] = {
                        average: adjacent_pressure,
                        readings: [],
                        interpolated: pass
                    };
                });
            });
        }
    }
    
    PressureNET.render_bins = function (readings) {

        PressureNET.reading_pressures = _(readings).map(function (reading) { return reading.reading; });
        PressureNET.reading_std_dev = Stats.stdev(PressureNET.reading_pressures);
        PressureNET.reading_median = Stats.median(PressureNET.reading_pressures);

        _(PressureNET.reading_bins).each(function (bin, bin_key) {
            var normalized_pressure = Math.round(Stats.sigmoid((bin.average - PressureNET.reading_median) / PressureNET.reading_std_dev) * 100);
            var bin_colour = PressureNET.gradient.colourAt(normalized_pressure);
            var bin_opacity = PressureNET.max_opacity;

            if (bin.interpolated) {
                var bin_opacity = (1 - (bin.interpolated/PressureNET.interpolation_passes)) * PressureNET.max_opacity;
            }

            PressureNET.draw_rectangle(bin_key, bin_colour, bin_opacity);
        });

        PressureNET.update_control_panel();
    }


    PressureNET.draw_rectangle = function (bin_key, bin_colour, bin_opacity) {
        var decoded_key = decodeGeoHash(bin_key);
        var bottom_left = new google.maps.LatLng(decoded_key.latitude[1], decoded_key.longitude[0]);
        var top_right = new google.maps.LatLng(decoded_key.latitude[0], decoded_key.longitude[1]);

        var rectangle_options = {
            map: PressureNET.map,
            strokeWeight: 0,
            fillColor: bin_colour,
            fillOpacity: bin_opacity ? bin_opacity: PressureNET.max_opacity,
            bounds: new google.maps.LatLngBounds(
                bottom_left,
                top_right
            )
        };

        // Add the circle for this city to the map.
        PressureNET.rectangles.push(new google.maps.Rectangle(rectangle_options));
    }

    PressureNET.update_control_panel = function () {
        $('#control_panel_num_readings').html(PressureNET.reading_pressures.length);
        $('#control_panel_min_pressure').html(_(PressureNET.reading_pressures).min());
        $('#control_panel_max_pressure').html(_(PressureNET.reading_pressures).max());
        $('#control_panel_mean_pressure').html(Stats.mean(PressureNET.reading_pressures));
        $('#control_panel_median_pressure').html(Stats.median(PressureNET.reading_pressures));
        $('#control_panel_standard_deviation').html(Stats.stdev(PressureNET.reading_pressures));
    }

}).call(this);
