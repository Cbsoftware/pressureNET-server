(function() {
    
    var global = this;

    var PressureNET = (global.PressureNET || (global.PressureNET = {}));

    var readingsUrl = '';

    var centerLat = 0;
    var centerLon = 0;
    var min_latitude = 35;
    var max_latitude = 45;
    var min_longitude = -77;
    var max_longitude = -65;
    var start_time = 0;
    var end_time = 0;
    var zoom = 20;
   
    var dataPoints = [];
    
    var defaultQueryLimit = 20000;
    var defaultQueryIncrement = 5000;
    //var largeQueryIncrement = 10000;
    
    var map;
    
    var currentQueryLimit = defaultQueryLimit;

    PressureNET.initialize = function(config) {
        readingsUrl = config.readingsUrl;

        $('#share_input').focus(function() {
          $(this).select();
        });

        $(function() {
            $("#start_date").datepicker({changeMonth: true,dateFormat: "yy/mm/dd" });
            $("#end_date").datepicker({changeMonth: true,dateFormat: "yy/mm/dd"});
            PressureNET.initializeMap();

            // if there are query parameters, use them
            var hasEventParams = PressureNET.getUrlVars()['event'];
            if(hasEventParams=='true') {
              var latitudeParam = parseFloat(PressureNET.getUrlVars()['latitude']);
              var longitudeParam = parseFloat(PressureNET.getUrlVars()['longitude']);
              var start_timeParam = parseInt(PressureNET.getUrlVars()['start_time']);
              var end_timeParam = parseInt(PressureNET.getUrlVars()['end_time']);
              var zoomLevelParam = parseInt(PressureNET.getUrlVars()['zoomLevel']);
              PressureNET.setMapPosition(latitudeParam, longitudeParam, zoomLevelParam, start_timeParam, end_timeParam);
            } else {
              PressureNET.setDates(new Date(((new Date()).getTime() - (2*86400000))), new Date(((new Date()).getTime() + 86400000)));
              PressureNET.getLocation();
            }

          
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
        PressureNET.updateAllMapParams(map);
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
                var plot_data = [];
                var heatmap_data = [];
                for(var reading_i in readings) {
                    var reading = readings[reading_i];
                    if(reading.reading > 800) {
                        plot_data.push([
                            reading.daterecorded, 
                            reading.reading
                        ]);
                        heatmap_data.push({
                            location: new google.maps.LatLng(reading.latitude, reading.longitude),
                            weight: reading.reading
                        });
                    }
                }
                var heatmap = new google.maps.visualization.HeatmapLayer({
                    data: heatmap_data
                });
                heatmap.setMap(map);


                $.plot($("#placeholder"), [plot_data],{ 
                    lines:{show:false}, 
                    points:{show:true},
                    xaxis:{mode:"time"},
                });
                 
                // if the results were likely limited, let the user show more
                var showMore = "";
                if(readings.length%1000 == 0) {
                    var showMore = "<a onClick='PressureNET.loadAndUpdate(1)' style='cursor:pointer'>Show More</a>";
                }
                var share = '';
                if(centerLat!=0 ) {
                  share = " |  <a style='cursor:pointer;' id='dynamic_share_link' onClick='PressureNET.showShareLink(\"" + PressureNET.getShareURL() + "\")'>Share</a>";
                }
                $("#query_results").html("Showing " + readings.length + " results. " + showMore + share);
                PressureNET.updateGraph(min_latitude, max_latitude, min_longitude, max_longitude, start_time, end_time, readings.length);
            }
        });
    }

    PressureNET.updateGraph = function(min_latitude, max_latitude, min_longitude, max_longitude, start_time, end_time, length) {
      $('#min_latitude_cell').html(parseFloat(min_latitude).toFixed(6));
      $('#max_latitude_cell').html(parseFloat(max_latitude).toFixed(6));
      $('#min_longitude_cell').html(parseFloat(min_longitude).toFixed(6));
      $('#max_longitude_cell').html(parseFloat(max_longitude).toFixed(6));
      $('#start_time_cell').html($.datepicker.formatDate('MM dd yy', new Date(start_time)));
      $('#end_time_cell').html($.datepicker.formatDate('MM dd yy', new Date(end_time)));
      $('#resultsCount_cell').html(length);
    }

    PressureNET.showShareLink = function(link) {
      $('#share_spot').toggle();
      $('#share_input').val(link);
      $('#share_input').focus();
    }

    
    PressureNET.updateChart = function() {
        $('#current_position').html(centerLat + ", " + centerLon + " at zoom " + zoom);
    }
  
    PressureNET.updateAllMapParams = function() {
        centerLat = map.getCenter().lat();
        centerLon = map.getCenter().lng();
        var bounds = map.getBounds();
        if (typeof bounds != 'undefined') {
          var ne = bounds.getNorthEast();
          var sw = bounds.getSouthWest();
          min_latitude = sw.lat();
          max_latitude = ne.lat();
          min_longitude = sw.lng();
          max_longitude = ne.lng();
        } 
        
        zoom = map.getZoom();
        PressureNET.updateChart();
    },

    PressureNET.alertCumulonimbus = function() {
      start_time = $('#start_date').datepicker('getDate').getTime();
      end_time = $('#end_date').datepicker('getDate').getTime();
      document.location.href = "mailto:software@cumulonimbus.ca?subject=pressureNET%20Interesting%20Data&body=" + centerLat + "%20" + centerLon + "%20" + start_time + "%20" + end_time + "%20" + zoom;
    },
  
    PressureNET.getShareURL = function() {
      start_time = $('#start_date').datepicker('getDate').getTime();
      end_time = $('#end_date').datepicker('getDate').getTime();
      return "http://pressurenet.cumulonimbus.ca/?event=true&latitude=" + centerLat + "&longitude=" + centerLon + "&start_time=" + start_time + "&end_time=" + end_time + "&zoomLevel=" + zoom;
    },

    PressureNET.initializeMap = function() {
        var mapOptions = {
          center: new google.maps.LatLng(42, -73), // start near nyc
          zoom: 4,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };
        map = new google.maps.Map(document.getElementById("map_canvas"),
            mapOptions);
      
        var aboutToReload;
      
        google.maps.event.addListener(map, 'center_changed', function() {
        /*
            window.clearTimeout(aboutToReload);
            PressureNET.updateAllMapParams();
            aboutToReload = setTimeout("PressureNET.loadAndUpdate()", 1000);
            */
        });

        google.maps.event.addListener(map, 'zoom_changed', function() {
         /*
             window.clearTimeout(aboutToReload);
            PressureNET.updateAllMapParams();
            aboutToReload = setTimeout("PressureNET.loadAndUpdate()", 1000);
            */
        });
        
        google.maps.event.addListener(map, 'bounds_changed', function() {
            //if(map.getZoom() > 15) {
            //  map.setZoom(15);
            //}
            //window.clearTimeout(aboutToReload);
            //PressureNET.updateAllMapParams();
            //aboutToReload = setTimeout("PressureNET.loadAndUpdate()", 1000);
        });
    }

}).call(this);
