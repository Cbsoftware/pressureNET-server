(function () {

    var global = this;

    var PressureNET = (global.PressureNET || (global.PressureNET = {}));

    PressureNET.dashboardDisplayGraphs = function (graphs) {
        $(graphs).each(function (index, graph) {

            var graph_id = graph.id + '_graph';
            var graph_html = '<strong>' + graph.title + '</strong><div id="' + graph_id + '"></div>';

            var $graphs = $('#graphs').append(graph_html);
            var $graph = $graphs.find('#' + graph_id);
            $graph.css({
                'height': '200px',
                'width': '100%'
            });
            $.plot($graph, [graph.data], {
                color: 'rgb(48, 155, 191)',
                points: {
                    show: true
                },
                lines: {
                    show: true
                },
                xaxis: {
                    mode: 'time',
                    timeformat: '%Y/%m/%d',
                }
            });
        });

    }

}).call(this);
