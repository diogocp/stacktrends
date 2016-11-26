import d3 from "d3";


export default class {
	
	constructor(element){
		// Set the dimensions of the canvas / graph
        var margin = {top: 30, right: 20, bottom: 30, left: 50},
        width = 600 - margin.left - margin.right,
        height = 270 - margin.top - margin.bottom;

        // Set the ranges
        var x = d3.time.scale().range([0, width]);
        var y = d3.scale.linear().range([height, 0]);

        // Define the axes
        var xAxis = d3.svg.axis().scale(x)
            .orient("bottom").ticks(5);

        var yAxis = d3.svg.axis().scale(y)
            .orient("left").ticks(5);

        // Define the line
        var priceline = d3.svg.line()
            .x(function(d) { return x(d.year); })
            .y(function(d) { return y(d.frequency); });

        // Adds the svg canvas
        var svg = d3.select(element)
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");

        // Get the data
        d3.csv("data/lineChartExample.csv", function(error, data) {
            data.forEach(function(d) {
                d.frequency = +d.frequency;
            });

            // Scale the range of the data
            x.domain(d3.extent(data, function(d) { return d.year; }));
            y.domain([0, d3.max(data, function(d) { return d.frequency; })]);

            // Add the X Axis
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            // Add the Y Axis
            svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

        });
		this._lineChart = svg;
		this._priceline = priceline;
	}
	
	update(tags) {		
        // gets the svg canvas and priceline
        var svg = this._lineChart;

        var priceline = this._priceline;

		d3.select(".line").remove();
		
        // Get the data
        d3.csv("data/lineChartExample.csv", function(error, data) {
            data.forEach(function(d) {
					d.frequency = +d.frequency;
            });

            // Nest the entries by symbol
            var dataNest = d3.nest()
                .key(function(d) {
							return d.language;
					})
                .entries(data);

			//Filter entries by tags received	
			var dataFiltered = dataNest.filter(
				function (d) {
					if(tags.indexOf(d.key) !== -1){
						return d.key;
					}
				}
			)
				
            // Loop through each language / key
            dataFiltered.forEach(function(d) {		
                svg.append("path")
                    .attr("class", "line")
					.attr("d", priceline(d.values));

            });

        });
    }


	
	}