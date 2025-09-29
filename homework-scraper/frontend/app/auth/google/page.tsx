"use client";

import { useEffect, useState } from "react";
import { Card, CardBody } from "@heroui/card";
import { Button } from "@heroui/button";
import { Spinner } from "@heroui/spinner";
import { GoogleIcon } from "@/components/icons";
import { title, subtitle } from "@/components/primitives";

export default function AuthGooglePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if this is a callback from Google OAuth
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const error = urlParams.get('error');

    if (error) {
      setError('Authentication was cancelled or failed');
      return;
    }

    if (code && state) {
      handleOAuthCallback(code, state);
    }
  }, []);

  const handleOAuthCallback = async (code: string, state: string) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/auth/google/callback/?code=${code}&state=${state}`);
      const data = await response.json();

      if (response.ok) {
        // Redirect to dashboard on success
        window.location.href = '/dashboard';
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/auth/google/login/');
      const data = await response.json();

      if (response.ok && data.authorization_url) {
        // Redirect to Google OAuth
        window.location.href = data.authorization_url;
      } else {
        setError(data.error || 'Failed to initiate authentication');
      }
    } catch (err) {
      setError('Network error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md w-full">
          <CardBody className="text-center py-12">
            <Spinner size="lg" className="mb-4" />
            <h2 className="text-lg font-semibold mb-2">Authenticating...</h2>
            <p className="text-default-500">Please wait while we set up your account.</p>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 flex items-center justify-center min-h-[60vh]">
      <Card className="max-w-md w-full">
        <CardBody className="text-center py-12">
          <div className="mb-6">
            <GoogleIcon size={64} className="mx-auto mb-4" />
            <h1 className={title({ size: "sm", class: "mb-2" })}>
              Sign in with Google
            </h1>
            <p className={subtitle({ class: "text-default-500" })}>
              Connect your Google account to access Google Tasks integration
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-lg">
              <p className="text-danger-700 text-sm">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <Button
              color="primary"
              size="lg"
              onPress={handleGoogleLogin}
              isLoading={loading}
              disabled={loading}
              startContent={!loading && <GoogleIcon size={20} />}
              className="w-full"
            >
              {loading ? 'Connecting...' : 'Continue with Google'}
            </Button>

            <div className="text-xs text-default-500">
              <p>By signing in, you agree to allow this application to:</p>
              <ul className="mt-2 space-y-1 text-left">
                <li>• Access your Google Tasks</li>
                <li>• Create and manage tasks in your "Homework" task list</li>
                <li>• Read your basic profile information</li>
              </ul>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t border-default-200">
            <p className="text-xs text-default-400">
              Your data is secure and will only be used for homework management.
              You can revoke access at any time from your Google account settings.
            </p>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}