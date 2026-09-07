/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "http",
        hostname: "www.veterinariahuellas.cl",
      },
      {
        protocol: "https",
        hostname: "www.veterinariahuellas.cl",
      },
    ],
  },
};

module.exports = nextConfig;
