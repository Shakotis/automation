'use client';

import { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Checkbox } from "@heroui/checkbox";
import { Chip } from "@heroui/chip";
import { Spinner } from "@heroui/spinner";
import { CheckIcon } from "@/components/icons";

interface Site {
  id: string;
  name: string;
  description: string;
}

interface SiteSelectionProps {
  onComplete: (selectedSites: string[]) => void;
  onSkip?: () => void;
}

export default function SiteSelection({ onComplete, onSkip }: SiteSelectionProps) {
  const [sites, setSites] = useState<Site[]>([]);
  const [selectedSites, setSelectedSites] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAvailableSites();
  }, []);

  const fetchAvailableSites = async () => {
    try {
      const response = await fetch('/api/auth/sites/', {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setSites(data.available_sites);
      } else {
        setError('Failed to load available sites');
      }
    } catch (error) {
      setError('Network error while loading sites');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSiteToggle = (siteId: string) => {
    setSelectedSites(prev => 
      prev.includes(siteId) 
        ? prev.filter(id => id !== siteId)
        : [...prev, siteId]
    );
  };

  const handleContinue = async () => {
    if (selectedSites.length === 0) {
      setError('Please select at least one site to continue');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/sites/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          selected_sites: selectedSites,
        }),
      });

      if (response.ok) {
        onComplete(selectedSites);
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to save site selection');
      }
    } catch (error) {
      setError('Network error while saving selection');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Spinner size="lg" label="Loading available sites..." />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card className="mb-6">
        <CardHeader className="pb-0">
          <div className="w-full text-center">
            <h1 className="text-2xl font-bold mb-2">Welcome! 🎓</h1>
            <p className="text-default-600">
              Let's set up your homework scraper. Select which educational sites you want to monitor:
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {sites.map((site) => (
          <Card 
            key={site.id} 
            className={`cursor-pointer transition-all hover:scale-105 ${
              selectedSites.includes(site.id) 
                ? 'border-primary shadow-lg' 
                : 'border-default-200'
            }`}
            isPressable
            onPress={() => handleSiteToggle(site.id)}
          >
            <CardBody className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-2">{site.name}</h3>
                  <p className="text-default-600 text-sm">{site.description}</p>
                </div>
                <Checkbox
                  isSelected={selectedSites.includes(site.id)}
                  onChange={() => handleSiteToggle(site.id)}
                  color="primary"
                  size="lg"
                />
              </div>
              
              {selectedSites.includes(site.id) && (
                <Chip 
                  color="primary" 
                  variant="flat" 
                  startContent={<CheckIcon size={16} />}
                  className="mt-2"
                >
                  Selected
                </Chip>
              )}
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <Button
          color="primary"
          size="lg"
          onPress={handleContinue}
          isDisabled={selectedSites.length === 0 || isSaving}
          isLoading={isSaving}
          className="w-full sm:w-auto"
        >
          {isSaving ? 'Saving Selection...' : `Continue with ${selectedSites.length} site${selectedSites.length !== 1 ? 's' : ''}`}
        </Button>
        
        {onSkip && (
          <Button
            variant="ghost"
            size="lg"
            onPress={onSkip}
            isDisabled={isSaving}
            className="w-full sm:w-auto"
          >
            Skip for now
          </Button>
        )}
      </div>

      <div className="mt-8 text-center">
        <p className="text-sm text-default-500">
          Don't worry, you can always change these settings later in your dashboard.
        </p>
      </div>
    </div>
  );
}