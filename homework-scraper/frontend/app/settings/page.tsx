"use client";

import { useState, useEffect } from "react";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { addToast } from "@heroui/toast";
import { Switch } from "@heroui/switch";
import { Input } from "@heroui/input";
import { Divider } from "@heroui/divider";
import { Chip } from "@heroui/chip";
import { Spinner } from "@heroui/spinner";
import { Select, SelectItem } from "@heroui/select";
import { title } from "@/components/primitives";

// Get API base URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';
console.log('[Settings] Using API_BASE_URL:', API_BASE_URL);

interface UserPreferences {
  enable_manodienynas: boolean;
  enable_eduka: boolean;
  last_scraped_manodienynas: string | null;
  last_scraped_eduka: string | null;
  google_tasks_title_format: 'title' | 'subject';
}

interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  has_google_oauth: boolean;
}

interface Credential {
  username: string;
  is_verified: boolean;
  last_verified: string | null;
}

interface SiteCredentials {
  manodienynas?: Credential;
  eduka?: Credential;
}

export default function SettingsPage() {
  const [preferences, setPreferences] = useState<UserPreferences>({
    enable_manodienynas: true,
    enable_eduka: true,
    last_scraped_manodienynas: null,
    last_scraped_eduka: null,
    google_tasks_title_format: 'title',
  });
  
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [credentials, setCredentials] = useState<SiteCredentials>({});
  const [credentialForm, setCredentialForm] = useState<{
    site: string;
    username: string;
    password: string;
    showPassword: boolean;
  }>({
    site: '',
    username: '',
    password: '',
    showPassword: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [verifying, setVerifying] = useState<string | null>(null);
  const [savingCredential, setSavingCredential] = useState<string | null>(null);
  const [showCredentialsPrompt, setShowCredentialsPrompt] = useState(false);
  const [generatingSchedule, setGeneratingSchedule] = useState(false);
  const [scheduleDownloadUrl, setScheduleDownloadUrl] = useState<string | null>(null);

  const requireAuth = (action: string) => {
    if (!userProfile) {
      addToast({
        title: 'Authentication Required',
        description: `Please sign in with Google to ${action}`,
        color: 'danger',
      });
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
      return false;
    }
    return true;
  };

  useEffect(() => {
    fetchUserData();
    fetchCredentials();
    
    // Check if redirected from OAuth with setup=credentials parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('setup') === 'credentials') {
      setShowCredentialsPrompt(true);
    }
  }, []);

  const fetchUserData = async () => {
    try {
      // Try to fetch real user profile from the API
      const response = await fetch(`${API_BASE_URL}/auth/user`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserProfile(data.user);
        
        // Fetch preferences
        const prefResponse = await fetch(`${API_BASE_URL}/scraper/preferences`, {
          credentials: 'include',
        });
        
        if (prefResponse.ok) {
          const prefData = await prefResponse.json();
          setPreferences({
            enable_manodienynas: prefData.enable_manodienynas,
            enable_eduka: prefData.enable_eduka,
            last_scraped_manodienynas: prefData.last_scraped_manodienynas,
            last_scraped_eduka: prefData.last_scraped_eduka,
            google_tasks_title_format: prefData.google_tasks_title_format || 'title',
          });
        }
      } else if (response.status === 401) {
        // User is not authenticated - show toast and redirect
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in with Google to access settings',
          color: 'danger',
        });
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        return;
      } else {
        // Other error - silently handle
        console.warn('Failed to fetch user data:', response.status);
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
      // Network error
      addToast({
        title: 'Connection Error',
        description: 'Failed to connect to backend server',
        color: 'danger',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchCredentials = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/credentials`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setCredentials(data.credentials || {});
      }
    } catch (error) {
      console.error('Error fetching credentials:', error);
    }
  };

  const handleSaveCredential = async (site: string, username: string, password: string) => {
    setSavingCredential(site);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/credentials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          site,
          username,
          password,
        }),
      });

      if (response.ok) {
        await fetchCredentials(); // Refresh credentials
        setCredentialForm({ site: '', username: '', password: '', showPassword: false });
        addToast({
          title: 'Credentials Saved',
          description: `Successfully saved for ${site}`,
          color: 'success',
        });
        
        // Automatically verify the credentials
        await handleVerifyCredential(site);
      } else {
        let errorMessage = 'Failed to save credentials';
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.detail || errorMessage;
          
          // Handle authentication error specifically
          if (response.status === 401 || errorMessage.includes('Authentication')) {
            errorMessage = 'Please sign in with Google first to save credentials';
            // Optionally redirect to login
            setTimeout(() => {
              window.location.href = '/';
            }, 2000);
          }
        } catch (e) {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        console.error('Error saving credential:', errorMessage);
        addToast({
          title: 'Save Failed',
          description: errorMessage,
          color: 'danger',
        });
      }
    } catch (error) {
      console.error('Error saving credential:', error);
      addToast({
        title: 'Network Error',
        description: 'Could not save credentials. Please check if the backend server is running.',
        color: 'danger',
      });
    } finally {
      setSavingCredential(null);
    }
  };

  const handleVerifyCredential = async (site: string) => {
    setVerifying(site);
    
    // Create timeout promise (60 seconds for slow sites)
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => {
        reject(new Error('Verification is taking longer than expected. The site may be slow or temporarily unavailable. Please try again later.'));
      }, 60000); // 60 seconds timeout
    });
    
    const verifyPromise = (async () => {
      try {
        // Race between actual verification and timeout
        const response = await Promise.race([
          fetch(`${API_BASE_URL}/auth/verify-credentials`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ site }),
          }),
          timeoutPromise
        ]);

        if (response.ok) {
          const data = await response.json();
          await fetchCredentials(); // Refresh to get updated verification status
          
          if (data.success) {
            return { success: true, message: `Credentials verified successfully for ${site}` };
          } else {
            throw new Error(data.message || 'Verification failed - please check your credentials');
          }
        } else {
          let errorMessage = 'Verification failed';
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorData.detail || errorMessage;
          } catch (e) {
            errorMessage = response.statusText || errorMessage;
          }
          throw new Error(errorMessage);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Network error during verification';
        throw new Error(errorMessage);
      } finally {
        setVerifying(null);
      }
    })();

    addToast({
      title: 'Verifying',
      description: `Checking credentials for ${site}...`,
      color: 'warning',
      promise: verifyPromise.then(
        (result) => ({
          title: 'Verified',
          description: result.message,
          color: 'success' as const,
        }),
        (error) => ({
          title: 'Verification Failed',
          description: error.message,
          color: 'danger' as const,
        })
      ),
    });

    try {
      const result = await verifyPromise;
      return { success: true, message: result.message };
    } catch (error) {
      return { success: false, message: error instanceof Error ? error.message : 'Unknown error' };
    }
  };

  const handleSavePreferences = async () => {
    setSaving(true);
    try {
      const response = await fetch(`${API_BASE_URL}/scraper/preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          enable_manodienynas: preferences.enable_manodienynas,
          enable_eduka: preferences.enable_eduka,
          google_tasks_title_format: preferences.google_tasks_title_format,
        }),
      });
      
      if (response.ok) {
        addToast({
          title: "Settings Saved",
          description: "Your preferences have been updated successfully!",
          color: "success",
        });
      } else {
        const errorData = await response.json();
        addToast({
          title: "Save Failed",
          description: errorData.error || 'Unknown error occurred',
          color: "danger",
        });
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      addToast({
        title: "Network Error",
        description: "Could not save preferences. Please try again.",
        color: "danger",
      });
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateSchedule = async () => {
    setGeneratingSchedule(true);
    setScheduleDownloadUrl(null);

    try {
      const response = await fetch(`${API_BASE_URL}/scraper/schedule/generate`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.download_url) {
          setScheduleDownloadUrl(data.download_url);
          addToast({
            title: "Schedule Generated",
            description: "Your lesson schedule is ready to download!",
            color: "success",
          });
        } else {
          throw new Error(data.message || 'Failed to generate schedule');
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.detail || 'Failed to generate schedule');
      }
    } catch (error) {
      console.error('Error generating schedule:', error);
      const errorMessage = error instanceof Error ? error.message : 'Could not generate schedule. Please ensure your Manodienynas credentials are saved and verified.';
      addToast({
        title: "Generation Failed",
        description: errorMessage,
        color: "danger",
      });
    } finally {
      setGeneratingSchedule(false);
    }
  };

  const handleGoogleAuth = () => {
    // Redirect to Google OAuth
    window.location.href = '/api/auth/google/login/';
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('lt-LT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const CredentialSection = ({ site, displayName, description }: { 
    site: string, 
    displayName: string, 
    description: string 
  }) => {
    const credential = credentials[site as keyof SiteCredentials];
    const isExpanded = credentialForm.site === site;
    const [localUsername, setLocalUsername] = useState('');
    const [localPassword, setLocalPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    useEffect(() => {
      if (credential) {
        setLocalUsername(credential.username);
      }
    }, [credential]);

    const handleSave = () => {
      if (localUsername && localPassword) {
        handleSaveCredential(site, localUsername, localPassword);
        setLocalPassword('');
        setCredentialForm({ site: '', username: '', password: '', showPassword: false });
      }
    };

    const toggleForm = () => {
      if (isExpanded) {
        setCredentialForm({ site: '', username: '', password: '', showPassword: false });
        setLocalPassword('');
      } else {
        setCredentialForm({ site, username: credential?.username || '', password: '', showPassword: false });
        setLocalUsername(credential?.username || '');
        setLocalPassword('');
      }
    };

    return (
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row justify-between items-start gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-sm sm:text-base">{displayName}</h3>
            <p className="text-xs sm:text-sm text-default-500">{description}</p>
            {credential && (
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 mt-2 flex-wrap">
                <span className="text-xs text-default-400 truncate">
                  Username: {credential.username}
                </span>
                <Chip 
                  size="sm" 
                  color={credential.is_verified ? 'success' : 'warning'}
                  variant="flat"
                >
                  {credential.is_verified ? '✓ Verified' : '⚠ Not Verified'}
                </Chip>
                {credential.last_verified && (
                  <span className="text-xs text-default-400">
                    Last verified: {formatDate(credential.last_verified)}
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto shrink-0">
            {credential && (
              <Button
                size="sm"
                variant="bordered"
                onClick={() => {
                  if (!requireAuth('verify credentials')) return;
                  handleVerifyCredential(site);
                }}
                isLoading={verifying === site}
                disabled={verifying === site}
                className="flex-1 sm:flex-none"
              >
                {verifying === site ? 'Verifying...' : 'Verify'}
              </Button>
            )}
            <Button
              size="sm"
              color={credential ? 'default' : 'primary'}
              variant={credential ? 'bordered' : 'solid'}
              onClick={() => {
                if (!requireAuth('manage credentials')) return;
                toggleForm();
              }}
              className="flex-1 sm:flex-none"
            >
              {credential ? 'Edit' : 'Add Credentials'}
            </Button>
          </div>
        </div>

        {isExpanded && (
          <Card className="bg-default-50">
            <CardBody className="space-y-4 p-4">
              <Input
                label="Username/Email"
                placeholder="Enter your username or email"
                value={localUsername}
                onChange={(e) => setLocalUsername(e.target.value)}
                variant="bordered"
                isRequired
                classNames={{
                  input: "text-sm",
                  label: "text-xs sm:text-sm"
                }}
              />
              <Input
                label="Password"
                placeholder="Enter your password"
                type={showPassword ? 'text' : 'password'}
                value={localPassword}
                onChange={(e) => setLocalPassword(e.target.value)}
                variant="bordered"
                isRequired
                classNames={{
                  input: "text-sm",
                  label: "text-xs sm:text-sm"
                }}
                endContent={
                  <Button
                    size="sm"
                    variant="light"
                    onClick={() => setShowPassword(!showPassword)}
                    isIconOnly
                  >
                    {showPassword ? '👁️‍🗨️' : '👁️'}
                  </Button>
                }
              />
              <div className="flex flex-col sm:flex-row gap-2">
                <Button
                  color="primary"
                  onClick={handleSave}
                  isDisabled={!localUsername || !localPassword}
                  isLoading={savingCredential === site}
                  className="w-full sm:w-auto"
                >
                  {savingCredential === site ? 'Saving...' : 'Save & Verify'}
                </Button>
                <Button
                  variant="bordered"
                  onClick={toggleForm}
                  className="w-full sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
              <div className="text-xs text-default-500 space-y-1">
                <p>🔒 Your credentials are encrypted and stored securely.</p>
                <p>⚡ Verification tests login to ensure credentials work correctly.</p>
              </div>
            </CardBody>
          </Card>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardBody className="h-32 bg-default-100" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 max-w-4xl">
      <h1 className={title({ class: "mb-4 sm:mb-8 text-2xl sm:text-3xl", size: "sm" })}>Settings</h1>

      {/* Credentials Setup Prompt */}
      {showCredentialsPrompt && userProfile && (
        <Card className="mb-4 sm:mb-6 border-primary-200 bg-primary-50">
          <CardBody className="p-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-start gap-3 flex-1">
                <div className="text-primary-600 text-xl sm:text-2xl pt-1 shrink-0">🔐</div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-primary-800 text-sm sm:text-base">Setup Your Site Credentials</h3>
                  <p className="text-primary-700 text-xs sm:text-sm break-words">
                    To start scraping homework, please add your Manodienynas or Eduka credentials below.
                  </p>
                </div>
              </div>
              <Button
                isIconOnly
                size="sm"
                variant="light"
                onClick={() => setShowCredentialsPrompt(false)}
                className="self-start sm:self-center shrink-0"
              >
                ✕
              </Button>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Authentication Warning */}
      {!userProfile && (
        <Card className="mb-4 sm:mb-6 border-warning-200 bg-warning-50">
          <CardBody className="p-4">
            <div className="flex flex-col sm:flex-row items-start gap-3">
              <div className="text-warning-600 text-xl sm:text-2xl pt-1 shrink-0">⚠️</div>
              <div className="flex-1">
                <h3 className="font-semibold text-warning-800 text-sm sm:text-base">Authentication Required</h3>
                <p className="text-warning-700 text-xs sm:text-sm mb-3">
                  You need to sign in with Google to save credentials and access all settings.
                </p>
                <Button
                  size="sm"
                  color="warning"
                  variant="bordered"
                  className="w-full sm:w-auto"
                  onClick={() => window.location.href = '/auth/google'}
                >
                  Sign In with Google
                </Button>
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* User Profile */}
      <Card className="mb-4 sm:mb-6">
        <CardHeader className="p-4">
          <h2 className="text-lg sm:text-xl font-semibold">User Profile</h2>
        </CardHeader>
        <CardBody className="p-4 pt-0">
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              <div>
                <Input
                  label="Email"
                  value={userProfile?.email || ''}
                  isReadOnly
                  variant="bordered"
                  className="w-full"
                  classNames={{
                    input: "text-sm",
                    label: "text-xs sm:text-sm"
                  }}
                />
              </div>
              <div>
                <Input
                  label="Name"
                  value={`${userProfile?.first_name || ''} ${userProfile?.last_name || ''}`}
                  isReadOnly
                  variant="bordered"
                  className="w-full"
                  classNames={{
                    input: "text-sm",
                    label: "text-xs sm:text-sm"
                  }}
                />
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 pt-2">
              <span className="text-xs sm:text-sm font-medium">Google OAuth:</span>
              {userProfile?.has_google_oauth ? (
                <Chip color="success" variant="flat" size="sm">
                  ✓ Connected
                </Chip>
              ) : (
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
                  <Chip color="warning" variant="flat" size="sm">
                    Not Connected
                  </Chip>
                  <Button
                    size="sm"
                    color="primary"
                    onPress={handleGoogleAuth}
                    className="w-full sm:w-auto"
                  >
                    Connect Google Account
                  </Button>
                </div>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Scraping Settings */}
      <Card className="mb-4 sm:mb-6">
        <CardHeader className="p-4">
          <h2 className="text-lg sm:text-xl font-semibold">Scraping Settings</h2>
        </CardHeader>
        <CardBody className="p-4 pt-0">
          <div className="space-y-4 sm:space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start gap-3">
              <div className="flex-1">
                <h3 className="font-medium text-sm sm:text-base">Enable Manodienynas.lt</h3>
                <p className="text-xs sm:text-sm text-default-500">
                  Scrape homework from Manodienynas.lt
                </p>
                {preferences.last_scraped_manodienynas && (
                  <p className="text-xs text-default-400 mt-1">
                    Last scraped: {formatDate(preferences.last_scraped_manodienynas)}
                  </p>
                )}
              </div>
              <Switch
                isSelected={preferences.enable_manodienynas}
                onValueChange={(value) => 
                  setPreferences(prev => ({ ...prev, enable_manodienynas: value }))
                }
                className="shrink-0"
              />
            </div>

            {preferences.enable_manodienynas && (
              <div className="pl-0 sm:pl-4 border-l-0 sm:border-l-2 border-primary-200">
                <CredentialSection
                  site="manodienynas"
                  displayName="Manodienynas Credentials"
                  description="Enter your Manodienynas.lt login credentials."
                />
              </div>
            )}

            <Divider />

            <div className="flex flex-col sm:flex-row justify-between items-start gap-3">
              <div className="flex-1">
                <h3 className="font-medium text-sm sm:text-base">Enable Eduka.lt</h3>
                <p className="text-xs sm:text-sm text-default-500">
                  Scrape homework from Eduka.lt
                </p>
                {preferences.last_scraped_eduka && (
                  <p className="text-xs text-default-400 mt-1">
                    Last scraped: {formatDate(preferences.last_scraped_eduka)}
                  </p>
                )}
              </div>
              <Switch
                isSelected={preferences.enable_eduka}
                onValueChange={(value) => 
                  setPreferences(prev => ({ ...prev, enable_eduka: value }))
                }
                className="shrink-0"
              />
            </div>

            {preferences.enable_eduka && (
              <div className="pl-0 sm:pl-4 border-l-0 sm:border-l-2 border-secondary-200">
                <CredentialSection
                  site="eduka"
                  displayName="Eduka Credentials"
                  description="Enter your Eduka.lt login credentials."
                />
              </div>
            )}
          </div>
        </CardBody>
      </Card>

      {/* Sync Settings */}
      <Card className="mb-4 sm:mb-6">
        <CardHeader className="p-4">
          <h2 className="text-lg sm:text-xl font-semibold">Google Tasks Integration</h2>
        </CardHeader>
        <CardBody className="p-4 pt-0">
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 sm:p-4 bg-default-50 rounded-lg gap-3">
              <div className="flex-1">
                <h3 className="font-medium text-sm sm:text-base">Google Tasks Sync</h3>
                <p className="text-xs sm:text-sm text-default-500">
                  Sync homework to "Homework" task list in Google Tasks
                </p>
              </div>
              {userProfile?.has_google_oauth ? (
                <Chip color="success" variant="flat" size="sm" className="shrink-0">
                  ✓ Ready
                </Chip>
              ) : (
                <Button
                  size="sm"
                  color="primary"
                  onPress={handleGoogleAuth}
                  className="w-full sm:w-auto shrink-0"
                >
                  Setup Google Tasks
                </Button>
              )}
            </div>

            <Divider />

            <div>
              <Select
                label="Google Tasks Title Format"
                selectedKeys={[preferences.google_tasks_title_format]}
                onSelectionChange={(keys) => {
                  const value = Array.from(keys)[0] as 'title' | 'subject';
                  setPreferences(prev => ({ ...prev, google_tasks_title_format: value }));
                }}
                variant="bordered"
                className="w-full"
                description="Choose what to display as the task title in Google Tasks"
                classNames={{
                  label: "text-xs sm:text-sm",
                  value: "text-xs sm:text-sm",
                  description: "text-xs"
                }}
              >
                <SelectItem key="title">
                  Task Title (e.g., "Complete math worksheet")
                </SelectItem>
                <SelectItem key="subject">
                  Subject Name (e.g., "Mathematics")
                </SelectItem>
              </Select>
            </div>

            <Divider />

            <div className="text-xs sm:text-sm text-default-500 space-y-1">
              <p>• Homework will be created as tasks in your Google Tasks "Homework" list.</p>
              <p>• Due dates will be preserved when available.</p>
              <p>• Task descriptions will include subject and source information.</p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Schedule Generator */}
      <Card className="mb-4 sm:mb-6">
        <CardHeader className="p-4">
          <h2 className="text-lg sm:text-xl font-semibold">Lesson Schedule</h2>
        </CardHeader>
        <CardBody className="p-4 pt-0">
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 sm:p-4 bg-default-50 rounded-lg gap-3">
              <div className="flex-1">
                <h3 className="font-medium text-sm sm:text-base">Generate Schedule PNG</h3>
                <p className="text-xs sm:text-sm text-default-500">
                  Download your lesson schedule as a formatted PNG image
                </p>
              </div>
              <Button
                size="sm"
                color="primary"
                onPress={() => {
                  if (!requireAuth('generate schedule')) return;
                  handleGenerateSchedule();
                }}
                isLoading={generatingSchedule}
                disabled={generatingSchedule || !userProfile}
                className="w-full sm:w-auto shrink-0"
              >
                {generatingSchedule ? 'Generating...' : 'Generate Schedule'}
              </Button>
            </div>

            {scheduleDownloadUrl && (
              <div className="p-3 sm:p-4 bg-success-50 rounded-lg space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-success-600 text-lg">✓</span>
                  <h4 className="font-medium text-success-800 text-sm sm:text-base">Schedule Ready!</h4>
                </div>
                <p className="text-xs sm:text-sm text-success-700">
                  Your lesson schedule has been generated successfully.
                </p>
                <Button
                  size="sm"
                  color="success"
                  variant="bordered"
                  as="a"
                  href={`${API_BASE_URL}${scheduleDownloadUrl}`}
                  download
                  className="w-full sm:w-auto"
                >
                  📥 Download Schedule
                </Button>
              </div>
            )}

            <Divider />

            <div className="text-xs sm:text-sm text-default-500 space-y-1">
              <p>• Schedule will be scraped from manodienynas.lt and formatted as a PNG.</p>
              <p>• Requires valid Manodienynas credentials to be saved and verified.</p>
              <p>• The image file will have a creation date of June 21, 2026.</p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          color="primary"
          onPress={() => {
            if (!requireAuth('save settings')) return;
            handleSavePreferences();
          }}
          isLoading={saving}
          disabled={saving}
          className="w-full"
        >
          Save Settings
        </Button>
        <Button
          variant="bordered"
          onPress={() => {
            if (!requireAuth('reset settings')) return;
            fetchUserData();
          }}
          disabled={saving}
          className="w-full"
        >
          Reset
        </Button>
      </div>

      {/* Privacy & Data Management */}
      <Card className="mt-6 border-2 border-default-200">
        <CardHeader className="p-4 bg-default-50">
          <h2 className="text-lg sm:text-xl font-semibold">🔒 Privacy & Data Management</h2>
        </CardHeader>
        <CardBody className="p-4 pt-0">
          <div className="space-y-4">
            <div className="text-xs sm:text-sm text-default-600 space-y-2 pt-2">
              <p>
                <strong>How we protect your data:</strong>
              </p>
              <ul className="list-disc pl-5 space-y-1">
                <li>Educational platform credentials are encrypted using industry-standard encryption (Fernet)</li>
                <li>All data transmission uses HTTPS/TLS encryption</li>
                <li>Google OAuth tokens are stored securely and never exposed</li>
                <li>We only access your Google Tasks when you explicitly sync homework</li>
              </ul>
            </div>

            <Divider />

            <div className="text-xs sm:text-sm text-default-600 space-y-2">
              <p>
                <strong>Your data rights:</strong>
              </p>
              <ul className="list-disc pl-5 space-y-1">
                <li>You can revoke Google OAuth access anytime from your <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google Account settings</a></li>
                <li>You can delete your educational platform credentials anytime</li>
                <li>Account deletion will permanently remove all your data within 30 days</li>
              </ul>
            </div>

            <Divider />

            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              <Button
                as="a"
                href="/privacy"
                target="_blank"
                size="sm"
                variant="bordered"
                className="w-full sm:w-auto"
              >
                📄 Privacy Policy
              </Button>
              <Button
                as="a"
                href="/terms"
                target="_blank"
                size="sm"
                variant="bordered"
                className="w-full sm:w-auto"
              >
                📋 Terms of Service
              </Button>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}