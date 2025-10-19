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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-indigo-950 dark:to-purple-950">
      <div className="container mx-auto py-12 px-4 max-w-4xl">
        <div className="text-center mb-12">
          <div className="inline-block mb-4 p-4 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full">
            <span className="text-6xl">🎓</span>
          </div>
          <h1 className="text-5xl font-extrabold mb-4 bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
            Welcome to Homework Scraper!
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Let&apos;s get you set up in just a few simple steps and start automating your homework tracking
          </p>
        </div>

        <Stepper
          initialStep={1}
          onFinalStepCompleted={handleComplete}
          nextButtonText="Continue"
          backButtonText="Back"
        >
          {/* Step 1: Google Tasks Explanation */}
          <Step>
            <div className="space-y-6">
              <div className="text-center mb-6">
                <div className="inline-block p-4 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-2xl mb-4">
                  <span className="text-6xl">📱</span>
                </div>
                <h2 className="text-3xl font-bold mb-2 text-gray-800 dark:text-white">Google Tasks Integration</h2>
                <p className="text-gray-600 dark:text-gray-300">Your homework, always at your fingertips</p>
              </div>
              
              <Card className="border-2 border-blue-100 dark:border-blue-900/30 shadow-xl">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-white">✨ Why Google Tasks?</h3>
                </CardHeader>
                <CardBody className="space-y-6">
                  <p className="text-lg text-gray-700 dark:text-gray-300">
                    Homework Scraper automatically syncs your assignments to Google Tasks, giving you seamless access to all your schoolwork:
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-start space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                      <span className="text-2xl">✅</span>
                      <div>
                        <p className="font-semibold text-gray-800 dark:text-white">Multi-Device Access</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Check homework from any device, anywhere</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                      <span className="text-2xl">🔔</span>
                      <div>
                        <p className="font-semibold text-gray-800 dark:text-white">Smart Notifications</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Never miss a deadline again</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                      <span className="text-2xl">📊</span>
                      <div>
                        <p className="font-semibold text-gray-800 dark:text-white">Progress Tracking</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">See what&apos;s done and what&apos;s pending</p>
                      </div>
                    </div>
                    
                    <div className="flex items-start space-x-3 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                      <span className="text-2xl">🔄</span>
                      <div>
                        <p className="font-semibold text-gray-800 dark:text-white">Real-Time Sync</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Instant updates across all devices</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 p-5 rounded-xl border-l-4 border-blue-500">
                    <p className="font-semibold mb-3 text-gray-800 dark:text-white flex items-center">
                      <span className="text-2xl mr-2">📝</span>
                      Quick & Easy Setup:
                    </p>
                    <ol className="space-y-2 text-gray-700 dark:text-gray-300 ml-8">
                      <li className="flex items-start">
                        <span className="font-bold mr-2">1.</span>
                        <span>Authorize Google Tasks access (takes 10 seconds)</span>
                      </li>
                      <li className="flex items-start">
                        <span className="font-bold mr-2">2.</span>
                        <span>Your homework automatically appears as tasks</span>
                      </li>
                      <li className="flex items-start">
                        <span className="font-bold mr-2">3.</span>
                        <span>Check off assignments as you complete them</span>
                      </li>
                      <li className="flex items-start">
                        <span className="font-bold mr-2">4.</span>
                        <span className="flex items-center">All done! <span className="ml-1 text-2xl">🎉</span></span>
                      </li>
                    </ol>
                  </div>

                  <div className="bg-amber-50 dark:bg-amber-900/20 p-5 rounded-xl border-l-4 border-amber-500">
                    <div className="flex items-start">
                      <span className="text-2xl mr-3">🔒</span>
                      <div>
                        <p className="font-semibold text-gray-800 dark:text-white mb-2">Privacy Guarantee</p>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          We only access your Google Tasks to add and update homework assignments. 
                          We <strong>never</strong> read your personal tasks or access other Google services.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
          </Step>

          {/* Step 2: Exam Dates Preferences */}
          <Step>
            <div className="space-y-6">
              <div className="text-center mb-6">
                <div className="inline-block p-4 bg-gradient-to-br from-green-100 to-teal-100 dark:from-green-900/30 dark:to-teal-900/30 rounded-2xl mb-4">
                  <span className="text-6xl">📅</span>
                </div>
                <h2 className="text-3xl font-bold mb-2 text-gray-800 dark:text-white">Exam Date Preferences</h2>
                <p className="text-gray-600 dark:text-gray-300">Choose how you want to track your exams</p>
              </div>
              
              <Card className="border-2 border-green-100 dark:border-green-900/30 shadow-xl">
                <CardBody className="space-y-6 p-8">
                  <p className="text-lg text-gray-700 dark:text-gray-300 text-center">
                    Where would you like to see your upcoming exams?
                  </p>

                  <div className="space-y-4">
                    <Card
                      isPressable
                      className={`transition-all duration-200 ${
                        formData.examInCalendar
                          ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-900/20 shadow-lg'
                          : 'hover:shadow-md'
                      }`}
                      onPress={() => 
                        setFormData(prev => ({ ...prev, examInCalendar: !prev.examInCalendar }))
                      }
                    >
                      <CardBody className="p-5">
                        <div className="flex items-start space-x-4">
                          <div className="flex-shrink-0">
                            <div className="text-4xl">📆</div>
                          </div>
                          <div className="flex-grow">
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="text-xl font-semibold text-gray-800 dark:text-white">Google Calendar</h3>
                              <Checkbox
                                isSelected={formData.examInCalendar}
                                color="success"
                                size="lg"
                              />
                            </div>
                            <p className="text-gray-600 dark:text-gray-400">
                              Exams appear as calendar events with automatic reminders
                            </p>
                            <div className="mt-3 flex flex-wrap gap-2">
                              <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-1 rounded-full">Time blocking</span>
                              <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-1 rounded-full">Visual overview</span>
                              <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-1 rounded-full">Conflict detection</span>
                            </div>
                          </div>
                        </div>
                      </CardBody>
                    </Card>

                    <Card
                      isPressable
                      className={`transition-all duration-200 ${
                        formData.examInTasks
                          ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-lg'
                          : 'hover:shadow-md'
                      }`}
                      onPress={() => 
                        setFormData(prev => ({ ...prev, examInTasks: !prev.examInTasks }))
                      }
                    >
                      <CardBody className="p-5">
                        <div className="flex items-start space-x-4">
                          <div className="flex-shrink-0">
                            <div className="text-4xl">✅</div>
                          </div>
                          <div className="flex-grow">
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="text-xl font-semibold text-gray-800 dark:text-white">Google Tasks</h3>
                              <Checkbox
                                isSelected={formData.examInTasks}
                                color="primary"
                                size="lg"
                              />
                            </div>
                            <p className="text-gray-600 dark:text-gray-400">
                              Exams appear as tasks alongside your homework
                            </p>
                            <div className="mt-3 flex flex-wrap gap-2">
                              <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-full">Check-off satisfaction</span>
                              <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-full">Priority sorting</span>
                              <span className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded-full">Mobile widgets</span>
                            </div>
                          </div>
                        </div>
                      </CardBody>
                    </Card>
                  </div>

                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-5 rounded-xl border-l-4 border-purple-500">
                    <div className="flex items-start">
                      <span className="text-2xl mr-3">💡</span>
                      <div>
                        <p className="font-semibold text-gray-800 dark:text-white mb-1">Pro Tip</p>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          We recommend enabling <strong>both options</strong> for maximum visibility! 
                          Use Calendar for planning and Tasks for checking off completed exam prep.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
          </Step>

          {/* Step 3: App Selection */}
          <Step>
            <div className="space-y-6">
              <div className="text-center mb-6">
                <div className="inline-block p-4 bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30 rounded-2xl mb-4">
                  <span className="text-6xl">🏫</span>
                </div>
                <h2 className="text-3xl font-bold mb-2 text-gray-800 dark:text-white">Select Your School Platforms</h2>
                <p className="text-gray-600 dark:text-gray-300">Choose which platforms we should sync from</p>
              </div>
              
              <Card className="border-2 border-orange-100 dark:border-orange-900/30 shadow-xl">
                <CardBody className="space-y-6 p-8">
                  <p className="text-lg text-gray-700 dark:text-gray-300 text-center">
                    Which platforms does your school use? (Select all that apply)
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card
                      isPressable
                      isHoverable
                      className={`cursor-pointer transition-all duration-200 ${
                        formData.selectedApps.includes('eduka')
                          ? 'ring-4 ring-blue-500 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 shadow-2xl transform scale-105'
                          : 'hover:shadow-lg hover:scale-102 bg-white dark:bg-gray-800'
                      }`}
                      onPress={() => handleAppToggle('eduka')}
                    >
                      <CardBody className="text-center p-8">
                        <div className="text-6xl mb-4">📚</div>
                        <h3 className="text-2xl font-bold mb-2 text-gray-800 dark:text-white">Eduka</h3>
                        <p className="text-gray-600 dark:text-gray-400 mb-4">
                          E-diary system for Lithuanian schools
                        </p>
                        {formData.selectedApps.includes('eduka') && (
                          <div className="mt-4 inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-full font-semibold shadow-lg">
                            <span className="mr-2">✓</span>
                            Selected
                          </div>
                        )}
                        {!formData.selectedApps.includes('eduka') && (
                          <div className="mt-4 text-gray-400 dark:text-gray-500">
                            Click to select
                          </div>
                        )}
                      </CardBody>
                    </Card>

                    <Card
                      isPressable
                      isHoverable
                      className={`cursor-pointer transition-all duration-200 ${
                        formData.selectedApps.includes('manodienynas')
                          ? 'ring-4 ring-green-500 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30 shadow-2xl transform scale-105'
                          : 'hover:shadow-lg hover:scale-102 bg-white dark:bg-gray-800'
                      }`}
                      onPress={() => handleAppToggle('manodienynas')}
                    >
                      <CardBody className="text-center p-8">
                        <div className="text-6xl mb-4">📖</div>
                        <h3 className="text-2xl font-bold mb-2 text-gray-800 dark:text-white">Mano Dienynas</h3>
                        <p className="text-gray-600 dark:text-gray-400 mb-4">
                          Popular e-diary platform in Lithuania
                        </p>
                        {formData.selectedApps.includes('manodienynas') && (
                          <div className="mt-4 inline-flex items-center px-4 py-2 bg-green-500 text-white rounded-full font-semibold shadow-lg">
                            <span className="mr-2">✓</span>
                            Selected
                          </div>
                        )}
                        {!formData.selectedApps.includes('manodienynas') && (
                          <div className="mt-4 text-gray-400 dark:text-gray-500">
                            Click to select
                          </div>
                        )}
                      </CardBody>
                    </Card>
                  </div>

                  {formData.selectedApps.length === 0 && (
                    <div className="bg-amber-50 dark:bg-amber-900/20 p-5 rounded-xl text-center border-2 border-amber-300 dark:border-amber-700">
                      <div className="text-4xl mb-2">⚠️</div>
                      <p className="font-semibold text-gray-800 dark:text-white mb-1">No platforms selected</p>
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        Please select at least one platform to continue
                      </p>
                    </div>
                  )}
                  
                  {formData.selectedApps.length > 0 && (
                    <div className="bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 p-5 rounded-xl border-l-4 border-green-500">
                      <div className="flex items-center">
                        <span className="text-3xl mr-3">🎯</span>
                        <div>
                          <p className="font-semibold text-gray-800 dark:text-white">
                            {formData.selectedApps.length} platform{formData.selectedApps.length > 1 ? 's' : ''} selected!
                          </p>
                          <p className="text-sm text-gray-700 dark:text-gray-300">
                            Ready to set up your credentials in the next step
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </CardBody>
              </Card>
            </div>
          </Step>

          {/* Step 4: Credentials Input & Verification */}
          <Step>
            <div className="space-y-6">
              <div className="text-center mb-6">
                <div className="inline-block p-4 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-2xl mb-4">
                  <span className="text-6xl">🔐</span>
                </div>
                <h2 className="text-3xl font-bold mb-2 text-gray-800 dark:text-white">Secure Credential Setup</h2>
                <p className="text-gray-600 dark:text-gray-300">Enter your login information for automated sync</p>
              </div>
              
              <Card className="border-2 border-purple-100 dark:border-purple-900/30 shadow-xl">
                <CardBody className="space-y-6 p-8">
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-5 rounded-xl border-l-4 border-purple-500">
                    <div className="flex items-start">
                      <span className="text-3xl mr-3">🔒</span>
                      <div>
                        <p className="font-semibold text-gray-800 dark:text-white mb-2">Your Security is Our Priority</p>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          All passwords are <strong>encrypted with military-grade AES-256 encryption</strong> and stored securely. 
                          We only use them to log in and fetch your homework—nothing else!
                        </p>
                      </div>
                    </div>
                  </div>

                  {formData.selectedApps.includes('eduka') && (
                    <div className="space-y-4 p-6 bg-blue-50/50 dark:bg-blue-900/10 rounded-xl border-2 border-blue-200 dark:border-blue-800">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                          <span className="text-3xl">📚</span>
                          Eduka Credentials
                        </h3>
                        {verificationStatus.eduka === 'success' && (
                          <div className="flex items-center bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-md">
                            <span className="mr-1">✓</span>
                            Verified
                          </div>
                        )}
                        {verificationStatus.eduka === 'error' && (
                          <div className="flex items-center bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-md">
                            <span className="mr-1">✗</span>
                            Failed
                          </div>
                        )}
                      </div>
                      <Input
                        label="Username"
                        placeholder="Enter your Eduka username"
                        value={formData.edukaUsername}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, edukaUsername: e.target.value }))
                        }
                        size="lg"
                        variant="bordered"
                        classNames={{
                          input: "text-lg",
                          inputWrapper: "bg-white dark:bg-gray-800"
                        }}
                      />
                      <Input
                        label="Password"
                        type="password"
                        placeholder="Enter your Eduka password"
                        value={formData.edukaPassword}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, edukaPassword: e.target.value }))
                        }
                        size="lg"
                        variant="bordered"
                        classNames={{
                          input: "text-lg",
                          inputWrapper: "bg-white dark:bg-gray-800"
                        }}
                      />
                    </div>
                  )}

                  {formData.selectedApps.includes('manodienynas') && (
                    <div className="space-y-4 p-6 bg-green-50/50 dark:bg-green-900/10 rounded-xl border-2 border-green-200 dark:border-green-800">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
                          <span className="text-3xl">📖</span>
                          Mano Dienynas Credentials
                        </h3>
                        {verificationStatus.manodienynas === 'success' && (
                          <div className="flex items-center bg-green-500 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-md">
                            <span className="mr-1">✓</span>
                            Verified
                          </div>
                        )}
                        {verificationStatus.manodienynas === 'error' && (
                          <div className="flex items-center bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold shadow-md">
                            <span className="mr-1">✗</span>
                            Failed
                          </div>
                        )}
                      </div>
                      <Input
                        label="Username"
                        placeholder="Enter your Mano Dienynas username"
                        value={formData.manoDienynasUsername}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, manoDienynasUsername: e.target.value }))
                        }
                        size="lg"
                        variant="bordered"
                        classNames={{
                          input: "text-lg",
                          inputWrapper: "bg-white dark:bg-gray-800"
                        }}
                      />
                      <Input
                        label="Password"
                        type="password"
                        placeholder="Enter your Mano Dienynas password"
                        value={formData.manoDienynasPassword}
                        onChange={(e) => 
                          setFormData(prev => ({ ...prev, manoDienynasPassword: e.target.value }))
                        }
                        size="lg"
                        variant="bordered"
                        classNames={{
                          input: "text-lg",
                          inputWrapper: "bg-white dark:bg-gray-800"
                        }}
                      />
                    </div>
                  )}

                  <Button
                    color="primary"
                    onClick={handleVerifyCredentials}
                    isLoading={isVerifying}
                    size="lg"
                    className="w-full text-lg font-semibold shadow-lg"
                  >
                    {isVerifying ? (
                      <>
                        <span className="animate-spin mr-2">🔄</span>
                        Verifying Credentials...
                      </>
                    ) : (
                      <>
                        <span className="mr-2">🔍</span>
                        Verify Credentials
                      </>
                    )}
                  </Button>

                  {Object.keys(verificationStatus).length > 0 && (
                    <div className="space-y-3">
                      {verificationStatus.eduka === 'success' && (
                        <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded-xl border-l-4 border-green-500 shadow-md">
                          <div className="flex items-center">
                            <span className="text-3xl mr-3">✅</span>
                            <div>
                              <p className="font-semibold text-green-800 dark:text-green-200">Eduka Verified!</p>
                              <p className="text-sm text-green-700 dark:text-green-300">Your credentials are working perfectly</p>
                            </div>
                          </div>
                        </div>
                      )}
                      {verificationStatus.eduka === 'error' && (
                        <div className="bg-red-100 dark:bg-red-900/30 p-4 rounded-xl border-l-4 border-red-500 shadow-md">
                          <div className="flex items-center">
                            <span className="text-3xl mr-3">❌</span>
                            <div>
                              <p className="font-semibold text-red-800 dark:text-red-200">Eduka Verification Failed</p>
                              <p className="text-sm text-red-700 dark:text-red-300">Please check your username and password</p>
                            </div>
                          </div>
                        </div>
                      )}
                      {verificationStatus.manodienynas === 'success' && (
                        <div className="bg-green-100 dark:bg-green-900/30 p-4 rounded-xl border-l-4 border-green-500 shadow-md">
                          <div className="flex items-center">
                            <span className="text-3xl mr-3">✅</span>
                            <div>
                              <p className="font-semibold text-green-800 dark:text-green-200">Mano Dienynas Verified!</p>
                              <p className="text-sm text-green-700 dark:text-green-300">Your credentials are working perfectly</p>
                            </div>
                          </div>
                        </div>
                      )}
                      {verificationStatus.manodienynas === 'error' && (
                        <div className="bg-red-100 dark:bg-red-900/30 p-4 rounded-xl border-l-4 border-red-500 shadow-md">
                          <div className="flex items-center">
                            <span className="text-3xl mr-3">❌</span>
                            <div>
                              <p className="font-semibold text-red-800 dark:text-red-200">Mano Dienynas Verification Failed</p>
                              <p className="text-sm text-red-700 dark:text-red-300">Please check your username and password</p>
                            </div>
                          </div>
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