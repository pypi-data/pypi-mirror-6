// TODO: Use simulation time (nicely formatted as date) for x-axis
//       (see: http://bost.ocks.org/mike/path/)
// TODO: Use node collors in timeline
// TODO: Allow more than one value to be selected per entity type
// TODO: take running mean of the duration of the last five update cycles and
//       use this as the duration for the next transition of the timeline.
// TODO: Dragging nodes in the topology shouldn't trigger the timeline.

//
// Config
//
var width = 1000;
var height = Math.min(800, window.innerHeight);
var sub_heights = {
    topology: height * 0.7,
    timeline: height * 0.3
}
var topology_config = {
    // Nodes
    node_r: 6,

    // Links
    link_length: 15,  // default link length (if link.length == 0)
    link_factor: 100,  // factor for link length (if link.length > 0)

    // Force params
    force_default_charge: -50,
    force_charge: {
        pqbus: -100,
        refbus: -75
    },
    force_gravity: 0.12
}
var timeline_backlog = 49;
var timeline_x_ticks = 25;


//
// Global state :-)
//
var etypes = null;  // Entity types (will be set in setup());
var progressbar = ProgressBar();
var topology = Topology(topology_config);
var timeline = Timeline(timeline_backlog);
var svg = d3.select('#canvas').attr('width', width).attr('height', height);
var ws = make_websocket();


//
// Functions
//
/**
 * Setup the websocket.
 */
function make_websocket() {
    var callbacks = {
        setup_topology: setup,
        update_data: update
    };

    var ws = new WebSocket('ws://' + location.host + '/websocket');
    ws.onopen = function get_topology(evt) {
        ws.send('get_topology');
    };
    ws.onmessage = function dispatch(evt) {
        var msg = JSON.parse(evt.data);
        var msg_type = callbacks[msg[0]];
        if (msg_type) {
            msg_type(msg[1]);
        }
        else {
            console.log('Unknow message type: ' + msg[0]);
        }
    };
    ws.onclose = function(evt) {
        progressbar.set_progress(0);
    }

    return ws;
}

/**
 * Create and initialize the topology graph.
 *
 * *data* is an object with three attributes:
 *
 * - ``data.etypes`` contaisn the configuration for all entity types.
 * - ``data.nodes`` is a list of node objects for the topology
 * - ``data.links`` is a list of link objects for the topology
 */
function setup(data) {
    etypes = data.etypes;  // Set global variable
    progressbar.set_progress(0);
    topology.create(data);
    timeline.init(data.nodes);
}

/**
 * Update the progress bar, topology and (if needed) the timeline
 *
 * *data* is an object with two attributes:
 *
 * - ``data.progress`` is a number with the current sim. progress in [0, 100].
 * - ``data.nodes`` is a dict/object mapping node names to a new "value".
 */
function update(data) {
    progressbar.set_progress(data.progress);
    topology.update(data);
    timeline.update(data.nodes);
}


function ProgressBar() {
    var progress_bar = d3.select('#progress');
    var progress_scale = d3.scale.linear()
        .domain([0, 100])
        .range([0, d3.select('html').style('width')]);

    return {
        set_progress: function set_progress(progress) {
            progress_bar.transition()
                .style('width', progress_scale(progress));
        }
    };
}


function Topology(conf) {
    // Colorbar scales
    var colorbar_gr = d3.scale.linear()
        .range([0, 120]);  // HSL 'hue' from red to green
    var colorbar_rgr = d3.scale.linear()
        .range([-120, 120]);  // HSL 'hue' from green to red to green

    /**
    * Create and initialize the topology graph.
    *
    * *data* is an object with three attributes:
    *
    * - ``data.etypes`` contaisn the configuration for all entity types.
    * - ``data.nodes`` is a list of node objects for the topology
    * - ``data.links`` is a list of link objects for the topology
    */
    function create(data) {
        // Set global etype etypesig and initialize the ring buffer.
        var etypes = data.etypes;

        // Initialize force layout
        var force = d3.layout.force()
            .size([width, sub_heights.topology])
            .links(data.links)
            .nodes(data.nodes)
            .charge(function(node) {
                var charge = conf.force_charge[etypes[node.type].cls];
                if (typeof charge === 'undefined') {
                    charge = conf.force_default_charge;
                }
                return charge;
            })
            .gravity(conf.force_gravity)
            .linkDistance(function(link) {
                var len = conf.link_length;
                if (link.length > 0) {
                    len = link.length * conf.link_factor;
                }
                return len;
            })
            .start();

        // Add circle and line elements for the topology
        var topology = svg.append('g')
            .attr('id', 'topology');

        var links = topology.selectAll('.link')
            .data(data.links)
        links.enter().append('line')
            .attr('class', 'link')

        var nodes = topology.selectAll('.node')
            .data(data.nodes)
        nodes.enter().append('circle')
            .attr('class', function(node) {
                var cls = 'node';
                if (etypes[node.type].cls) {
                    cls += ' ' + etypes[node.type].cls;
                }
                return cls;
            })
            .attr('r', conf.node_r)
            .on('click', function(d) {
                timeline.create(d, d3.select(this));
            })
            .call(force.drag);
        nodes.append('title').text(function(node) {
            return node.name;
        });

        // Update the position of the SVG elements (circles and lines) at each
        // tick of the force simulation.
        force.on('tick', function() {
            links.attr('x1', function(d) {
                return d.source.x;
            }).attr('y1', function(d) {
                return d.source.y;
            }).attr('x2', function(d) {
                return d.target.x;
            }).attr('y2', function(d) {
                return d.target.y;
            });

            nodes.attr('cx', function(d) {
                return d.x;
            }).attr('cy', function(d) {
                return d.y;
            });
        });

        make_legend(etypes, conf);
    }

    /**
    * Create a legend for the various node types.
    *
    * *etypes* is "data.etypes" the same as in "setup()".
    */
    function make_legend(etypes, conf) {
        var node_r = conf.node_r;
        var legend = svg.append('g')
            .attr('id', 'toplogy_legend')
            .attr('class', 'legend')
            .attr('transform', 'translate(30, 30)');

        var items = d3.entries(etypes)
            .sort(function(a, b) { return a.key > b.key; });

        var li = legend.selectAll('g')
                    .data(items)
                .enter().append('g')
                    .attr('transform', function(d, i) {
                        return 'translate(0, ' + (i * node_r * 4) + ')';
                    });
        li.append('circle')
            .attr('cx', 0)
            .attr('cy', 0)
            .attr('r', node_r)
            .attr('class', function(d) { return 'node ' + d.value.cls; })
        li.append('text')
            .attr('x', node_r * 3.5)
            .attr('y', node_r)
            .text(function(d) { return d.key; });
    }

    /**
    * Update visualization with new data
    */
    function update(data) {
        // Update node data and the ring buffer.
        var nodes = svg.selectAll('#topology .node');
        nodes.data().forEach(function(node, i) {
            node.value = data.nodes[node.name].value;
        });

        // Update the fill color of all nodes.
        nodes.style('fill', function(node) {
            var etype = etypes[node.type];
            var min = etype.min;
            var max = etype.max;
            // Clip value to [min, max]:
            var value = Math.min(max, Math.max(min, node.value));

            if (etype.min == 0) {
                // Positive values from [0, max]
                var colorbar = colorbar_gr.domain([0, etype.max]);
            }
            else if (etype.max == 0) {
                // Negative values from [min, 0]
                var colorbar = colorbar_gr.domain([0, etype.min]);
            }
            else {
                // Values in [min, max] with their center in (min + max) / 2
                var colorbar = colorbar_rgr.domain([etype.min, etype.max]);
            }
            var cval = colorbar(value);

            // Flip red-green to green-red (e.g, convert '0' to '120'):
            var range_max = colorbar.range()[1];
            cval = -1 * (Math.abs(cval) - range_max);

            return 'hsl(' + cval + ', 100%, 50%)';
        });
    }

    return {
        create: create,
        update: update
    };
}


/**
 * Animated time line of a node's data.
 *
 * Inspired by http://bl.ocks.org/mbostock/1642874
 */
function Timeline(backlog_size) {
    var timeline_node = null;
    var timeline_circle = null; // Highlighted circle element of the topo.
    var backlog_data = {};

    // Margin and size of the actual drawing area
    var m = {top: 20, right: 20, bottom: 30, left: 110};
    var w = width - m.left - m.right;
    var h = sub_heights.timeline - m.top - m.bottom;

    // Scale to map data values to the pixel grid
    var x = d3.scale.linear();
    var y = d3.scale.linear();

    // Function mapping data to (x, y) coordinates in the plot
    var make_line = d3.svg.line()
        .x(function(d, i) { return x(i); })
        .y(function(d) { return y(d); });

    /**
     * Create the ring buffers for node data.
     */
    function init(nodes) {
        nodes.forEach(function(node) {
            var init_val;
            if (etypes[node.type].min == 0 || etypes[node.type].max == 0) {
                init_val = 0;
            }
            else {
                init_val = (etypes[node.type].min + etypes[node.type].max) / 2;
            }
            backlog_data[node.name] = RingBuffer(backlog_size, init_val);
        });
    }

    /**
     * Create axes for the timeline
     *
     * *node* is a node object from the topology.
     */
    function create(node, circle) {
        svg.selectAll('#timeline').remove();
        if (timeline_circle) {
            timeline_circle.classed('highlight', false);
        }
        if (timeline_node == node.name) {
            timeline_node = null;
            timeline_circle = null;
            return;
        }
        timeline_node = node.name;
        timeline_circle = circle.classed('highlight', true);

        var min = etypes[node.type].min;
        var max = etypes[node.type].max;

        x.domain([0, timeline_backlog - 1]).range([0, w]);
        y.domain([min, max]).range([h, 0]);

        // Add an SVG element with the desired dimensions and margin.
        var timeline = svg.append('g')
            .attr('id', 'timeline')
            .attr('class', 'timeline')
            .attr('transform', 'translate(0, ' + sub_heights.topology + ')')
            .attr('width', w + m.left + m.right)
            .attr('height', h + m.top + m.bottom)

        timeline.append('text')
            .attr('class', 'label')
            .attr('text-anchor', 'middle')
            .attr('x', m.left + w / 2)
            .attr('y', '1em')
            .text(node.name)

        var graph = timeline.append('g')
            .attr('transform', 'translate(' + m.left + ', ' + m.top + ')');

        // Clip path for animated timeline
        graph.append('defs').append('clipPath')
                .attr('id', 'clip')
            .append('rect')
                .attr('width', w)
                .attr('height', h);

        // Create and append the x-axis
        var x_axis = d3.svg.axis().scale(x)
            .ticks(timeline_x_ticks)
            .tickFormat(function(val) { return val + 1 - timeline_backlog; });
        var y_pos;
        if (min == 0) {
            y_pos = 0;
        }
        else if (max == 0) {
            y_pos = max;
        }
        else {
            // Vertically center x-axis, e.g. for node voltages.
            y_pos = (min + max) / 2;
        }
        graph.append('g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0, ' + y(y_pos) + ')')
            .call(x_axis);

        // Create and append the y-axis
        var y_axis = d3.svg.axis().scale(y).ticks(5).orient('left');
        graph.append('g')
                .attr('class', 'y axis')
                .call(y_axis)
            .append('text')
                .attr('class', 'label')
                .attr('text-anchor', 'end')
                .attr('x', 0)
                .attr('dx', -60)
                .attr('y', h / 2)
                .attr('dy', '.32em')  // or: #y_axis -> g[2/5] -> text.dy
                .text(etypes[node.type].unit);

        graph.append('g')
                .attr('clip-path', 'url(#clip)')
            .append('path')
                .datum(backlog_data[node.name].data())
                .attr('class', 'line')
                .attr('d', make_line);
    }

    /**
     * Update the timeline with new values.
     */
    function update(nodes) {
        // Update ring buffes with new data
        d3.map(nodes).forEach(function(k, v) {
            backlog_data[k].push(v.value);
        });

        if (timeline_node == null) {
            return;
        }

        var value = nodes[timeline_node].value;
        var line = svg.select('#timeline .line');
        line.datum().push(value);

        line.attr('d', make_line)
            .attr('transform', null);
        line.transition()
            .ease('linear')
            .attr('transform',
                    'translate(' + x(-1) + ', 0)');
        if (line.datum().length > timeline_backlog) {
            line.datum().shift();
        }
    }

    return {
        init: init,
        create: create,
        update: update
    };
}


/**
 * A simple ring buffer with stores at most *size* elements.
 *
 * If it reaches its capacity and another item is pushed, the oldest item is
 * dropped.
 *
 * ``data()``
 *   Return an array containing all data. The oldest item will be at position
 *   0 and the newest item on the end.
 *
 * ``push(item)``
 *   Push *item* to the buffer removing the oldest item if necessary.
 */
function RingBuffer(size, init_val) {
    var zero = 0;  // Points to element "0"
    var buffer = [];
    for (var i = 0; i < size; i ++) {
        buffer.push(init_val);
    }

    function get(key) {
        key = (size + zero + key) % size;
        return buffer[key];
    }

    return {
        data: function() {
            ret = [];
            for (var i = 0; i < buffer.length; i ++) {
                ret.push(get(i));
            }
            return ret;
        },
        push: function(item) {
            buffer[zero] = item;
            zero = (zero + 1) % size;
        }
    };
}
