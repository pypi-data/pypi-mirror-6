cw.cubes.semnews = new Namespace('cw.cubes.semnews');

$.extend(cw.cubes.semnews, {


    d3BarChart: function(data, divid, settings){
	var $div = $('#' + divid);
        settings = settings || {};
	var label = settings.label || '';
        var width = settings.width || $div.width();
        var height = settings.height || $div.width();
	var margin = {top: 20, right: 20, bottom: 150, left: 40},
	width = width - margin.left - margin.right,
	height = height - margin.top - margin.bottom;

	var x = d3.scale.ordinal()
	    .rangeRoundBands([0, width], .1);

	var y = d3.scale.linear()
	    .range([height, 0]);

	var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom");

	var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left");

	var vis = d3.select('#' + divid).append("svg:svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	    .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	x.domain(data.map(function(d) { return d.label; }));
	y.domain([0, d3.max(data, function(d) { return d.value; })]);

	vis.append("g")
	    .attr("class", "x axis")
	    .attr("transform", "translate(0," + height + ")")
	    .call(xAxis)
            .selectAll("text")
		.attr("class", "x-axis-text")
                .style("text-anchor", "end")
		.attr("dx", "-.8em")
		.attr("dy", ".15em")
		.attr("transform", function(d) {return "rotate(-65)";});

	vis.append("g")
	    .attr("class", "y axis")
	    .call(yAxis)
	    .append("text")
	    .attr("transform", "rotate(-90)")
	    .attr("y", 6)
	    .attr("dy", ".71em")
	    .style("text-anchor", "end")
	    .text(label);

	vis.selectAll(".bar")
	    .data(data)
	    .enter().append("rect")
	    .attr("class", "bar")
	    .attr("x", function(d) { return x(d.label); })
	    .attr("width", x.rangeBand())
	    .attr("y", function(d) { return y(d.value); })
	    .attr("height", function(d) { return height - y(d.value); });
	},


    d3BundlingWheel: function(nodes, divid, settings){
	var $div = $('#' + divid);
        settings = settings || {};
        var tension = settings.tension || .70;
        var width = settings.width || $div.width();
        var height = settings.height || $div.width();
	var colormap = settings.colormap || ['lightgray', 'black'];
        var cluster = d3.layout.cluster()
            .size([360, width / 6])
            .sort(null)
            .value(function(d) { return d.size; });

        var bundle = d3.layout.bundle();

        var line = d3.svg.line.radial()
            .interpolate("bundle")
            .tension(tension)
            .radius(function(d) { return d.y; })
            .angle(function(d) { return d.x / 180 * Math.PI; });

        var all_nodes = [];
        $.each(nodes, function(k,v){all_nodes.push(v); });

	// Only display graph if there exist nodes
	var linkminscale = 0;
	var linkmaxscale = 1;
	var nodeminscale = 0;
	var nodemaxscale = 1;
	// Create a div for svg
	var vis = d3.select('#' + divid).append("svg:svg")
		      .attr("width", width)
		      .attr("height", height)
		      .append("svg:g")
		      .attr("transform", "translate("+width/2+","+height/2+")");

	// Cluster nodes
	nodes = cluster({size: 0, children: all_nodes});
	var nodes_mapping = {};
	$.each(nodes, function(idx, node) {nodes_mapping[node.data.id] = node;});
	// Create links
	var links = [];
	$.each(nodes, function(idx, node) {
	    if (node.data.weight > nodemaxscale){nodemaxscale = node.data.weight;}
	    if (node.data.weight < nodeminscale){nodeminscale = node.data.weight;}
	    $.each(node.data.edges || [], function(idx, edge) {
		if (edge[0] in nodes_mapping) {
		    links.push({source: node, target: nodes_mapping[edge[0]], weight:edge[1]});
		    if (edge[1] > linkmaxscale){linkmaxscale = edge[1];}
		    if (edge[1] < linkminscale){linkminscale = edge[1];}
		}
	    });
	});
	var splines = bundle(links);

	//var colorscale = d3.scale.category20c();
	var linkcolorscale = d3.scale.linear().domain([linkminscale,linkmaxscale]).range(colormap);
	var linkwidthscale = d3.scale.linear().domain([linkminscale,linkmaxscale]).range([0.1, 4]);

	// Rendering
	vis.selectAll("path.link")
		.data(links)
		.enter().append("path")
		.attr("class", function(d) {return 'link link-'+d.source.data.id+' link-'+d.target.data.id;})
		.style("stroke-width", function(d) {return linkwidthscale(d.weight); })
		.style("stroke", function(d) {return linkcolorscale(d.weight); })
		.attr("d", function(d, i) {return line(splines[i]);});

        function mouseover(d){
		$('.node-' + d.data.id+' text').css('stroke', 'blue');
		$.each(d.data.edges || [], function(idx, edge) {
			   $('.node-'+edge[0]+' text').css('stroke', 'blue');});
		$('.link').hide();
		$('.link-' + d.data.id).show();}

        function mouseout(d){
		/*$('.node-' + d.data.id+' text').css('stroke', nodescale(d.data.weight));
		$.each(d.data.edges || [], function(idx, edge) {
			   var color = nodescale(nodes_mapping[edge[0]].data.weight);
			   $('.node-'+edge[0]+' text').css('stroke', color);});*/
		$('.node-' + d.data.id+' text').attr('style', '');
		$.each(d.data.edges || [], function(idx, edge) {
			   $('.node-'+edge[0]+' text').attr('style', '')});
		$('.link').show();}

	var nodescale = d3.scale.linear().domain([nodeminscale,nodemaxscale]).range(colormap);
	var node = vis.selectAll("g.node")
		.data(nodes)
		.enter().append("svg:g")
		.attr("class", function(d) {return "node node-"+d.data.id;})
		.attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; });

	node.append("svg:text")
		.attr("dx", function(d) { return d.x < 180 ? 8 : -8; })
		.attr("dy", ".31em")
		.attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
		.attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; })
		//.style("stroke", function(d) {return nodescale(d.data.weight); })
		.on("mouseover", mouseover)
		.on("mouseout", mouseout)
		.on("click", function(d){window.location.href=d.data.url;})
		.text(function(d) { return d.data.label; });

	/*node.append("image")
	    .attr("xlink:href", function(d) {return d.data.depiction; })
	    .attr("height", 50)
	    .attr("width", 50)
	    .attr("transform", function(d) { return d.x < 180 ? null : "rotate(180)"; });*/


        d3.select(self.frameElement).style("height", height);
	}
    });