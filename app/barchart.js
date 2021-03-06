import d3 from "d3";
import d3Promise from "d3.promise";
import nv from "nvd3";


export default class {
    constructor(parentId) {
        this.dataset = this.loadData("data/country_tag.csv");
        this.container = d3.select("#" + parentId);
        this.selectedCountry = "XXX";
        this.draw();
        window.addEventListener(
                "tagSelectionChange",
                this.onTagSelectionChange.bind(this),
                false);
        window.addEventListener(
                "countryClick",
                this.onCountryClick.bind(this),
                false);
    }

    draw() {
        var container = this.container;

        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function(d) { return d.tag })
                .y(function(d) { return d.count })
                .showValues(true)
                .duration(500);

            chart.valueFormat(d3.format(",.0f"));

            chart.yAxis
                .axisLabel("Number of posts")
                .tickValues(false)
                .showMaxMin(false);

            chart.tooltip.contentGenerator(obj =>
                `<table><tbody><tr>
                   <td class="legend-color-guide">
                     <div style="background-color: ${obj.color};"></div>
                   </td>
                   <td class="key">${obj.data.tag}</td>
                   <td class="value">${d3.format("0.3%")(obj.data.freq)}</td>
                 </tr></tbody></table>`
            )

            container.append("svg").datum([]).call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        },
        chart => {
            chart.discretebar.dispatch.on("elementClick", event => {
                window.dispatchEvent(new CustomEvent(
                            "primaryTagChange", {
                                detail: event.data.tag
                            }));
            });
            return this.chart = chart;
        });
    }

    async update() {
        var data = await this.filterData(this.selectedCountry,
                this.selectedTags);

        // Stagger labels when there are more than 8 bars
        if(data.length) {
            this.chart.staggerLabels(data[0].values.length > 8);
        }

        this.container
            .select("svg")
            .datum(data)
            .call(this.chart);
    }

    onTagSelectionChange(event) {
        this.selectedTags = event.detail;
        this.update();
    }

    onCountryClick(event) {
        this.selectedCountry = event.detail;
        this.update();
    }

    async filterData(country, tags) {
        if(!country || !tags) {
            return [];
        }

        var dataset = await this.dataset;

        if(!dataset[country]) {
            return [];
        }

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
                count: +item.count,
                freq: +item.freq
            });
        });

        return dataset;
    }
}
