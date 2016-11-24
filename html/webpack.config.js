module.exports = {
    entry: "./js/index.js",
    output: {
//        filename: "[name].js",
        filename: "bundle.js",
        path: "./dist",
        publicPath: "/dist/",
        library: "stacktrends"
    }
}
