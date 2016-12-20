import d3 from "d3";
import d3Promise from "d3.promise";


export default class {
    constructor(parentId) {
        this.container = d3.select("#" + parentId);
        this.dataset = this.loadData("data/tag_matrix.json");
        this.nodata(); // TODO remove this

        window.addEventListener(
            "tagSelectionChange",
            this.onTagSelectionChange.bind(this),
            false);
    }

    draw(dataset) {
        var outerRadius = 260,
            innerRadius = outerRadius - 150;

        var fill = d3.scale.category20c();

        var chord = d3.layout.chord()
            .padding(.04)
            .sortSubgroups(d3.descending)
            .sortChords(d3.descending);

        var arc = d3.svg.arc()
            .innerRadius(innerRadius)
            .outerRadius(innerRadius + 20);

        // Responsive SVG: http://stackoverflow.com/questions/16265123
        var svg = this.container
            .append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("preserveAspectRatio", "xMidYMid meet")
            .attr("viewBox", "0 0 400 400")
            .classed("svg-content-responsive", true)
            .append("g")
            .attr("transform", "translate(200, 200)");

        chord.matrix(dataset.data);

        var g = svg.selectAll(".group")
            .data(chord.groups)
            .enter().append("g")
            .attr("class", "group")
            .on("mouseover", this.fade(svg,.02))
            .on("mouseout", this.fade(svg,.80));

        g.append("path")
            .style("fill", d => fill(d.index))
            .style("stroke", d => fill(d.index))
            .attr("d", arc);

        g.append("text")
            .each(function(d) { d.angle = (d.startAngle + d.endAngle) / 2; })
            .attr("dy", ".35em")
            .attr("transform", function(d) {
                return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
                    + "translate(" + (innerRadius + 26) + ")"
                    + (d.angle > Math.PI ? "rotate(180)" : "");
            })
            .style("text-anchor", d => d.angle > Math.PI ? "end" : null)
            .text(d => dataset.tagByIndex[d.index]);

        svg.selectAll(".chord")
            .data(chord.chords)
            .enter().append("path")
            .attr("class", "chord")
            .style("stroke", d => d3.rgb(fill(d.source.index)).darker())
            .style("fill", d => fill(d.source.index))
            .attr("d", d3.svg.chord().radius(innerRadius));
    }

    // Returns an event handler for fading a given chord group.
    fade(svg, opacity) {
        return function(d, i) {
            svg.selectAll("path.chord")
                .filter(d => d.source.index != i && d.target.index != i)
                .transition()
                .style("stroke-opacity", opacity)
                .style("fill-opacity", opacity);
        };
    }

    clear() {
        this.container.select("svg").remove();
        this.container.select("h3").remove(); //TODO remove this later
    }

    nodata() { // TODO remove this later
        var text = this.container.append("h3");
        text.attr("style", "text-align: center;");
        text[0][0].innerHTML = "No Data Available.";
    }

    async onTagSelectionChange(event) {
        var selectedTags = event.detail;

        if(selectedTags.length > 1) {
            var data = await this.filterData(selectedTags);
            this.clear();
            this.draw(data);
        } else {
            this.clear();
            this.nodata();
        }
    }

    async filterData(tags) {
        var dataset = await this.dataset;

        var tagByIndex = Object.assign({}, tags);
        var indexByTag = tags.reduce((a, b) =>
            Object.assign(a, {[b]: Object.keys(a).length}), {});

        // Build the matrix of co-occurrences
        var matrix = [];
        tags.forEach(i => {
            var row = [];
            tags.forEach(j => {
                row.push(i == j ? 0 : dataset[i][j]);
            });
            matrix.push(row);
        });

        return {
            indexByTag: indexByTag,
            tagByIndex: tagByIndex,
            data: matrix
        };
    }

    loadData(filename) {
        return d3Promise.json(filename);
    }
}
