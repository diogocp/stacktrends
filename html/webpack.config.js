module.exports = {
    entry: {
        choropleth: "./js/choropleth.js"
    },
    output: {
//        filename: "[name].js",
        filename: "bundle.js",
        path: "./dist",
        library: "stacktrends"
    }
}
