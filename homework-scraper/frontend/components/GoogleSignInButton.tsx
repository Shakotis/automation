'use client';

import { useState } from 'react';
import { Button } from "@heroui/button";
import { GoogleIcon } from "@/components/icons";
import { authAPI } from "@/lib/api";

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
      
      alert(`Failed to initiate Google sign-in: ${errorMessage}\n\nPlease ensure:\n1. Backend server is running (http://127.0.0.1:8000)\n2. Frontend server is running (http://localhost:3000)\n3. Check the browser console for more details`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      color="primary"
      radius="full"
      size="lg"
      variant="shadow"
      startContent={<GoogleIcon size={20} />}
      onPress={handleGoogleSignIn}
      isLoading={isLoading}
    >
      {isLoading ? 'Connecting...' : 'Sign in with Google'}
    </Button>
  );
}