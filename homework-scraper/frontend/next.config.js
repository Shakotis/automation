import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Removed rewrites - using API route handler instead (app/api/[...path]/route.ts)
  
  // Fix workspace root detection
  outputFileTracingRoot: path.join(__dirname, '../'),
  
  // Output configuration for static export (Netlify compatible)
  output: 'export',
  
  // Disable features not compatible with static export
  images: {
    unoptimized: true, // Required for static export
  },
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  },
  
  // Trailing slash for better static hosting compatibility
  trailingSlash: true,
  
  // Netlify-specific optimizations
  eslint: {
    ignoreDuringBuilds: false, // Change to true if you want to ignore ESLint errors during build
  },
  typescript: {
    ignoreBuildErrors: false, // Change to true if you want to ignore TypeScript errors during build
  },
};

export default nextConfig;
