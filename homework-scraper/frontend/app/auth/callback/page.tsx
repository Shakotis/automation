'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardBody } from "@heroui/card";
import { Spinner } from "@heroui/spinner";
import { Chip } from "@heroui/chip";

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing authentication...');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');

      if (error) {
        setStatus('error');
        setMessage(`Authentication failed: ${error}`);
        return;
      }

      if (!code) {
        setStatus('error');
        setMessage('No authorization code received');
        return;
      }

      try {
        // Send the code to our backend for processing
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const response = await fetch(`${apiUrl}/auth/google/callback/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            code: code,
            state: state
          })
        });

        const data = await response.json();

        if (response.ok) {
          setStatus('success');
          setMessage('Authentication successful! Redirecting...');
          
          // Check if this is first login and redirect accordingly
          if (data.is_first_login) {
            setTimeout(() => router.push('/onboarding'), 2000);
          } else {
            setTimeout(() => router.push('/dashboard'), 2000);
          }
        } else {
          setStatus('error');
          setMessage(data.error || data.message || 'Authentication failed');
        }
      } catch (error) {
        setStatus('error');
        setMessage('Network error during authentication');
      }
    };

    handleCallback();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <Card className="max-w-md w-full">
        <CardBody className="text-center space-y-4">
          {status === 'loading' && (
            <>
              <Spinner size="lg" />
              <p className="text-lg font-semibold">Authenticating...</p>
              <p className="text-default-600">{message}</p>
            </>
          )}
          
          {status === 'success' && (
            <>
              <div className="text-6xl">✅</div>
              <p className="text-lg font-semibold text-success">Success!</p>
              <p className="text-default-600">{message}</p>
            </>
          )}
          
          {status === 'error' && (
            <>
              <div className="text-6xl">❌</div>
              <p className="text-lg font-semibold text-danger">Authentication Failed</p>
              <p className="text-default-600">{message}</p>
              <Chip 
                color="primary" 
                variant="flat"
                className="cursor-pointer"
                onClick={() => router.push('/')}
              >
                Return to Home
              </Chip>
            </>
          )}
        </CardBody>
      </Card>
    </div>
  );
}