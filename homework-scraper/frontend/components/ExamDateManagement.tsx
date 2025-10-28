'use client';

import { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import { Select, SelectItem } from "@heroui/select";
import { Chip } from "@heroui/chip";
import { Switch } from "@heroui/switch";
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from "@heroui/modal";
import { addToast } from "@heroui/toast";
import { CheckIcon, TaskIcon } from "@/components/icons";

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? `${window.location.protocol}//${window.location.hostname}:8000/api` : '/api');

interface ScrapedExam {
  id: number;
  exam_name: string;
  subject: string;
  exam_date: string;
  site: string;
  url: string;
  scraped_at: string;
  synced_to_google_calendar: boolean;
  google_calendar_event_id: string;
}

interface ExamEvent {
  id?: string;
  title: string;
  date: string;
  description?: string;
  calendar_id?: string;
}

interface Calendar {
  id: string;
  summary: string;
  description?: string;
}

interface IntegrationPreferences {
  homework_sync_target: 'tasks' | 'calendar';
  exam_sync_target: 'tasks' | 'calendar';
  auto_sync_enabled: boolean;
  preferred_calendar_id?: string;
}

export default function ExamDateManagement() {
  const [scrapedExams, setScrapedExams] = useState<ScrapedExam[]>([]);
  const [isLoadingExams, setIsLoadingExams] = useState(true);
  const [isScrapingExams, setIsScrapingExams] = useState(false);
  const [isSyncingExams, setIsSyncingExams] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [preferences, setPreferences] = useState<IntegrationPreferences>({
    homework_sync_target: 'tasks',
    exam_sync_target: 'calendar',
    auto_sync_enabled: true,
  });
  const [calendars, setCalendars] = useState<Calendar[]>([]);
  const [examForm, setExamForm] = useState<ExamEvent>({
    title: '',
    date: '',
    description: '',
    calendar_id: '',
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isCreatingExam, setIsCreatingExam] = useState(false);
  const [showExamModal, setShowExamModal] = useState(false);
  const [showPreferencesModal, setShowPreferencesModal] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
    loadPreferences();
    loadCalendars();
    loadScrapedExams();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/user`, {
        credentials: 'include',
      });
      setIsAuthenticated(response.ok);
    } catch (error) {
      setIsAuthenticated(false);
    }
  };

  const requireAuth = (action: string) => {
    if (!isAuthenticated) {
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

  const loadScrapedExams = async () => {
    setIsLoadingExams(true);
    try {
      const response = await fetch(`${API_BASE_URL}/scraper/exams`, {
        credentials: 'include',
      });
      
      if (response.status === 401) {
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in with Google to view exams',
          color: 'danger',
        });
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        return;
      }
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          setScrapedExams(data.results || []);
        }
      }
    } catch (error) {
      // Silently handle error - API may not be available yet
    } finally {
      setIsLoadingExams(false);
    }
  };

  const scrapeExams = async () => {
    setIsScrapingExams(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/scraper/exams/scrape`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.status === 401) {
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in with Google to scrape exams',
          color: 'danger',
        });
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        addToast({
          title: 'Exams Scraped',
          description: `Successfully scraped ${data.scraped_count} exams`,
          color: 'success',
        });
        loadScrapedExams(); // Reload exams
      } else {
        const data = await response.json().catch(() => ({}));
        const errorMsg = data.error || 'Failed to scrape exams';
        addToast({
          title: 'Scraping Failed',
          description: errorMsg,
          color: 'danger',
        });
      }
    } catch (error) {
      addToast({
        title: 'Connection Error',
        description: 'Failed to connect to backend server',
        color: 'danger',
      });
    } finally {
      setIsScrapingExams(false);
    }
  };

  const syncExamsToCalendar = async () => {
    setIsSyncingExams(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/scraper/exams/sync-calendar`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.status === 401) {
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in with Google to sync exams',
          color: 'danger',
        });
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        return;
      }
      
      if (response.ok) {
        const data = await response.json();
        addToast({
          title: 'Exams Synced',
          description: `Successfully synced ${data.synced_count} exams to Google Calendar`,
          color: 'success',
        });
        loadScrapedExams(); // Reload to show updated sync status
      } else {
        const data = await response.json().catch(() => ({}));
        const errorMsg = data.error || 'Failed to sync exams';
        addToast({
          title: 'Sync Failed',
          description: errorMsg,
          color: 'danger',
        });
      }
    } catch (error) {
      addToast({
        title: 'Connection Error',
        description: 'Failed to connect to backend server',
        color: 'danger',
      });
    } finally {
      setIsSyncingExams(false);
    }
  };

  const loadPreferences = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/preferences/`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          setPreferences(data.preferences);
        }
      }
    } catch (error) {
      // Silently handle error - API may not be available yet
    }
  };

  const loadCalendars = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/calendar/calendars/`, {
        credentials: 'include',
      });
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          setCalendars(data.calendars || []);
        }
      }
    } catch (error) {
      // Silently handle error - API may not be available yet
    } finally {
      setIsLoading(false);
    }
  };

  const savePreferences = async () => {
    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/tasks/preferences/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(preferences),
      });

      if (response.ok) {
        setSuccess('Preferences saved successfully!');
        setShowPreferencesModal(false);
        setTimeout(() => setSuccess(null), 3000);
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to save preferences');
      }
    } catch (error) {
      setError('Network error while saving preferences');
    } finally {
      setIsSaving(false);
    }
  };

  const createExamEvent = async () => {
    if (!examForm.title || !examForm.date) {
      setError('Title and date are required');
      return;
    }

    setIsCreatingExam(true);
    setError(null);

    try {
      const endpoint = preferences.exam_sync_target === 'calendar' 
        ? `${API_BASE_URL}/tasks/calendar/exam/`
        : `${API_BASE_URL}/tasks/sync/`; // For Google Tasks

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          title: examForm.title,
          date: examForm.date,
          description: examForm.description,
          calendar_id: examForm.calendar_id || preferences.preferred_calendar_id,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`Exam event created successfully in ${preferences.exam_sync_target === 'calendar' ? 'Google Calendar' : 'Google Tasks'}!`);
        setShowExamModal(false);
        setExamForm({ title: '', date: '', description: '', calendar_id: '' });
        setTimeout(() => setSuccess(null), 5000);
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to create exam event');
      }
    } catch (error) {
      setError('Network error while creating exam event');
    } finally {
      setIsCreatingExam(false);
    }
  };

  const handleDateChange = (dateString: string) => {
    setExamForm(prev => ({ ...prev, date: dateString }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader className="pb-0">
          <div className="w-full text-center">
            <h1 className="text-2xl font-bold mb-2">Exam Date Management 📅</h1>
            <p className="text-default-600">
              Create exam events and manage your integration preferences for Google Tasks and Calendar.
            </p>
          </div>
        </CardHeader>
      </Card>

      {/* Status Messages */}
      {error && (
        <Card className="border-danger">
          <CardBody>
            <p className="text-danger text-center">{error}</p>
          </CardBody>
        </Card>
      )}

      {success && (
        <Card className="border-success">
          <CardBody>
            <p className="text-success text-center flex items-center justify-center gap-2">
              <CheckIcon size={16} />
              {success}
            </p>
          </CardBody>
        </Card>
      )}

      {/* Current Preferences */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Current Integration Settings</h3>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="flex items-center justify-between">
              <span>Homework Sync Target:</span>
              <Chip 
                color={preferences.homework_sync_target === 'tasks' ? 'primary' : 'secondary'}
                variant="flat"
                startContent={<TaskIcon size={16} />}
              >
                {preferences.homework_sync_target === 'tasks' ? 'Google Tasks' : 'Google Calendar'}
              </Chip>
            </div>
            <div className="flex items-center justify-between">
              <span>Exam Sync Target:</span>
              <Chip 
                color={preferences.exam_sync_target === 'calendar' ? 'secondary' : 'primary'}
                variant="flat"
                startContent={<TaskIcon size={16} />}
              >
                {preferences.exam_sync_target === 'calendar' ? 'Google Calendar' : 'Google Tasks'}
              </Chip>
            </div>
          </div>
          
          <div className="flex items-center justify-between mb-4">
            <span>Auto-sync enabled:</span>
            <Chip 
              color={preferences.auto_sync_enabled ? 'success' : 'default'}
              variant="flat"
            >
              {preferences.auto_sync_enabled ? 'Yes' : 'No'}
            </Chip>
          </div>

          <Button
            color="primary"
            variant="bordered"
            onPress={() => setShowPreferencesModal(true)}
          >
            Change Settings
          </Button>
        </CardBody>
      </Card>

      {/* Scraped Exams Section */}
      <Card>
        <CardHeader className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">Scraped Exams from Manodienynas</h3>
          <div className="flex gap-2">
            <Button
              color="primary"
              variant="bordered"
              onPress={() => {
                if (!requireAuth('scrape exams')) return;
                scrapeExams();
              }}
              isLoading={isScrapingExams}
              size="sm"
            >
              🔄 Scrape Exams
            </Button>
            <Button
              color="success"
              variant="bordered"
              onPress={() => {
                if (!requireAuth('sync exams to calendar')) return;
                syncExamsToCalendar();
              }}
              isLoading={isSyncingExams}
              size="sm"
            >
              📅 Sync to Calendar
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          {isLoadingExams ? (
            <div className="text-center py-8">
              <p className="text-default-600">Loading exams...</p>
            </div>
          ) : scrapedExams.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-default-600 mb-4">No exams found</p>
              <Button
                color="primary"
                onPress={() => {
                  if (!requireAuth('scrape exams')) return;
                  scrapeExams();
                }}
                isLoading={isScrapingExams}
              >
                Scrape Exams from Manodienynas
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {scrapedExams.map((exam) => (
                <Card key={exam.id} className={exam.synced_to_google_calendar ? "bg-success-50" : ""}>
                  <CardBody>
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-semibold text-lg">{exam.exam_name}</h4>
                        <div className="flex items-center gap-4 text-sm text-default-600 mt-1">
                          <span>📚 {exam.subject}</span>
                          <span>📅 {new Date(exam.exam_date).toLocaleDateString()}</span>
                          <span>🌐 {exam.site}</span>
                        </div>
                      </div>
                      <div>
                        {exam.synced_to_google_calendar ? (
                          <Chip size="sm" color="success" variant="flat">
                            ✓ Synced to Calendar
                          </Chip>
                        ) : (
                          <Chip size="sm" color="warning" variant="flat">
                            Not Synced
                          </Chip>
                        )}
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
        <Card className="p-6">
          <CardBody className="text-center">
            <div className="text-4xl mb-4">📝</div>
            <h3 className="text-lg font-semibold mb-2">Create Exam Event</h3>
            <p className="text-default-600 mb-4">
              Add a new exam date to your {preferences.exam_sync_target === 'calendar' ? 'Google Calendar' : 'Google Tasks'}.
            </p>
            <Button
              color="primary"
              onPress={() => {
                if (!requireAuth('add exam dates')) return;
                setShowExamModal(true);
              }}
            >
              Add Exam Date
            </Button>
          </CardBody>
        </Card>
      </div>

      {/* Exam Creation Modal */}
      <Modal 
        isOpen={showExamModal} 
        onClose={() => setShowExamModal(false)}
        size="lg"
      >
        <ModalContent>
          <ModalHeader>
            <h3 className="text-xl font-bold">Create Exam Event</h3>
          </ModalHeader>
          <ModalBody>
            <div className="space-y-4">
              <Input
                label="Exam Title"
                placeholder="e.g., Math Final Exam"
                value={examForm.title}
                onChange={(e) => setExamForm(prev => ({ ...prev, title: e.target.value }))}
                isRequired
              />

              <Input
                label="Exam Date"
                type="date"
                value={examForm.date}
                onChange={(e) => handleDateChange(e.target.value)}
                isRequired
              />

              <Input
                label="Description (Optional)"
                placeholder="Additional details about the exam..."
                value={examForm.description}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setExamForm(prev => ({ ...prev, description: e.target.value }))}
              />

              {preferences.exam_sync_target === 'calendar' && calendars.length > 0 && (
                <Select
                  label="Calendar (Optional)"
                  placeholder="Choose a specific calendar"
                  selectedKeys={examForm.calendar_id ? [examForm.calendar_id] : []}
                  onSelectionChange={(keys) => {
                    const selected = Array.from(keys)[0] as string;
                    setExamForm(prev => ({ ...prev, calendar_id: selected }));
                  }}
                >
                  {calendars.map((calendar) => (
                    <SelectItem key={calendar.id}>
                      {calendar.summary}
                    </SelectItem>
                  ))}
                </Select>
              )}

              <div className="p-3 bg-default-100 rounded-lg">
                <p className="text-sm text-default-700">
                  This exam will be created in{' '}
                  <strong>
                    {preferences.exam_sync_target === 'calendar' ? 'Google Calendar' : 'Google Tasks'}
                  </strong>
                  . You can change this preference in the settings.
                </p>
              </div>
            </div>
          </ModalBody>
          <ModalFooter>
            <Button
              variant="light"
              onPress={() => setShowExamModal(false)}
            >
              Cancel
            </Button>
            <Button
              color="primary"
              onPress={createExamEvent}
              isLoading={isCreatingExam}
            >
              Create Exam Event
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Preferences Modal */}
      <Modal 
        isOpen={showPreferencesModal} 
        onClose={() => setShowPreferencesModal(false)}
        size="lg"
      >
        <ModalContent>
          <ModalHeader>
            <h3 className="text-xl font-bold">Integration Preferences</h3>
          </ModalHeader>
          <ModalBody>
            <div className="space-y-6">
              <div>
                <label className="text-sm font-medium mb-2 block">Homework Sync Target</label>
                <Select
                  selectedKeys={[preferences.homework_sync_target]}
                  onSelectionChange={(keys) => {
                    const selected = Array.from(keys)[0] as 'tasks' | 'calendar';
                    setPreferences(prev => ({ ...prev, homework_sync_target: selected }));
                  }}
                >
                  <SelectItem key="tasks">Google Tasks</SelectItem>
                  <SelectItem key="calendar">Google Calendar</SelectItem>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Exam Sync Target</label>
                <Select
                  selectedKeys={[preferences.exam_sync_target]}
                  onSelectionChange={(keys) => {
                    const selected = Array.from(keys)[0] as 'tasks' | 'calendar';
                    setPreferences(prev => ({ ...prev, exam_sync_target: selected }));
                  }}
                >
                  <SelectItem key="calendar">Google Calendar</SelectItem>
                  <SelectItem key="tasks">Google Tasks</SelectItem>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Auto-sync enabled</p>
                  <p className="text-sm text-default-600">Automatically sync new homework and exams</p>
                </div>
                <Switch
                  isSelected={preferences.auto_sync_enabled}
                  onValueChange={(checked) => setPreferences(prev => ({ ...prev, auto_sync_enabled: checked }))}
                />
              </div>

              {calendars.length > 0 && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Preferred Calendar (Optional)</label>
                  <Select
                    placeholder="Choose a default calendar"
                    selectedKeys={preferences.preferred_calendar_id ? [preferences.preferred_calendar_id] : []}
                    onSelectionChange={(keys) => {
                      const selected = Array.from(keys)[0] as string;
                      setPreferences(prev => ({ ...prev, preferred_calendar_id: selected }));
                    }}
                  >
                    {calendars.map((calendar) => (
                      <SelectItem key={calendar.id}>
                        {calendar.summary}
                      </SelectItem>
                    ))}
                  </Select>
                </div>
              )}
            </div>
          </ModalBody>
          <ModalFooter>
            <Button
              variant="light"
              onPress={() => setShowPreferencesModal(false)}
            >
              Cancel
            </Button>
            <Button
              color="primary"
              onPress={savePreferences}
              isLoading={isSaving}
            >
              Save Preferences
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
}