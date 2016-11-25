module.exports = {
    entry: "./js/index.js",
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
                presets: ['es2015']
            }
          }
        ]
    },
    devtool: "source-map"
}
