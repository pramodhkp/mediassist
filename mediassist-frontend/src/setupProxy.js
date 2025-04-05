const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Add logging middleware
  app.use((req, res, next) => {
    console.log(`Request: ${req.method} ${req.path}`);
    next();
  });

  const options = {
    target: 'http://localhost:5000',
    changeOrigin: true,
    logLevel: 'debug',
    onProxyReq: (proxyReq, req, res) => {
      console.log(`Proxying ${req.method} ${req.path} to ${options.target}${req.path}`);
    }
  };

  app.use('/send_message', createProxyMiddleware(options));
  app.use('/daily_insights', createProxyMiddleware(options));
  app.use('/weekly_insights', createProxyMiddleware(options));
  app.use('/api', createProxyMiddleware(options));
};