'use client';

import { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";

export default function TestConnection() {
  const [testResult, setTestResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const testAPI = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/test/', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setTestResult(data);
      } else {
        setTestResult({ 
          status: 'error', 
          message: `HTTP ${response.status}: ${response.statusText}` 
        });
      }
    } catch (error) {
      setTestResult({ 
        status: 'error', 
        message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}` 
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    testAPI();
  }, []);

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Card>
        <CardHeader>
          <h1 className="text-2xl font-bold">API Connection Test</h1>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <Button 
              color="primary" 
              onPress={testAPI}
              isLoading={isLoading}
            >
              {isLoading ? 'Testing...' : 'Test API Connection'}
            </Button>
            
            {testResult && (
              <Card className={testResult.status === 'success' ? 'border-success' : 'border-danger'}>
                <CardBody>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <strong>Status:</strong>
                      <Chip 
                        color={testResult.status === 'success' ? 'success' : 'danger'}
                        variant="flat"
                      >
                        {testResult.status}
                      </Chip>
                    </div>
                    
                    <div><strong>Message:</strong> {testResult.message}</div>
                    
                    {testResult.django_running !== undefined && (
                      <div className="flex items-center gap-2">
                        <strong>Django Backend:</strong>
                        <Chip 
                          color={testResult.django_running ? 'success' : 'danger'}
                          variant="flat"
                        >
                          {testResult.django_running ? 'Running' : 'Not Running'}
                        </Chip>
                      </div>
                    )}
                    
                    {testResult.google_oauth_configured !== undefined && (
                      <div className="flex items-center gap-2">
                        <strong>Google OAuth:</strong>
                        <Chip 
                          color={testResult.google_oauth_configured ? 'success' : 'warning'}
                          variant="flat"
                        >
                          {testResult.google_oauth_configured ? 'Configured' : 'Not Configured'}
                        </Chip>
                      </div>
                    )}
                  </div>
                </CardBody>
              </Card>
            )}
          </div>
          
          <div className="mt-6 p-4 bg-default-100 rounded-lg">
            <h3 className="font-semibold mb-2">Troubleshooting:</h3>
            <ul className="text-sm space-y-1">
              <li>• Django backend should be running on http://localhost:8000</li>
              <li>• Google OAuth credentials need to be configured in .env file</li>
              <li>• Check browser developer tools for detailed error messages</li>
            </ul>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}