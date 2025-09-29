"use client";

import { useState, useEffect } from "react";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Switch } from "@heroui/switch";
import { Input } from "@heroui/input";
import { Divider } from "@heroui/divider";
import { Chip } from "@heroui/chip";
import { title } from "@/components/primitives";

interface UserPreferences {
  enable_manodienynas: boolean;
  enable_eduka: boolean;
  auto_sync_to_google_tasks: boolean;
  scraping_frequency_hours: number;
  last_scraped_manodienynas: string | null;
  last_scraped_eduka: string | null;
}

interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  has_google_oauth: boolean;
}

export default function SettingsPage() {
  const [preferences, setPreferences] = useState<UserPreferences>({
    enable_manodienynas: true,
    enable_eduka: true,
    auto_sync_to_google_tasks: true,
    scraping_frequency_hours: 6,
    last_scraped_manodienynas: null,
    last_scraped_eduka: null,
  });
  
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      // Mock data for demo
      setUserProfile({
        id: 1,
        email: "user@example.com",
        first_name: "Vardas",
        last_name: "Pavardė",
        has_google_oauth: true,
      });
      
      setPreferences({
        enable_manodienynas: true,
        enable_eduka: true,
        auto_sync_to_google_tasks: true,
        scraping_frequency_hours: 6,
        last_scraped_manodienynas: new Date().toISOString(),
        last_scraped_eduka: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    setSaving(true);
    try {
      // const response = await fetch('/api/scraper/preferences/', {
      //   method: 'PUT',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(preferences),
      // });
      
      // Mock save
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      console.log('Preferences saved:', preferences);
    } catch (error) {
      console.error('Error saving preferences:', error);
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
            <div className="space-y-4">
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

              <Divider />

              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium">Auto-sync to Google Tasks</h3>
                  <p className="text-sm text-default-500">
                    Automatically sync scraped homework to Google Tasks
                  </p>
                </div>
                <Switch
                  isSelected={preferences.auto_sync_to_google_tasks}
                  onValueChange={(value) => 
                    setPreferences(prev => ({ ...prev, auto_sync_to_google_tasks: value }))
                  }
                />
              </div>

              <Divider />

              <div>
                <label className="block text-sm font-medium mb-2">
                  Scraping Frequency (hours)
                </label>
                <Input
                  type="number"
                  min="1"
                  max="24"
                  value={preferences.scraping_frequency_hours.toString()}
                  onChange={(e) => 
                    setPreferences(prev => ({ 
                      ...prev, 
                      scraping_frequency_hours: parseInt(e.target.value) || 6 
                    }))
                  }
                  variant="bordered"
                  description="How often to automatically scrape for new homework (1-24 hours)"
                  className="max-w-xs"
                />
              </div>
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
          onPress={handleSavePreferences}
          isLoading={saving}
          disabled={saving}
        >
          Save Settings
        </Button>
        <Button
          variant="bordered"
          onPress={fetchUserData}
          disabled={saving}
        >
          Reset to Default
        </Button>
      </div>
    </div>
  );
}