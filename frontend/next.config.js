/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_URL: process.env.API_URL || 'http://localhost:3100',
    WEBSOCKET_URL: process.env.WEBSOCKET_URL || 'ws://localhost:3100/ws',
  },
  // Configure server-to-client API calls
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.API_URL ? `${process.env.API_URL}/api/:path*` : 'http://localhost:3100/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig 