// webpack.config.js
const path = require('path');

module.exports = {
  entry: './src/index.js', // Your React entry point
  output: {
    path: path.resolve(__dirname, 'src', 'assets', 'js', 'core'),
    filename: 'bundle.js', // Output file bundled by Webpack
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/, // Match JS and JSX files
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  mode: 'development',
};
