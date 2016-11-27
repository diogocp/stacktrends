import d3 from "d3";
import d3Promise from "d3.promise";
import nv from "nvd3";


export default class {
    constructor(parentId) {
        this.dataset = this.loadData("data/country_tag.csv");
        this.container = d3.select("#" + parentId);
        this.draw();
        window.addEventListener(
                "tagSelectionChange",
                this.onTagSelectionChange.bind(this),
                false);
    }

    async draw() {
        var container = this.container;

        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function(d) { return d.tag })
                .y(function(d) { return d.count })
                .showValues(true)
                .duration(500)
                .noData("Please select one or more programming languages");

            container.append("svg").datum([]).call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        },
        chart => {
            this.chart = chart;
        });
    }

    async onTagSelectionChange(event) {
        var selectedTags = event.detail;

        // FIXME select correct country
        var data = await this.filterData("USA", selectedTags);

        // Stagger labels when there are more than 8 bars
        this.chart.staggerLabels(data[0].values.length > 8);

        this.container
            .select("svg")
            .datum(data)
            .call(this.chart);
    }

    async filterData(country, tags) {
        var dataset = await this.dataset;

        return [{
            key: country,
            values: dataset[country].values.filter(item => {
                return tags.indexOf(item.tag) != -1;
            })
        }];
    }

    async loadData(filename) {
        var data = await d3Promise.csv(filename);
        var dataset = {};

        data.forEach(item => {
            if(typeof dataset[item.country] === "undefined") {
                dataset[item.country] = {key: item.country, values: []};
            }
            dataset[item.country].values.push({
                tag: item.tag,
                count: +item.count
            });
        });

        return dataset;
    }
}
