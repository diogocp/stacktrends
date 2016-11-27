import d3 from "d3";
import d3Promise from "d3.promise";

export default class {
    constructor(parentId) {
        this.dataset = this.loadData("data/country_tag.csv");
        this.container = d3.select("#" + parentId);
        window.addEventListener(
                "tagSelectionChange",
                this.onTagSelectionChange.bind(this),
                false);
    }

    async draw(tags) {
        var data = (await this.dataset)["USA"];
        data = data.filter(item => {
            return tags.indexOf(item.tag) != -1;
        });

        var containerRect = this.container.node().getBoundingClientRect();

        this.container.select("svg").remove();
        var svg = this.container
            .append("svg")
            .attr("width", containerRect.width - 10)
            .attr("height", containerRect.height - 10);
        var margin = {top: 20, right: 20, bottom: 30, left: 80};
        var width = +svg.attr("width") - margin.left - margin.right;
        var height = +svg.attr("height") - margin.top - margin.bottom;

        var g = svg.append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var x = d3.scale
            .ordinal()
            .rangeRoundBands([0, width], .1)
            .domain(data.map(d => d.tag));
        var y = d3.scale
            .linear()
            .range([height, 0])
            .domain([0, d3.max(data, d => d.count)]);

        g.append("g")
            .attr("class", "axis axis--x")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.svg.axis().scale(x).orient("bottom"));

        g.append("g")
            .attr("class", "axis axis--y")
            .call(d3.svg.axis().scale(y).orient("left"))
            .append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", "0.71em")
            .attr("text-anchor", "end")
            .text("Frequency");

        g.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.tag))
            .attr("y", d => y(d.count))
            .attr("width", x.rangeBand())
            .attr("height", d => height - y(d.count));

        this.chart = g;
    }

    onTagSelectionChange(event) {
        var selectedTags = event.detail;
        this.draw(selectedTags);
    }

    loadData(filename) {
        return d3Promise.csv(filename).then(data => {
            var dataset = {};
            data.forEach(item => {
                if(typeof dataset[item.country] === "undefined") {
                    dataset[item.country] = [];
                }
                dataset[item.country].push({
                    tag: item.tag,
                    count: +item.count
                });
            });
            return dataset;
        });
    }
}
