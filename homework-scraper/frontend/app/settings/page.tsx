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
    
    const verifyPromise = (async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/auth/verify-credentials`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ site }),
        });

        if (response.ok) {
          const data = await response.json();
          await fetchCredentials(); // Refresh to get updated verification status
          
          if (data.success) {
            return { success: true, message: `Credentials verified successfully for ${site}` };
          } else {
            throw new Error(data.message);
          }
        } else {
          let errorMessage = 'Verification failed';
          try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorMessage;
          } catch (e) {
            errorMessage = response.statusText || errorMessage;
          }
          throw new Error(errorMessage);
        }
      } catch (error) {
        console.error('Error verifying credential:', error);
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
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="font-medium">{displayName}</h3>
            <p className="text-sm text-default-500">{description}</p>
            {credential && (
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-default-400">
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
          <div className="flex items-center gap-2">
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
            >
              {credential ? 'Edit' : 'Add Credentials'}
            </Button>
          </div>
        </div>

        {isExpanded && (
          <Card className="bg-default-50">
            <CardBody className="space-y-4">
              <Input
                label="Username/Email"
                placeholder="Enter your username or email"
                value={localUsername}
                onChange={(e) => setLocalUsername(e.target.value)}
                variant="bordered"
                isRequired
              />
              <Input
                label="Password"
                placeholder="Enter your password"
                type={showPassword ? 'text' : 'password'}
                value={localPassword}
                onChange={(e) => setLocalPassword(e.target.value)}
                variant="bordered"
                isRequired
                endContent={
                  <Button
                    size="sm"
                    variant="light"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? '👁️‍🗨️' : '👁️'}
                  </Button>
                }
              />
              <div className="flex gap-2">
                <Button
                  color="primary"
                  onClick={handleSave}
                  isDisabled={!localUsername || !localPassword}
                  isLoading={savingCredential === site}
                >
                  {savingCredential === site ? 'Saving...' : 'Save & Verify'}
                </Button>
                <Button
                  variant="bordered"
                  onClick={toggleForm}
                >
                  Cancel
                </Button>
              </div>
              <div className="text-xs text-default-500">
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
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className={title({ class: "mb-8" })}>Settings</h1>

      {/* Credentials Setup Prompt */}
      {showCredentialsPrompt && userProfile && (
        <Card className="mb-6 border-primary-200 bg-primary-50">
          <CardBody>
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="text-primary-600 text-2xl">🔐</div>
                <div>
                  <h3 className="font-semibold text-primary-800">Setup Your Site Credentials</h3>
                  <p className="text-primary-700 text-sm">
                    To start scraping homework, please add your Manodienynas or Eduka credentials below.
                  </p>
                </div>
              </div>
              <Button
                size="sm"
                color="default"
                variant="light"
                onClick={() => setShowCredentialsPrompt(false)}
              >
                ✕
              </Button>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Authentication Warning */}
      {!userProfile && (
        <Card className="mb-6 border-warning-200 bg-warning-50">
          <CardBody>
            <div className="flex items-center gap-3">
              <div className="text-warning-600 text-2xl">⚠️</div>
              <div>
                <h3 className="font-semibold text-warning-800">Authentication Required</h3>
                <p className="text-warning-700 text-sm">
                  You need to sign in with Google to save credentials and access all settings.
                </p>
                <Button
                  size="sm"
                  color="warning"
                  variant="bordered"
                  className="mt-2"
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
      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-xl font-semibold">User Profile</h2>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Email</label>
                <Input
                  value={userProfile?.email || ''}
                  isReadOnly
                  variant="bordered"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <Input
                  value={`${userProfile?.first_name || ''} ${userProfile?.last_name || ''}`}
                  isReadOnly
                  variant="bordered"
                />
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium">Google OAuth Status:</span>
              {userProfile?.has_google_oauth ? (
                <Chip color="success" variant="flat">
                  ✓ Connected
                </Chip>
              ) : (
                <div className="flex items-center gap-2">
                  <Chip color="warning" variant="flat">
                    Not Connected
                  </Chip>
                  <Button
                    size="sm"
                    color="primary"
                    onPress={handleGoogleAuth}
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
      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-xl font-semibold">Scraping Settings</h2>
        </CardHeader>
        <CardBody>
          <div className="space-y-6">
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium">Enable Manodienynas.lt</h3>
                  <p className="text-sm text-default-500">
                    Scrape homework from Manodienynas.lt
                  </p>
                  {preferences.last_scraped_manodienynas && (
                    <p className="text-xs text-default-400">
                      Last scraped: {formatDate(preferences.last_scraped_manodienynas)}
                    </p>
                  )}
                </div>
                <Switch
                  isSelected={preferences.enable_manodienynas}
                  onValueChange={(value) => 
                    setPreferences(prev => ({ ...prev, enable_manodienynas: value }))
                  }
                />
              </div>

              {preferences.enable_manodienynas && (
                <div className="ml-4 pl-4 border-l-2 border-primary-200">
                  <CredentialSection
                    site="manodienynas"
                    displayName="Manodienynas Credentials"
                    description="Enter your Manodienynas.lt login credentials to enable automatic scraping"
                  />
                </div>
              )}

              <Divider />

              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium">Enable Eduka.lt</h3>
                  <p className="text-sm text-default-500">
                    Scrape homework from Eduka.lt
                  </p>
                  {preferences.last_scraped_eduka && (
                    <p className="text-xs text-default-400">
                      Last scraped: {formatDate(preferences.last_scraped_eduka)}
                    </p>
                  )}
                </div>
                <Switch
                  isSelected={preferences.enable_eduka}
                  onValueChange={(value) => 
                    setPreferences(prev => ({ ...prev, enable_eduka: value }))
                  }
                />
              </div>

              {preferences.enable_eduka && (
                <div className="ml-4 pl-4 border-l-2 border-secondary-200">
                  <CredentialSection
                    site="eduka"
                    displayName="Eduka Credentials"
                    description="Enter your Eduka.lt login credentials to enable automatic scraping"
                  />
                </div>
              )}
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Sync Settings */}
      <Card className="mb-6">
        <CardHeader>
          <h2 className="text-xl font-semibold">Google Tasks Integration</h2>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-default-50 rounded-lg">
              <div>
                <h3 className="font-medium">Google Tasks Sync</h3>
                <p className="text-sm text-default-500">
                  Sync homework to "Homework" task list in Google Tasks
                </p>
              </div>
              {userProfile?.has_google_oauth ? (
                <Chip color="success" variant="flat">
                  ✓ Ready
                </Chip>
              ) : (
                <Button
                  size="sm"
                  color="primary"
                  onPress={handleGoogleAuth}
                >
                  Setup Google Tasks
                </Button>
              )}
            </div>

            <Divider />

            <div>
              <label className="block text-sm font-medium mb-2">
                Google Tasks Title Format
              </label>
              <Select
                selectedKeys={[preferences.google_tasks_title_format]}
                onSelectionChange={(keys) => {
                  const value = Array.from(keys)[0] as 'title' | 'subject';
                  setPreferences(prev => ({ ...prev, google_tasks_title_format: value }));
                }}
                variant="bordered"
                className="max-w-xs"
                description="Choose what to display as the task title in Google Tasks"
              >
                <SelectItem key="title">
                  Task Title (e.g., "Complete math worksheet")
                </SelectItem>
                <SelectItem key="subject">
                  Subject Name (e.g., "Mathematics")
                </SelectItem>
              </Select>
              <p className="text-xs text-default-500 mt-2">
                {preferences.google_tasks_title_format === 'title' 
                  ? "The task title will be shown in Google Tasks, with subject in notes"
                  : "The subject will be shown in Google Tasks, with task title in notes"}
              </p>
            </div>

            <Divider />

            <div className="text-sm text-default-500">
              <p>
                • Homework will be created as tasks in your Google Tasks "Homework" list
              </p>
              <p>
                • Due dates will be preserved when available
              </p>
              <p>
                • Task descriptions will include subject and source information
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          color="primary"
          onPress={() => {
            if (!requireAuth('save settings')) return;
            handleSavePreferences();
          }}
          isLoading={saving}
          disabled={saving}
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
        >
          Reset to Default
        </Button>
      </div>
    </div>
  );
}