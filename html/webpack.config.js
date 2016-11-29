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
                plugins: [
                    ["transform-async-to-generator"],
                    ["transform-es2015-template-literals"]
                ]
            }
          },
          {
              test: /\.json$/,
              loader: "json"
          },
          { // Chosen needs jQuery in the global namespace
              test: /chosen-js\/.+\.(jsx|js)$/,
              loader: "imports?jQuery=jquery,$=jquery,this=>window"
          },
          { test: /\.css$/, loader: "style-loader!css-loader" },
          { test: /\.png$/, loader: "url-loader?limit=100000" }
        ]
    },
    devtool: "source-map"
}
