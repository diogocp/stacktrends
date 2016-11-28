import d3 from "d3";
import d3Promise from "d3.promise";
import Datamap from "datamaps";


export default class {
    constructor(elementId) {
        this.dataset = this.loadData("data/country_tag.csv");

        this.map = new Datamap({
            element: document.getElementById(elementId),
            projection: "mercator",
            fills: { defaultFill: "#f5f5f5" },
            geographyConfig: {
                borderColor: "#dedede",
                highlightBorderWidth: 2,
                // don't change color on mouse hover
                //            highlightFillColor: function(geo) {
                //                return geo["fillColor"] || "#f5f5f5";
                //            },
                // only change border
                highlightBorderColor: '#b7b7b7',
                // show desired information in tooltip
                popupTemplate: function(geo, data) {
                    var count = data.count || "N/A";
                    return `<div class="hoverinfo">
                        <strong>${geo.properties.name}</strong>
                        <br>Count: <strong>${count}</strong>
                        </div>`;
                }
            },
            done: function(datamap) {
                datamap.svg
                    .selectAll(".datamaps-subunit")
                    .on("click", function(geography) {
                        window.dispatchEvent(
                                new CustomEvent(
                                    "countryClick",
                                    {detail: geography.id}
                                    )
                                );
                    });
            }
        });

        window.addEventListener(
                "primaryTagChange",
                this.onPrimaryTagChange.bind(this),
                false);
    }

    onPrimaryTagChange(event) {
        this.update(event.detail);
        document.getElementById("tag-input").value = event.detail; //FIXME
    }

    async update(tag) {
        var data = (await this.dataset)[tag];

        if(data === undefined) {
            this.map.updateChoropleth(null, {reset: true});
        } else {
            this.map.updateChoropleth(data, {reset: true});
        }
    }

    loadData(filename) {
        // Load data from CSV
        return d3Promise.csv(filename).then(data => {
            // Prepare the dataset
            var dataset = {};
            data.forEach(item => {
                if(typeof dataset[item.tag] === "undefined") {
                    dataset[item.tag] = {};
                }
                dataset[item.tag][item.country] = +item.count;
            });

            for(var tag in dataset) {
                // Create color palette
                var values = Object.values(dataset[tag]);
                var minCount = Math.min.apply(null, values);
                var maxCount = Math.max.apply(null, values);
                var paletteScale = d3.scale.linear()
                    .domain([minCount, maxCount])
                    .range(["#fee5d9", "#a50f15"]);

                // Set color for each country
                for(var country in dataset[tag]) {
                    dataset[tag][country] = {
                        count: dataset[tag][country],
                        fillColor: paletteScale(dataset[tag][country])
                    }
                }
            }
            return dataset;
        });
    }
}
