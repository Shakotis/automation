/** @type {import('next').NextConfig} */
const nextConfig = {
  // Removed rewrites - using API route handler instead (app/api/[...path]/route.ts)
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },
  
  // Output configuration for static export (optional)
  // output: 'export', // Use this for static export if needed
  
  // Image optimization (Netlify supports Next.js Image Optimization)
  images: {
    domains: ['localhost'],
    unoptimized: false, // Set to true if you want to disable image optimization
  },
  
  // Netlify-specific optimizations
  eslint: {
    ignoreDuringBuilds: false, // Change to true if you want to ignore ESLint errors during build
  },
  typescript: {
    ignoreBuildErrors: false, // Change to true if you want to ignore TypeScript errors during build
  },
};

export default nextConfig;
