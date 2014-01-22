(function () {
    var global = this;

    var PressureNET = (global.PressureNET || (global.PressureNET = {}));

    PressureNET.initialize = function (config) {
        PressureNET.config = config;
        PressureNET.initialize_map();
        PressureNET.initialize_controls();
    }

    PressureNET.initialize_map = function () {
        PressureNET.map = new google.maps.Map(
            document.getElementById('map_canvas'),
            {
                center: new google.maps.LatLng(42, -73), // start near nyc
                zoom: 4,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            }
        );
        
        // Create the search box and link it to the UI element.
        var search_input = document.getElementById('pac-input');
        PressureNET.map.controls[google.maps.ControlPosition.TOP_LEFT].push(search_input);

        var searchBox = new google.maps.places.SearchBox((search_input));

        google.maps.event.addListenerOnce(PressureNET.map, 'idle', function() {
            $('.controls').fadeIn();
            $('#map_panel').fadeIn();
            
        });

        google.maps.event.addListener(searchBox, 'places_changed', function() {
            var places = searchBox.getPlaces();

            var bounds = new google.maps.LatLngBounds();
            for (var i = 0, place; place = places[i]; i++) {
                bounds.extend(place.geometry.location);
            }
            PressureNET.map.fitBounds(bounds);
            PressureNET.map.setZoom(12);
        });

        google.maps.event.addListener(PressureNET.map, 'bounds_changed', function() {
            PressureNET.update_graph();
        });
        
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(function (position) { 
                var latitude = position.coords.latitude;
                var longitude = position.coords.longitude;
                var lat_lng = new google.maps.LatLng(latitude, longitude); //Makes a latlng
                PressureNET.map.panTo(lat_lng);
                PressureNET.map.setZoom(12);
            });
        }
    }

    PressureNET.initialize_controls = function () {
        $('.input-daterange').datepicker({
            endDate: new Date(),
            autoclose: true
        });

        var end = new Date();
        var start = new Date(end - (7 * 24 * 60 * 60 * 1000));

        $('#start_date').datepicker('setDate', start);
        $('#end_date').datepicker('setDate', end + '');

        $('#start_date').datepicker().on('changeDate', PressureNET.update_graph); 
        $('#end_date').datepicker().on('changeDate', PressureNET.update_graph); 
        $('#date_length').on('change', PressureNET.update_graph); 
    }

    PressureNET.update_graph = function () {
        var bounds = PressureNET.map.getBounds();
        var ne = bounds.getNorthEast();
        var sw = bounds.getSouthWest();
        
        var min_latitude = sw.lat();
        var max_latitude = ne.lat();
        var min_longitude = sw.lng();
        var max_longitude = ne.lng();

        var log_duration = $('#date_length').val();

        var start_time = $('#start_date').datepicker('getDate').getTime(); 
        var end_time = $('#end_date').datepicker('getDate').getTime();

        var query_params = {
            min_latitude: min_latitude,
            max_latitude: max_latitude,
            min_longitude: min_longitude,
            max_longitude: max_longitude,
            start_time: start_time,
            end_time: end_time,
            log_duration: log_duration
        };

        $.ajax({
            url: PressureNET.config.data_url, 
            data: query_params,
            dataType: 'json',
            success: function(data, status) {
                var plot_data = [];

                for(var data_point_i in data) {
                    var data_point = data[data_point_i];
                    plot_data.push([data_point.timestamp, data_point.median]);
                }

                $.plot(
                    $('#map_graph'), 
                    [{
                        data: plot_data,
                        color: '#428bca',
                        lines: {
                            show: true
                        },
                        points: {
                            show: false
                        },
                    }], {
                        xaxis: {
                            mode: 'time',
                        },
                        yaxis: {
                        },
                        grid: {
                            color: '#ffffff'
                        }
                    }
                );
            }
        });
    }

}).call(this);
