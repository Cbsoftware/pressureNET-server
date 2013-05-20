/*
 * pressureNET Analysis Server
 * Jacob Sheehy, Cumulonimbus
 * 
 * Run with node.js: node server.js
 * 
 * This source is released under the MIT license.
*/

var http = require('http');
var pg = require('pg'); 
var sys = require('sys');
var fs = require('fs');
var url = require('url');
var lineReader = require('line-reader');

var connectionString = "postgres://postgres:password@localhost:5432/postgres"; 

var returnPage = "";

http.createServer(function (req, res) {

var minVisLat = 0;
var maxVisLat = 0;
var minVisLon = 0;
var maxVisLon = 0;

var limit = 1000;

 try  {
    minVisLat = url.parse(req.url, true).query.minVisLat;
    maxVisLat = url.parse(req.url, true).query.maxVisLat;
    minVisLon = url.parse(req.url, true).query.minVisLon;
    maxVisLon = url.parse(req.url, true).query.maxVisLon;
    startTime = url.parse(req.url, true).query.startTime;
    endTime   = url.parse(req.url, true).query.endTime;
    limit = url.parse(req.url, true).query.limit;
    
    var after = function(callback) {
      return function(err, queryResult) {
        if(err) {
          return res.end("Error! " + sys.inspect(err))
        }
        callback(queryResult)
      }
    }
  } catch(e) {
    console.log(e);
  }
  
  /*
   * Build a data array that we will return through http.
   * 
   * The first array element is [minpressure, maxpressure]
   * The second is [minTime, maxTime].
   * All others are the data points. 
   * 
   * 
  */
  function assembleJSGraphsFromData(result) {
   var finalJSCode = [];
   
   for(var i = 0; i < result.rows.length; i++) { 
     finalJSCode.push('[' + [(result.rows[i].daterecorded) + ',' +  result.rows[i].reading] + ']');
   }
   return '[' + finalJSCode + ']';
  }
  
  pg.connect(connectionString, after(function(client) {
    try{
        var where = "latitude > " + minVisLat + " and latitude < " + maxVisLat + " and longitude > " + minVisLon + " and longitude < " + maxVisLon + " and daterecorded > " + startTime + " and daterecorded < " + endTime;
        
        var whereDataIsClose = " and (reading > (select avg(archive.reading) from archive where " + where + ") - 2*(select (STDDEV_POP(archive.reading)) from archive where " + where + ")) and (reading < (select avg(archive.reading) from archive where " + where + ") + 2*(select (STDDEV_POP(archive.reading)) from archive where " + where + "))";
        var simpleQuery = "SELECT * FROM archive WHERE " + where + " limit " + limit;
        
        where += whereDataIsClose;
        
        var dataQuery = "SELECT id, reading, latitude, longitude, reading, daterecorded FROM archive GROUP BY archive.reading, archive.id, archive.latitude, archive.longitude, archive.daterecorded HAVING " + where + " limit " + limit; // limit 10000
        //console.log(dataQuery);
        
        
        client.query(dataQuery, after(function(result) {
          console.log(dataQuery);
          var js = assembleJSGraphsFromData(result);
          var text = js;
          res.writeHead(200, {"Content-Type": "text/javascript", "Access-Control-Allow-Origin": "*"});
          res.end(text);
        }))
     } catch(e) {
      console.log(e);      
     }
  }))
}).listen(3142);

console.log('Server running at http://127.0.0.1:3142/');

