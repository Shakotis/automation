'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Stepper, { Step } from '@/components/ui/stepper';
import { Button } from '@heroui/button';
import { Input } from '@heroui/input';
import { Card, CardBody, CardHeader } from '@heroui/card';
import { Checkbox } from '@heroui/checkbox';

export default function OnboardingPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    examInCalendar: true,
    examInTasks: true,
    selectedApps: [] as string[],
    edukaUsername: '',
    edukaPassword: '',
    manoDienynasUsername: '',
    manoDienynasPassword: '',
  });

  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<{
    eduka?: 'success' | 'error';
    manodienynas?: 'success' | 'error';
  }>({});

  const handleAppToggle = (app: string) => {
    setFormData(prev => ({
      ...prev,
      selectedApps: prev.selectedApps.includes(app)
        ? prev.selectedApps.filter(a => a !== app)
        : [...prev.selectedApps, app]
    }));
  };

  const handleVerifyCredentials = async () => {
    setIsVerifying(true);
    setVerificationStatus({});

    try {
      // Verify Eduka credentials if selected
      if (formData.selectedApps.includes('eduka') && formData.edukaUsername && formData.edukaPassword) {
        const edukaResponse = await fetch('/api/verify-credentials', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            platform: 'eduka',
            username: formData.edukaUsername,
            password: formData.edukaPassword,
          }),
        });

        setVerificationStatus(prev => ({
          ...prev,
          eduka: edukaResponse.ok ? 'success' : 'error'
        }));
      }

      // Verify Mano Dienynas credentials if selected
      if (formData.selectedApps.includes('manodienynas') && formData.manoDienynasUsername && formData.manoDienynasPassword) {
        const manoResponse = await fetch('/api/verify-credentials', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            platform: 'manodienynas',
            username: formData.manoDienynasUsername,
            password: formData.manoDienynasPassword,
          }),
        });

        setVerificationStatus(prev => ({
          ...prev,
          manodienynas: manoResponse.ok ? 'success' : 'error'
        }));
      }
    } catch (error) {
      console.error('Verification error:', error);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleComplete = async () => {
    // Save preferences and redirect to dashboard
    await fetch('/api/save-onboarding', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto py-8 px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Welcome to Homework Scraper! 🎓</h1>
          <p className="text-gray-600 dark:text-gray-400">Let&apos;s get you set up in just a few steps</p>
        </div>

        <Stepper
          initialStep={1}
          onFinalStepCompleted={handleComplete}
          nextButtonText="Continue"
          backButtonText="Back"
        >
          {/* Step 1: Google Tasks Explanation */}
          <Step>
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold mb-4">📱 Google Tasks Integration</h2>
              
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-medium">Why Google Tasks?</h3>
                </CardHeader>
                <CardBody className="space-y-4">
                  <p className="text-gray-700 dark:text-gray-300">
                    Homework Scraper automatically syncs your assignments to Google Tasks, giving you:
                  </p>
                  
                  <ul className="list-disc list-inside space-y-2 text-gray-600 dark:text-gray-400">
                    <li>✅ Access to homework from any device</li>
                    <li>🔔 Smart notifications and reminders</li>
                    <li>📊 Progress tracking and completion history</li>
                    <li>🔄 Real-time sync across all your devices</li>
                    <li>📅 Integration with Google Calendar</li>
                  </ul>

                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mt-4">
                    <p className="text-sm font-medium mb-2">📝 Quick Setup:</p>
                    <ol className="list-decimal list-inside space-y-1 text-sm text-gray-700 dark:text-gray-300">
                      <li>We&apos;ll ask you to authorize Google Tasks access</li>
                      <li>Your homework will automatically appear in tasks</li>
                      <li>Check off assignments as you complete them</li>
                      <li>All done! 🎉</li>
                    </ol>
                  </div>

                  <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border-l-4 border-yellow-400">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      <strong>Privacy Note:</strong> We only access your Google Tasks to add and update homework assignments. 
                      We never read your personal tasks or access other Google services.
                    </p>
                  </div>
                </CardBody>
              </Card>
            </div>
          </Step>

          {/* Step 2: Exam Dates Preferences */}
          <Step>
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold mb-4">📅 Exam Date Preferences</h2>
              
              <Card>
                <CardBody className="space-y-6">
                  <p className="text-gray-700 dark:text-gray-300">
                    Where would you like to see your upcoming exams?
                  </p>

                  <div className="space-y-4">
                    <Checkbox
                      isSelected={formData.examInCalendar}
                      onValueChange={(checked) => 
                        setFormData(prev => ({ ...prev, examInCalendar: checked }))
                      }
                    >
                      <div>
                        <p className="font-medium">Add to Google Calendar 📆</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Exams will appear as calendar events with reminders
                        </p>
                      </div>
                    </Checkbox>

                    <Checkbox
                      isSelected={formData.examInTasks}
                      onValueChange={(checked) => 
                        setFormData(prev => ({ ...prev, examInTasks: checked }))
                      }
                    >
                      <div>
                        <p className="font-medium">Add to Google Tasks ✅</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Exams will appear as tasks alongside your homework
                        </p>
                      </div>
                    </Checkbox>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      💡 <strong>Tip:</strong> We recommend enabling both options for maximum visibility of important exam dates!
                    </p>
                  </div>
                </CardBody>
              </Card>
            </div>
          </Step>

          {/* Step 3: App Selection */}
          <Step>
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold mb-4">🏫 Select Your School Apps</h2>
              
              <Card>
                <CardBody className="space-y-6">
                  <p className="text-gray-700 dark:text-gray-300">
                    Which platforms does your school use? (Select all that apply)
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card
                      isPressable
                      isHoverable
                      className={`cursor-pointer transition-all ${
                        formData.selectedApps.includes('eduka')
                          ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                      onPress={() => handleAppToggle('eduka')}
                    >
                      <CardBody className="text-center p-6">
                        <div className="text-4xl mb-2">📚</div>
                        <h3 className="text-lg font-semibold mb-1">Eduka</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          E-diary system for Lithuanian schools
                        </p>
                        {formData.selectedApps.includes('eduka') && (
                          <div className="mt-3 text-blue-500 font-medium">✓ Selected</div>
                        )}
                      </CardBody>
                    </Card>

                    <Card
                      isPressable
                      isHoverable
                      className={`cursor-pointer transition-all ${
                        formData.selectedApps.includes('manodienynas')
                          ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-900/20'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}
                      onPress={() => handleAppToggle('manodienynas')}
                    >
                      <CardBody className="text-center p-6">
                        <div className="text-4xl mb-2">📖</div>
                        <h3 className="text-lg font-semibold mb-1">Mano Dienynas</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Popular e-diary platform in Lithuania
                        </p>
                        {formData.selectedApps.includes('manodienynas') && (
                          <div className="mt-3 text-green-500 font-medium">✓ Selected</div>
                        )}
                      </CardBody>
                    </Card>
                  </div>

                  {formData.selectedApps.length === 0 && (
                    <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg text-center">
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        ⚠️ Please select at least one platform to continue
                      </p>
                    </div>
                  )}
                </CardBody>
              </Card>
            </div>
          </Step>

          {/* Step 4: Credentials Input & Verification */}
          <Step>
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold mb-4">🔐 Enter Your Credentials</h2>
              
              <Card>
                <CardBody className="space-y-6">
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      🔒 <strong>Your credentials are secure:</strong> All passwords are encrypted and stored securely. 
                      We only use them to log in and fetch your homework.
                    </p>
                  </div>

                  {formData.selectedApps.includes('eduka') && (
                    <div className="space-y-3">
                      <h3 className="font-semibold text-lg flex items-center gap-2">
                        📚 Eduka Credentials
                        {verificationStatus.eduka === 'success' && (
                          <span className="text-green-500 text-sm">✓ Verified</span>
                        )}
                        {verificationStatus.eduka === 'error' && (
                          <span className="text-red-500 text-sm">✗ Failed</span>
                        )}
                      </h3>
                      <Input
                        label="Username"
                        placeholder="Enter your Eduka username"
                        value={formData.edukaUsername}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, edukaUsername: e.target.value }))
                        }
                      />
                      <Input
                        label="Password"
                        type="password"
                        placeholder="Enter your Eduka password"
                        value={formData.edukaPassword}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, edukaPassword: e.target.value }))
                        }
                      />
                    </div>
                  )}

                  {formData.selectedApps.includes('manodienynas') && (
                    <div className="space-y-3">
                      <h3 className="font-semibold text-lg flex items-center gap-2">
                        📖 Mano Dienynas Credentials
                        {verificationStatus.manodienynas === 'success' && (
                          <span className="text-green-500 text-sm">✓ Verified</span>
                        )}
                        {verificationStatus.manodienynas === 'error' && (
                          <span className="text-red-500 text-sm">✗ Failed</span>
                        )}
                      </h3>
                      <Input
                        label="Username"
                        placeholder="Enter your Mano Dienynas username"
                        value={formData.manoDienynasUsername}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, manoDienynasUsername: e.target.value }))
                        }
                      />
                      <Input
                        label="Password"
                        type="password"
                        placeholder="Enter your Mano Dienynas password"
                        value={formData.manoDienynasPassword}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, manoDienynasPassword: e.target.value }))
                        }
                      />
                    </div>
                  )}

                  <Button
                    color="primary"
                    onClick={handleVerifyCredentials}
                    isLoading={isVerifying}
                    className="w-full"
                  >
                    {isVerifying ? 'Verifying...' : 'Verify Credentials'}
                  </Button>

                  {Object.keys(verificationStatus).length > 0 && (
                    <div className="space-y-2">
                      {verificationStatus.eduka === 'success' && (
                        <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg text-green-700 dark:text-green-300">
                          ✓ Eduka credentials verified successfully!
                        </div>
                      )}
                      {verificationStatus.eduka === 'error' && (
                        <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-red-700 dark:text-red-300">
                          ✗ Eduka verification failed. Please check your credentials.
                        </div>
                      )}
                      {verificationStatus.manodienynas === 'success' && (
                        <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg text-green-700 dark:text-green-300">
                          ✓ Mano Dienynas credentials verified successfully!
                        </div>
                      )}
                      {verificationStatus.manodienynas === 'error' && (
                        <div className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg text-red-700 dark:text-red-300">
                          ✗ Mano Dienynas verification failed. Please check your credentials.
                        </div>
                      )}
                    </div>
                  )}
                </CardBody>
              </Card>
            </div>
          </Step>
        </Stepper>
      </div>
    </div>
  );
}