'use client';

import { useState } from 'react';
import { authAPI } from "@/lib/api";

/**
 * Google Sign-In Button Component
 * 
 * Compliant with Google's Branding Guidelines:
 * https://developers.google.com/identity/branding-guidelines
 * 
 * Features:
 * - Official Google "G" logo (standard colors)
 * - Roboto Medium font
 * - Proper padding and sizing
 * - Light and dark mode support
 * - Loading state
 */
export default function GoogleSignInButton() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    try {
      const data = await authAPI.getGoogleAuthUrl();
      // Redirect to Google OAuth URL
      window.location.href = data.authorization_url;
    } catch (error) {
      console.error('[GoogleSignIn] Failed to get auth URL:', error);
      
      const errorMessage = error instanceof Error 
        ? error.message 
        : 'Unknown error occurred';
      
      alert(`Failed to initiate Google sign-in: ${errorMessage}\n\nPlease ensure:\n1. Backend server is running\n2. Check the browser console for more details`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleGoogleSignIn}
      disabled={isLoading}
      className="group relative inline-flex items-center justify-center gap-3 px-6 py-3 
                 bg-white dark:bg-[#131314] 
                 border border-[#747775] dark:border-[#8E918F]
                 rounded-full
                 text-[#1F1F1F] dark:text-[#E3E3E3]
                 font-medium text-base
                 hover:bg-[#F8F9FA] dark:hover:bg-[#1F1F1F]
                 active:bg-[#E8EAED] dark:active:bg-[#2C2C2C]
                 disabled:opacity-60 disabled:cursor-not-allowed
                 transition-all duration-200
                 shadow-sm hover:shadow-md
                 min-w-[200px]"
      style={{ fontFamily: "'Roboto', sans-serif" }}
      aria-label="Sign in with Google"
    >
      {/* Official Google "G" Logo - Standard Colors */}
      {!isLoading && (
        <svg 
          width="20" 
          height="20" 
          viewBox="0 0 48 48" 
          xmlns="http://www.w3.org/2000/svg"
          className="flex-shrink-0"
        >
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
          <path fill="none" d="M0 0h48v48H0z"/>
        </svg>
      )}
      
      {/* Loading Spinner */}
      {isLoading && (
        <svg 
          className="animate-spin h-5 w-5 flex-shrink-0" 
          xmlns="http://www.w3.org/2000/svg" 
          fill="none" 
          viewBox="0 0 24 24"
        >
          <circle 
            className="opacity-25" 
            cx="12" 
            cy="12" 
            r="10" 
            stroke="currentColor" 
            strokeWidth="4"
          />
          <path 
            className="opacity-75" 
            fill="currentColor" 
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      
      {/* Button Text - Roboto Medium Font */}
      <span className="font-medium text-base whitespace-nowrap">
        {isLoading ? 'Signing in...' : 'Sign in with Google'}
      </span>
    </button>
  );
}