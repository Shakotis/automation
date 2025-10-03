'use client';

import { useEffect, useState } from 'react';

export default function APIDebugPage() {
  const [diagnostics, setDiagnostics] = useState<any>({});
  const [testResult, setTestResult] = useState<string>('');

  useEffect(() => {
    const info = {
      windowExists: typeof window !== 'undefined',
      currentURL: typeof window !== 'undefined' ? window.location.href : 'N/A',
      origin: typeof window !== 'undefined' ? window.location.origin : 'N/A',
      hostname: typeof window !== 'undefined' ? window.location.hostname : 'N/A',
      port: typeof window !== 'undefined' ? window.location.port : 'N/A',
      protocol: typeof window !== 'undefined' ? window.location.protocol : 'N/A',
      apiBaseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
      nodeEnv: process.env.NODE_ENV,
    };
    setDiagnostics(info);
  }, []);

  const testFetch = async () => {
    setTestResult('Testing...');
    
    try {
      console.log('=== FETCH TEST START ===');
      const testURL = '/api/auth/sites/';
      console.log('Test URL:', testURL);
      console.log('Absolute URL:', new URL(testURL, window.location.origin).href);
      
      const response = await fetch(testURL, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      console.log('Response:', response);
      console.log('Status:', response.status);
      console.log('OK:', response.ok);
      
      const data = await response.json();
      console.log('Data:', data);
      
      setTestResult(`✅ SUCCESS\n\nStatus: ${response.status}\n\nData:\n${JSON.stringify(data, null, 2)}`);
    } catch (error) {
      console.error('=== FETCH TEST ERROR ===');
      console.error('Error:', error);
      console.error('Error type:', typeof error);
      console.error('Error constructor:', error?.constructor?.name);
      console.error('Error message:', error instanceof Error ? error.message : 'Unknown');
      console.error('Error stack:', error instanceof Error ? error.stack : 'No stack');
      
      setTestResult(`❌ ERROR\n\nType: ${typeof error}\nConstructor: ${error?.constructor?.name}\nMessage: ${error instanceof Error ? error.message : 'Unknown'}\n\nFull error: ${JSON.stringify(error, null, 2)}`);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'system-ui', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>
        API Diagnostics
      </h1>
      
      <div style={{ backgroundColor: '#f5f5f5', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '10px' }}>Environment Info</h2>
        <pre style={{ fontSize: '12px', overflow: 'auto' }}>
          {JSON.stringify(diagnostics, null, 2)}
        </pre>
      </div>

      <button
        onClick={testFetch}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          backgroundColor: '#0070f3',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          marginBottom: '20px',
        }}
      >
        Test Fetch to /api/auth/sites/
      </button>

      {testResult && (
        <div style={{
          backgroundColor: testResult.startsWith('✅') ? '#d4edda' : '#f8d7da',
          padding: '15px',
          borderRadius: '8px',
          border: `1px solid ${testResult.startsWith('✅') ? '#c3e6cb' : '#f5c6cb'}`,
        }}>
          <pre style={{ fontSize: '12px', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {testResult}
          </pre>
        </div>
      )}

      <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#e7f3ff', borderRadius: '8px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '10px' }}>Instructions</h3>
        <ol style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
          <li>Open browser DevTools (F12)</li>
          <li>Go to the Console tab</li>
          <li>Click the "Test Fetch" button above</li>
          <li>Check both the result on this page AND the console logs</li>
          <li>If it fails, check the console for detailed error information</li>
        </ol>
      </div>
    </div>
  );
}
