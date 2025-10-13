'use client';

import { useState } from 'react';
import { Button } from "@heroui/button";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { authAPI } from '@/lib/api';

export default function TestAuth() {
  const [result, setResult] = useState<string>('');
  const [sessionData, setSessionData] = useState<any>(null);
  const [userData, setUserData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const testGoogleAuth = async () => {
    setLoading(true);
    setResult('Testing...');
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      console.log('Making request to:', `${apiUrl}/auth/google/login/`);
      
      const response = await fetch(`${apiUrl}/auth/google/login/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Response data:', data);
        setResult(`Success! Got authorization URL: ${data.authorization_url?.substring(0, 100)}...`);
      } else {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        setResult(`Error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('Network error:', error);
      setResult(`Network error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setLoading(false);
    }
  };

  const testSessionDebug = async () => {
    setLoading(true);
    try {
      const data = await authAPI.debugSession();
      setSessionData(data);
      setResult('Session debug data loaded');
    } catch (error: any) {
      setSessionData({ error: error.message || 'Failed to fetch session data' });
      setResult('Failed to load session debug data');
    } finally {
      setLoading(false);
    }
  };

  const testUserProfile = async () => {
    setLoading(true);
    try {
      const data = await authAPI.getUserProfile();
      setUserData(data);
      setResult('User profile loaded successfully');
    } catch (error: any) {
      setUserData({ error: error.message || 'Failed to fetch user profile' });
      setResult('Failed to load user profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Authentication Debug</h1>
      
      <div className="grid gap-6 md:grid-cols-2 mb-6">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Session Debug</h2>
          </CardHeader>
          <CardBody>
            <Button
              onPress={testSessionDebug}
              isLoading={loading}
              className="mb-4"
              color="primary"
            >
              Test Session Debug
            </Button>

            {sessionData && (
              <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-96">
                {JSON.stringify(sessionData, null, 2)}
              </pre>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">User Profile</h2>
          </CardHeader>
          <CardBody>
            <Button
              onPress={testUserProfile}
              isLoading={loading}
              className="mb-4"
              color="secondary"
            >
              Test User Profile
            </Button>

            {userData && (
              <pre className="text-xs bg-gray-100 p-4 rounded overflow-auto max-h-96">
                {JSON.stringify(userData, null, 2)}
              </pre>
            )}
          </CardBody>
        </Card>
      </div>

      <div className="space-y-4">
        <Button 
          onClick={testGoogleAuth} 
          isLoading={loading}
          color="primary"
        >
          Test Google OAuth Endpoint
        </Button>
        
        <div className="p-4 border rounded-lg bg-gray-50">
          <h3 className="font-semibold mb-2">Result:</h3>
          <pre className="whitespace-pre-wrap text-sm">{result}</pre>
        </div>
        
        <div className="p-4 border rounded-lg bg-blue-50">
          <h3 className="font-semibold mb-2">Debug Instructions:</h3>
          <ol className="list-decimal list-inside text-sm space-y-1">
            <li>Click "Test Session Debug" to see your current session state</li>
            <li>Check if "user_authenticated" is true and if you see a "sessionid" cookie</li>
            <li>If not authenticated, click "Test Google OAuth Endpoint" to start login</li>
            <li>Complete the OAuth flow, then come back and test again</li>
            <li>Check browser DevTools → Application → Cookies to see session cookies</li>
            <li>Look for CORS errors in the Network tab</li>
          </ol>
        </div>
      </div>
    </div>
  );
}