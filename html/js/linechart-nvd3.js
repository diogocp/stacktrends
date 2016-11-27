import d3 from "d3";
import d3Promise from "d3.promise";
import nv from "nvd3";


export default class {
    constructor(parentId) {
        this.dataset = this.loadData("data/tag_year.csv");
        this.draw(parentId);
    }

    async draw(parentId) {
        var chart = nv.models.lineChart().options({
            duration: 100,
            useInteractiveGuideline: false
        });

        // chart sub-models (ie. xAxis, yAxis, etc) when accessed directly, return themselves, not the parent chart, so need to chain separately
        chart.xAxis
            .axisLabel("Year")
            .tickFormat(d3.format('.0f'))
            .staggerLabels(false);

        chart.yAxis
            .axisLabel('Posts')
            .tickFormat(d => {
                if (d == null) {
                    return 'N/A';
                }
                return d3.format(',.0f')(d);
            });

        var data = await this.dataset;
        d3.select("#" + parentId).append('svg')
            .datum(data)
            .call(chart);

        nv.utils.windowResize(chart.update);

        this.chart = chart;
    }

    async loadData(filename) {
        var data = await d3Promise.csv(filename);
        var dataset = {};

        data.forEach(item => {
            if(typeof dataset[item.tag] === "undefined") {
                dataset[item.tag] = {key: item.tag, values: []};
            }
            dataset[item.tag].values.push({
                x: +item.date,
                y: +item.count
            });
        });

        return Object.values(dataset);
    }
}
