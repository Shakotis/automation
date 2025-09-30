'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import SiteSelection from '@/components/SiteSelection';
import CredentialInput from '@/components/CredentialInput';

type OnboardingStep = 'site-selection' | 'credential-input' | 'completed';

export default function OnboardingFlow() {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('site-selection');
  const [selectedSites, setSelectedSites] = useState<string[]>([]);
  const router = useRouter();

  const handleSiteSelectionComplete = (sites: string[]) => {
    setSelectedSites(sites);
    setCurrentStep('credential-input');
  };

  const handleCredentialInputComplete = () => {
    setCurrentStep('completed');
    // Redirect to dashboard after a brief delay
    setTimeout(() => {
      router.push('/dashboard');
    }, 1000);
  };

  const handleBackToSiteSelection = () => {
    setCurrentStep('site-selection');
  };

  const handleSkipOnboarding = () => {
    router.push('/dashboard');
  };

  if (currentStep === 'completed') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-2xl font-bold mb-2">Setup Complete!</h1>
          <p className="text-default-600">Redirecting you to your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {currentStep === 'site-selection' && (
        <SiteSelection
          onComplete={handleSiteSelectionComplete}
          onSkip={handleSkipOnboarding}
        />
      )}
      
      {currentStep === 'credential-input' && (
        <CredentialInput
          selectedSites={selectedSites}
          onComplete={handleCredentialInputComplete}
          onBack={handleBackToSiteSelection}
        />
      )}
    </div>
  );
}