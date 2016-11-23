module.exports = {
    entry: {
        linechart: "./js/linechart.js",
        choropleth: "./js/choropleth.js"
    },
    output: {
//        filename: "[name].js",
        filename: "bundle.js",
        path: "./dist",
        library: "stacktrends"
    }
}
