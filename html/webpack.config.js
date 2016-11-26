module.exports = {
    entry: ["babel-polyfill", "./js/index.js"],
    output: {
        filename: "bundle.js",
        path: "./dist",
        publicPath: "/dist/",
        library: "stacktrends"
    },
    module: {
        loaders: [
          {
            test: /\.js$/,
            exclude: /node_modules/,
            loader: "babel-loader",
            query: {
                presets: ["es2015"],
                plugins: ["transform-async-to-generator"]
            }
          }
        ]
    },
    devtool: "source-map"
}
