'use client';

import { useState } from 'react';

// Get API base URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';
console.log('[Test API] Using API_BASE_URL:', API_BASE_URL);

export default function TestAPIPage() {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    setResult('Testing...');
    
    try {
      console.log('Starting fetch test...');
      const response = await fetch(`${API_BASE_URL}/auth/google/login`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      console.log('Response received:', response);
      const data = await response.json();
      console.log('Data:', data);
      
      setResult(JSON.stringify(data, null, 2));
    } catch (error) {
      console.error('Error:', error);
      setResult(`Error: ${error instanceof Error ? error.message : 'Unknown error'}\n\nType: ${typeof error}\nConstructor: ${error?.constructor?.name}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>API Test Page</h1>
      <button 
        onClick={testAPI}
        disabled={loading}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          cursor: loading ? 'not-allowed' : 'pointer',
          backgroundColor: loading ? '#ccc' : '#0070f3',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
        }}
      >
        {loading ? 'Testing...' : 'Test API Call'}
      </button>
      
      <pre style={{
        marginTop: '20px',
        padding: '10px',
        backgroundColor: '#f5f5f5',
        borderRadius: '5px',
        overflow: 'auto',
        maxHeight: '400px',
      }}>
        {result || 'Click the button to test the API'}
      </pre>
      
      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <p><strong>Test Details:</strong></p>
        <ul>
          <li>Endpoint: /api/auth/google/login/</li>
          <li>Method: GET</li>
          <li>Expected: JSON with authorization_url</li>
        </ul>
      </div>
    </div>
  );
}
