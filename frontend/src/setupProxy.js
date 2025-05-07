const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy all /api requests to the Flask backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://172.16.16.6:5004',
      changeOrigin: true,
      secure: false,
      pathRewrite: {
        '^/api': '/api', // Keep the /api prefix
      },
      // This is important for cookie handling
      cookieDomainRewrite: {
        '*': '172.16.16.6'  // Rewrite all cookie domains to backend IP
      },
      // Pass cookies from the frontend to the backend
      onProxyReq: (proxyReq) => {
        // Log proxy requests for debugging
        console.log(`Proxying ${proxyReq.method} ${proxyReq.path} to ${proxyReq.protocol}//${proxyReq.host}${proxyReq.path}`);
      },
      // Ensure all cookies from backend are passed to frontend
      onProxyRes: (proxyRes) => {
        // Log proxy responses for debugging
        console.log(`Proxy response status: ${proxyRes.statusCode}`);
      }
    })
  );
}; 