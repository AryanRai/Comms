// webpack.config.js
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
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
