function loadMapData() {
    var d3 = require("d3");
    var d3Promise = require("d3.promise");

    // Load data from CSV
    return d3Promise.csv("data/country_tag.csv")
    .then(function(data) {
        // Prepare the dataset
        var dataset = {};
        data.forEach(function(item) {
            if(typeof dataset[item.tag] === "undefined") {
                dataset[item.tag] = {};
            }
            dataset[item.tag][item.country] = +item.count;
        });

        for(var tag in dataset) {
            // Create color palette
            var minCount = Math.min.apply(null, Object.values(dataset[tag]));
            var maxCount = Math.max.apply(null, Object.values(dataset[tag]));
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

function drawMap(elementId) {
    var Datamap = require("datamaps");

    var map = new Datamap({
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
                // don't show tooltip if country not present in dataset
                if (!data) { return ; }
                // tooltip content
                return ['<div class="hoverinfo">',
                '<strong>', geo.properties.name, '</strong>',
                '<br>Count: <strong>', data.count, '</strong>',
                '</div>'].join('');
            }
        }
    });

    return map;
}

module.exports = {loadMapData, drawMap};
