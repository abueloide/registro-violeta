const { override } = require('customize-cra');

module.exports = override(
  (config, env) => {
    // Configuración para desarrollo
    if (env === 'development') {
      config.devServer = {
        ...config.devServer,
        host: '0.0.0.0',
        port: 3000,
        allowedHosts: 'all',
        disableHostCheck: true,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': '*',
          'Access-Control-Allow-Headers': '*',
        },
        client: {
          webSocketURL: 'auto://0.0.0.0:0/ws'
        }
      };
    }
    return config;
  }
);