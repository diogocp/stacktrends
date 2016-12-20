import d3 from "d3";
import d3Promise from "d3.promise";
import nv from "nvd3";


export default class {
    constructor(parentId) {
        this.dataset = this.loadData("data/tag_year.csv");
        this.container = parentId;
        this.draw();
        window.addEventListener(
                "tagSelectionChange",
                this.onTagSelectionChange.bind(this),
                false);
    }

    draw() {
        var container = this.container;

        nv.addGraph(function() {
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
                    return d3.format(',.3f')(d);
                });

            chart.tooltip.contentGenerator(obj =>
                `<table>
                   <thead><tr>
                     <td colspan="3">
                       <strong class="x-value">${obj.point.x}</strong>
                     </td></tr>
                   </thead>
                   <tbody><tr>
                     <td class="legend-color-guide">
                       <div style="background-color: ${obj.point.color};">
                       </div>
                     </td>
                     <td class="key">
                       ${obj.series[0].key}
                    </td>
                     <td class="value">
                       ${d3.format(",")(obj.point.count)}
                     </td></tr>
                   </tbody>
                 </table>`
            )

            d3.select("#" + container)
                .append("svg")
                .datum([])
                .call(chart);

            nv.utils.windowResize(chart.update);

            return chart;
        },
        chart => {
            this.chart = chart;
        });
    }

    async onTagSelectionChange(event) {
        var selectedTags = event.detail;

        var data = (await this.dataset)
            .filter(item => selectedTags.indexOf(item.key) != -1);

        d3.select("#" + this.container)
            .select("svg")
            .datum(data)
            .call(this.chart);
    }

    async loadData(filename) {
        var data = await d3Promise.csv(filename);
        var dataset = {};

        data.forEach(item => {
            if(typeof dataset[item.tag] === "undefined") {
                dataset[item.tag] = {key: item.tag, values: []};
            }
            dataset[item.tag].values.push({
                x: +item.year,
                y: +item.pct,
                count: +item.count
            });
        });

        return Object.values(dataset);
    }
}
