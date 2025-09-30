'use client';

import { useState } from 'react';
import { Button } from "@heroui/button";

export default function TestAuth() {
  const [result, setResult] = useState<string>('');
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

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Test Google Authentication</h1>
      
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
          <h3 className="font-semibold mb-2">Instructions:</h3>
          <ol className="list-decimal list-inside text-sm space-y-1">
            <li>Open browser developer tools (F12)</li>
            <li>Go to the Console tab</li>
            <li>Click the "Test Google OAuth Endpoint" button</li>
            <li>Check for any error messages in the console</li>
            <li>Look for CORS or network errors</li>
          </ol>
        </div>
      </div>
    </div>
  );
}