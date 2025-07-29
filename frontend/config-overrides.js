const { override, addWebpackPlugin } = require('customize-cra');

module.exports = override(
  (config) => {
    config.devServer = {
      ...config.devServer,
      host: '0.0.0.0',
      port: 3000,
      allowedHosts: 'all',
      disableHostCheck: true,
    };
    return config;
  }
);