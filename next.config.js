/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com',
    NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT || 'development',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'https://medical-ai-chatbot-backend.onrender.com'}/api/:path*`,
      },
    ];
  },
  // Handle trailing slashes
  trailingSlash: false,
  // Optimize for production
  poweredByHeader: false,
  compress: true,
}

module.exports = nextConfig
