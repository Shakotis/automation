'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Chip } from "@heroui/chip";
import { Spinner } from "@heroui/spinner";
import { Progress } from "@heroui/progress";
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from "@heroui/modal";
import { CheckIcon, EyeFilledIcon, EyeSlashFilledIcon, WarningIcon } from "@/components/icons";

interface Site {
  id: string;
  name: string;
  description: string;
}

interface CredentialData {
  username: string;
  password: string;
  url?: string;
}

interface SiteCredentials {
  [siteId: string]: CredentialData;
}

interface CredentialInputProps {
  selectedSites: string[];
  onComplete: () => void;
  onBack?: () => void;
}

export default function CredentialInput({ selectedSites, onComplete, onBack }: CredentialInputProps) {
  const [sites, setSites] = useState<Site[]>([]);
  const [credentials, setCredentials] = useState<SiteCredentials>({});
  const [verificationStatus, setVerificationStatus] = useState<{[key: string]: boolean | null}>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isVerifying, setIsVerifying] = useState<{[key: string]: boolean}>({});
  const [verificationProgress, setVerificationProgress] = useState<{[key: string]: number}>({});
  const [verificationMessage, setVerificationMessage] = useState<{[key: string]: string}>({});
  const [showPasswords, setShowPasswords] = useState<{[key: string]: boolean}>({});
  const [error, setError] = useState<string | null>(null);
  const [showVerificationModal, setShowVerificationModal] = useState(false);
  const [verificationResults, setVerificationResults] = useState<{[key: string]: {success: boolean, message: string}}>({});

  useEffect(() => {
    fetchSiteInfo();
    initializeCredentials();
  }, [selectedSites]);

  const fetchSiteInfo = async () => {
    try {
      const response = await fetch('/api/auth/sites/', {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setSites(data.available_sites.filter((site: Site) => selectedSites.includes(site.id)));
      }
    } catch (error) {
      setError('Failed to load site information');
    } finally {
      setIsLoading(false);
    }
  };

  const initializeCredentials = () => {
    const initialCredentials: SiteCredentials = {};
    selectedSites.forEach(siteId => {
      initialCredentials[siteId] = { username: '', password: '', url: '' };
    });
    setCredentials(initialCredentials);
  };

  const handleCredentialChange = (siteId: string, field: keyof CredentialData, value: string) => {
    setCredentials(prev => ({
      ...prev,
      [siteId]: {
        ...prev[siteId],
        [field]: value
      }
    }));
    
    // Reset verification status when credentials change
    if (field === 'username' || field === 'password') {
      setVerificationStatus(prev => ({
        ...prev,
        [siteId]: null
      }));
    }
  };

  const togglePasswordVisibility = (siteId: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [siteId]: !prev[siteId]
    }));
  };

  const verifyCredentials = async (siteId: string) => {
    const cred = credentials[siteId];
    if (!cred.username || !cred.password) {
      setError('Please enter both username and password');
      return;
    }

    setIsVerifying(prev => ({ ...prev, [siteId]: true }));
    setVerificationProgress(prev => ({ ...prev, [siteId]: 0 }));
    setVerificationMessage(prev => ({ ...prev, [siteId]: 'Starting verification...' }));
    setError(null);

    // Simulate progress updates
    const progressUpdates = [
      { progress: 20, message: 'Opening browser...' },
      { progress: 40, message: 'Navigating to login page...' },
      { progress: 60, message: 'Entering credentials...' },
      { progress: 80, message: 'Logging in...' },
      { progress: 100, message: 'Verifying login...' }
    ];

    let updateIndex = 0;
    const progressInterval = setInterval(() => {
      if (updateIndex < progressUpdates.length) {
        const update = progressUpdates[updateIndex];
        setVerificationProgress(prev => ({ ...prev, [siteId]: update.progress }));
        setVerificationMessage(prev => ({ ...prev, [siteId]: update.message }));
        updateIndex++;
      }
    }, 800); // Update every 800ms

    try {
      const response = await fetch('/api/auth/verify-credentials/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          site: siteId,
          url: cred.url || undefined
        }),
      });

      const data = await response.json();
      
      clearInterval(progressInterval);
      setVerificationProgress(prev => ({ ...prev, [siteId]: 100 }));
      setVerificationMessage(prev => ({ ...prev, [siteId]: data.success ? 'Verification successful!' : 'Verification failed!' }));
      
      setVerificationStatus(prev => ({
        ...prev,
        [siteId]: data.success
      }));

      setVerificationResults(prev => ({
        ...prev,
        [siteId]: {
          success: data.success,
          message: data.message
        }
      }));

    } catch (error) {
      clearInterval(progressInterval);
      setVerificationProgress(prev => ({ ...prev, [siteId]: 100 }));
      setVerificationMessage(prev => ({ ...prev, [siteId]: 'Network error occurred!' }));
      setVerificationStatus(prev => ({
        ...prev,
        [siteId]: false
      }));
      setError('Network error during verification');
    } finally {
      setTimeout(() => {
        setIsVerifying(prev => ({ ...prev, [siteId]: false }));
        setVerificationProgress(prev => ({ ...prev, [siteId]: 0 }));
        setVerificationMessage(prev => ({ ...prev, [siteId]: '' }));
      }, 2000); // Keep progress visible for 2 seconds
    }
  };

  const saveCredentials = async (siteId: string) => {
    const cred = credentials[siteId];
    
    // Read the actual DOM values to catch autofilled passwords that didn't trigger onChange
    // HeroUI wraps inputs, so we need to find the actual <input> elements within the card
    const siteCards = Array.from(document.querySelectorAll('[data-site-card]'));
    let actualUsername = cred.username;
    let actualPassword = cred.password;
    
    for (const card of siteCards) {
      if ((card as HTMLElement).dataset.siteCard === siteId) {
        const inputs = card.querySelectorAll('input');
        if (inputs.length >= 2) {
          // First input is username, second is password
          actualUsername = inputs[0].value || cred.username;
          actualPassword = inputs[1].value || cred.password;
          
          console.log(`[${siteId}] Saving credentials:`, {
            stateUsername: cred.username,
            domUsername: inputs[0].value,
            finalUsername: actualUsername,
            statePassword: cred.password ? '***' : '(empty)',
            domPassword: inputs[1].value ? '***' : '(empty)',
            finalPassword: actualPassword ? '***' : '(empty)'
          });
          break;
        }
      }
    }
    
    try {
      const response = await fetch('/api/auth/credentials/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          site: siteId,
          username: actualUsername,
          password: actualPassword,
          additional_data: {
            url: cred.url
          }
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to save credentials');
      }

      return true;
    } catch (error) {
      throw error;
    }
  };

  const handleSaveAndVerifyAll = async () => {
    setIsSaving(true);
    setError(null);
    const results: {[key: string]: {success: boolean, message: string}} = {};

    try {
      // First, save all credentials
      for (const siteId of selectedSites) {
        const cred = credentials[siteId];
        if (cred.username && cred.password) {
          await saveCredentials(siteId);
        }
      }

      // Then verify all credentials
      for (const siteId of selectedSites) {
        const cred = credentials[siteId];
        if (cred.username && cred.password) {
          try {
            const response = await fetch('/api/auth/verify-credentials/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              credentials: 'include',
              body: JSON.stringify({
                site: siteId,
                url: cred.url || undefined
              }),
            });

            const data = await response.json();
            results[siteId] = {
              success: data.success,
              message: data.message
            };
          } catch (error) {
            results[siteId] = {
              success: false,
              message: 'Verification failed'
            };
          }
        }
      }

      setVerificationResults(results);
      setShowVerificationModal(true);
      
    } catch (error) {
      setError('Failed to save credentials. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCompleteSetup = () => {
    setShowVerificationModal(false);
    onComplete();
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Spinner size="lg" label="Loading..." />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="mb-6">
        <CardHeader className="pb-0">
          <div className="w-full text-center">
            <h1 className="text-2xl font-bold mb-2">Setup Your Credentials 🔐</h1>
            <p className="text-default-600">
              Enter your login credentials for each selected site. We'll verify they work and store them securely.
            </p>
          </div>
        </CardHeader>
      </Card>

      {error && (
        <Card className="mb-6 border-danger">
          <CardBody>
            <p className="text-danger text-center">{error}</p>
          </CardBody>
        </Card>
      )}

      <div className="space-y-6 mb-8">
        {sites.map((site) => (
          <Card key={site.id} className="p-6" data-site-card={site.id}>
            <CardHeader className="px-0 pt-0">
              <div className="flex items-center justify-between w-full">
                <div>
                  <h3 className="text-lg font-semibold">{site.name}</h3>
                  <p className="text-default-600 text-sm">{site.description}</p>
                </div>
                {verificationStatus[site.id] !== null && (
                  <Chip
                    color={verificationStatus[site.id] ? "success" : "danger"}
                    variant="flat"
                    startContent={verificationStatus[site.id] ? <CheckIcon size={16} /> : <WarningIcon size={16} />}
                  >
                    {verificationStatus[site.id] ? "Verified" : "Failed"}
                  </Chip>
                )}
              </div>
            </CardHeader>
            
            <CardBody className="px-0 pb-0">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <Input
                  label="Username/Email"
                  placeholder="Enter your username or email"
                  value={credentials[site.id]?.username || ''}
                  onChange={(e) => handleCredentialChange(site.id, 'username', e.target.value)}
                  onInput={(e) => handleCredentialChange(site.id, 'username', (e.target as HTMLInputElement).value)}
                  autoComplete="off"
                  data-site={site.id}
                  isRequired
                />
                <Input
                  label="Password"
                  placeholder="Enter your password"
                  type={showPasswords[site.id] ? "text" : "password"}
                  value={credentials[site.id]?.password || ''}
                  onChange={(e) => handleCredentialChange(site.id, 'password', e.target.value)}
                  onInput={(e) => handleCredentialChange(site.id, 'password', (e.target as HTMLInputElement).value)}
                  autoComplete="new-password"
                  data-site={site.id}
                  endContent={
                    <button
                      className="focus:outline-none"
                      type="button"
                      onClick={() => togglePasswordVisibility(site.id)}
                    >
                      {showPasswords[site.id] ? (
                        <EyeSlashFilledIcon className="text-2xl text-default-400 pointer-events-none" />
                      ) : (
                        <EyeFilledIcon className="text-2xl text-default-400 pointer-events-none" />
                      )}
                    </button>
                  }
                  isRequired
                />
              </div>
              
              {(site.id === 'moodle' || site.id === 'custom') && (
                <Input
                  label="Site URL (Optional)"
                  placeholder="https://your-school.moodle.com"
                  value={credentials[site.id]?.url || ''}
                  onChange={(e) => handleCredentialChange(site.id, 'url', e.target.value)}
                  className="mb-4"
                />
              )}
              
              <Button
                color="primary"
                variant="bordered"
                onPress={() => verifyCredentials(site.id)}
                isDisabled={!credentials[site.id]?.username || !credentials[site.id]?.password}
                isLoading={isVerifying[site.id]}
                className="w-full md:w-auto"
              >
                {isVerifying[site.id] ? 'Verifying...' : 'Test Connection'}
              </Button>
              
              {isVerifying[site.id] && (
                <div className="mt-4 space-y-2">
                  <Progress
                    value={verificationProgress[site.id] || 0}
                    color="primary"
                    className="w-full"
                    label="Verification Progress"
                    showValueLabel={true}
                  />
                  <p className="text-sm text-default-600">
                    {verificationMessage[site.id] || 'Starting verification...'}
                  </p>
                </div>
              )}
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
        {onBack && (
          <Button
            variant="bordered"
            size="lg"
            onPress={onBack}
            isDisabled={isSaving}
            className="w-full sm:w-auto"
          >
            Back
          </Button>
        )}
        
        <Button
          color="primary"
          size="lg"
          onPress={handleSaveAndVerifyAll}
          isLoading={isSaving}
          className="w-full sm:w-auto"
        >
          {isSaving ? 'Saving & Verifying...' : 'Save & Verify All'}
        </Button>
      </div>

      {/* Verification Results Modal */}
      <Modal 
        isOpen={showVerificationModal} 
        onClose={() => setShowVerificationModal(false)}
        size="2xl"
      >
        <ModalContent>
          <ModalHeader>
            <h3 className="text-xl font-bold">Verification Results</h3>
          </ModalHeader>
          <ModalBody>
            <div className="space-y-4">
              {Object.entries(verificationResults).map(([siteId, result]) => {
                const site = sites.find(s => s.id === siteId);
                return (
                  <div key={siteId} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <h4 className="font-semibold">{site?.name}</h4>
                      <p className="text-sm text-default-600">{result.message}</p>
                    </div>
                    <Chip
                      color={result.success ? "success" : "danger"}
                      variant="flat"
                      startContent={result.success ? <CheckIcon size={16} /> : <WarningIcon size={16} />}
                    >
                      {result.success ? "✓ Verified" : "✗ Failed"}
                    </Chip>
                  </div>
                );
              })}
            </div>
            
            <div className="mt-6 p-4 bg-default-100 rounded-lg">
              <p className="text-sm text-default-700">
                <strong>Note:</strong> Failed verifications might be due to incorrect credentials, 
                site maintenance, or security restrictions. You can update credentials later in your dashboard.
              </p>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button
              color="primary"
              onPress={handleCompleteSetup}
            >
              Continue to Dashboard
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
}