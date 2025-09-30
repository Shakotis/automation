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
      console.error('Network error:', error);
      alert('Network error occurred. Please check if the backend server is running on http://localhost:8000');
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