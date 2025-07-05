/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '10mb',
    },
    serverComponentsExternalPackages: ['@ai-sdk/openai', '@ai-sdk/anthropic'],
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  webpack: (config, { dev, isServer }) => {
    // Monaco Editor support
    config.module.rules.push({
      test: /\.worker\.js$/,
      use: { loader: 'worker-loader' },
    });

    // Handle .node files for MCP client
    config.module.rules.push({
      test: /\.node$/,
      use: 'raw-loader',
    });

    // Optimize for WebAssembly
    config.experiments = {
      ...config.experiments,
      asyncWebAssembly: true,
    };

    return config;
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Cross-Origin-Embedder-Policy',
            value: 'require-corp',
          },
          {
            key: 'Cross-Origin-Opener-Policy',
            value: 'same-origin',
          },
        ],
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: `${process.env.BACKEND_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;