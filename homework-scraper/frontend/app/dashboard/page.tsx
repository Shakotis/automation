"use client";

import { useState, useEffect } from "react";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Progress } from "@heroui/progress";
import { Divider } from "@heroui/divider";
import { Spinner } from "@heroui/spinner";
import { Switch } from "@heroui/switch";
import { addToast } from "@heroui/toast";
import { title } from "@/components/primitives";

interface HomeworkItem {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  subject: string;
  site: string;
  synced_to_google_tasks: boolean;
  scraped_at: string;
  completed: boolean;
  completed_at: string | null;
}

interface DashboardStats {
  total_homework: number;
  synced_homework: number;
  completed_homework: number;
  pending_homework: number;
  overdue_homework: number;
  sites_enabled: string[];
  last_scrape: string | null;
  tomorrow_total: number;
}

type FilterStatus = 'all' | 'upcoming' | 'overdue' | 'completed' | 'deleted';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [homework, setHomework] = useState<HomeworkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [filter, setFilter] = useState<FilterStatus>('all');
  const [error, setError] = useState<string | null>(null);
  const [showDeleted, setShowDeleted] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, [filter, showDeleted]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch stats
      const statsResponse = await fetch('/api/scraper/stats/', {
        credentials: 'include', // Include cookies for authentication
      });
      
      // If unauthorized, show toast and redirect to login
      if (statsResponse.status === 401) {
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in with Google to view homework',
          color: 'danger',
        });
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        return;
      }
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      } else {
        // Silently handle stats fetch error - not critical
        console.warn('Failed to fetch stats:', statsResponse.statusText);
      }

      // Fetch homework based on filter
      let homeworkUrl = '/api/scraper/homework/';
      const params = new URLSearchParams();
      
      if (showDeleted) {
        params.append('deleted', 'true');
      }
      
      if (filter !== 'all' && filter !== 'deleted') {
        params.append('status', filter);
      }
      
      if (params.toString()) {
        homeworkUrl += `?${params.toString()}`;
      }
      
      const homeworkResponse = await fetch(homeworkUrl, {
        credentials: 'include', // Include cookies for authentication
      });
      
      if (homeworkResponse.status === 401) {
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in with Google to view homework',
          color: 'danger',
        });
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        return;
      }
      
      if (homeworkResponse.ok) {
        const homeworkData = await homeworkResponse.json();
        // Handle paginated response
        const results = homeworkData.results || homeworkData;
        setHomework(Array.isArray(results) ? results : []);
      } else if (homeworkResponse.status === 404) {
        addToast({
          title: 'Backend Connection Failed',
          description: 'Could not connect to backend server',
          color: 'danger',
        });
        setHomework([]);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Show toast for connection errors
      addToast({
        title: 'Connection Error',
        description: 'Failed to connect to backend server',
        color: 'danger',
      });
      setHomework([]);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeNow = async () => {
    setScraping(true);
    setError(null);
    try {
      // First, check if user has credentials before attempting to scrape
      const credResponse = await fetch('/api/auth/credentials', {
        credentials: 'include',
      });
      
      if (credResponse.ok) {
        const credData = await credResponse.json();
        const hasCredentials = credData.credentials && Object.keys(credData.credentials).length > 0;
        
        if (!hasCredentials) {
          addToast({
            title: 'No Credentials',
            description: 'Please add your school credentials in Settings',
            color: 'warning',
          });
          setScraping(false);
          window.location.href = '/settings?setup=credentials';
          return;
        }
      } else if (credResponse.status === 401) {
        addToast({
          title: 'Authentication Required',
          description: 'Please sign in with Google first',
          color: 'danger',
        });
        setScraping(false);
        setTimeout(() => {
          window.location.href = '/';
        }, 2000);
        return;
      }
      
      // Now proceed with scraping
      const scrapePromise = (async () => {
        try {
          const response = await fetch('/api/scraper/homework/scrape', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
          });
          
          if (response.ok) {
            const result = await response.json();
            await fetchDashboardData();
            const message = result.synced_count !== undefined
              ? `Scraped ${result.scraped_count} items and synced ${result.synced_count} to Google Tasks`
              : `Scraped ${result.scraped_count} homework items`;
            return { success: true, message };
          } else if (response.status === 401) {
            setTimeout(() => {
              window.location.href = '/';
            }, 2000);
            throw new Error('Authentication required - please sign in');
          } else {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.error || 'Failed to scrape homework';
            
            // If error mentions credentials, suggest going to settings
            if (errorMessage.toLowerCase().includes('credential')) {
              setTimeout(() => {
                if (confirm('Would you like to go to Settings to add/verify your credentials?')) {
                  window.location.href = '/settings?setup=credentials';
                }
              }, 1000);
            }
            throw new Error(errorMessage);
          }
        } catch (networkError) {
          // Handle network/connection errors
          if (networkError instanceof Error) {
            throw networkError;
          }
          throw new Error('Failed to connect to backend server');
        }
      })();

      addToast({
        title: 'Scraping Homework',
        description: 'Fetching latest homework from school websites...',
        color: 'warning',
        promise: scrapePromise.then(
          (result) => ({
            title: 'Scraping Complete',
            description: result.message,
            color: 'success' as const,
          }),
          (error) => ({
            title: 'Scraping Failed',
            description: error instanceof Error ? error.message : 'Unknown error',
            color: 'danger' as const,
          })
        ),
      });

      try {
        await scrapePromise;
      } catch (error) {
        // Error already handled by toast via promise rejection
        // Silently catch to prevent console error
      }
    } catch (error) {
      console.error('Error in scrape handler:', error);
      // Toast already shown via promise
    } finally {
      setScraping(false);
    }
  };

  const handleToggleComplete = async (homeworkId: number, currentStatus: boolean) => {
    try {
      const response = await fetch(`/api/scraper/homework/${homeworkId}/complete/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          completed: !currentStatus,
        }),
      });

      if (response.ok) {
        // Update local state
        setHomework(homework.map(hw => 
          hw.id === homeworkId 
            ? { ...hw, completed: !currentStatus, completed_at: !currentStatus ? new Date().toISOString() : null }
            : hw
        ));
        // Refresh stats
        fetchDashboardData();
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update homework status');
      }
    } catch (error) {
      console.error('Error toggling homework completion:', error);
      setError('Failed to update homework status');
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No due date';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return `Overdue by ${Math.abs(diffDays)} day${Math.abs(diffDays) !== 1 ? 's' : ''}`;
    } else if (diffDays === 0) {
      return 'Due today';
    } else if (diffDays === 1) {
      return 'Due tomorrow';
    } else if (diffDays <= 7) {
      return `Due in ${diffDays} days`;
    }
    
    return date.toLocaleDateString('lt-LT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getSiteColor = (site: string) => {
    return site === 'manodienynas' ? 'primary' : 'secondary';
  };

  const getDueDateColor = (dueDate: string | null, completed: boolean) => {
    if (completed) return 'success';
    if (!dueDate) return 'default';
    
    const date = new Date(dueDate);
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) return 'danger';
    if (diffDays <= 2) return 'warning';
    return 'success';
  };

  if (loading && !homework.length) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="flex justify-between items-center mb-8">
        <h1 className={title()}>Homework</h1>
        <Button
          color="primary"
          onPress={handleScrapeNow}
          isLoading={scraping}
          disabled={scraping}
        >
          {scraping ? 'Scraping...' : 'Scrape Now'}
        </Button>
      </div>

      {error && (
        <Card className="mb-6 border-danger">
          <CardBody>
            <p className="text-danger">{error}</p>
          </CardBody>
        </Card>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <Card className="hover:scale-105 transition-transform">
          <CardBody className="text-center py-6">
            <div className="text-4xl font-bold text-primary mb-2">
              {stats?.total_homework || 0}
            </div>
            <div className="text-sm text-default-500">This Week</div>
          </CardBody>
        </Card>

        <Card className="hover:scale-105 transition-transform">
          <CardBody className="text-center py-6">
            <div className="text-4xl font-bold text-warning mb-2">
              {stats?.pending_homework || 0}
            </div>
            <div className="text-sm text-default-500">Pending</div>
          </CardBody>
        </Card>

        <Card className="hover:scale-105 transition-transform">
          <CardBody className="text-center py-6">
            <div className="text-4xl font-bold text-success mb-2">
              {stats?.completed_homework || 0}
            </div>
            <div className="text-sm text-default-500">Completed</div>
          </CardBody>
        </Card>
      </div>

      {/* Completion Rate Progress */}
      {stats && stats.tomorrow_total > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <h3 className="text-lg font-semibold">Tomorrow's Tasks Completion</h3>
          </CardHeader>
          <CardBody>
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm">Completion Rate (Tomorrow)</span>
                <span className="text-sm text-default-500">
                  {stats.completed_homework}/{stats.tomorrow_total} ({Math.round((stats.completed_homework / stats.tomorrow_total) * 100)}%)
                </span>
              </div>
              <Progress
                value={(stats.completed_homework / stats.tomorrow_total) * 100}
                color="success"
                size="md"
              />
            </div>
          </CardBody>
        </Card>
      )}

      {/* Filter Buttons */}
      <div className="flex gap-2 mb-6 flex-wrap items-center">
        <Button
          size="sm"
          color={filter === 'all' && !showDeleted ? 'primary' : 'default'}
          variant={filter === 'all' && !showDeleted ? 'solid' : 'bordered'}
          onPress={() => { setFilter('all'); setShowDeleted(false); }}
        >
          This Week ({stats?.total_homework || 0})
        </Button>
        <Button
          size="sm"
          color={filter === 'upcoming' ? 'success' : 'default'}
          variant={filter === 'upcoming' ? 'solid' : 'bordered'}
          onPress={() => { setFilter('upcoming'); setShowDeleted(false); }}
        >
          Upcoming ({stats?.pending_homework || 0})
        </Button>
        <Button
          size="sm"
          color={filter === 'completed' ? 'success' : 'default'}
          variant={filter === 'completed' ? 'solid' : 'bordered'}
          onPress={() => { setFilter('completed'); setShowDeleted(false); }}
        >
          Completed ({stats?.completed_homework || 0})
        </Button>
        
        <Switch
          isSelected={showDeleted}
          onValueChange={(checked) => {
            setShowDeleted(checked);
            if (checked) {
              setFilter('all');
            }
          }}
          size="sm"
          color="danger"
        >
          Show Deleted
        </Switch>
      </div>

      {/* Homework List */}
      <Card>
        <CardHeader className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">
            {showDeleted && 'Deleted Tasks'}
            {!showDeleted && filter === 'all' && 'This Week\'s Homework'}
            {filter === 'upcoming' && 'Upcoming Homework'}
            {filter === 'completed' && 'Completed Homework'}
          </h3>
          {stats?.last_scrape && (
            <span className="text-xs text-default-400">
              Last scraped: {new Date(stats.last_scrape).toLocaleString('lt-LT')}
            </span>
          )}
        </CardHeader>
        <CardBody>
          {homework.length === 0 ? (
            <div className="text-center py-12 text-default-400">
              <p className="text-lg mb-2">No homework found</p>
              <p className="text-sm">
                {filter !== 'all' 
                  ? `Try changing the filter or scraping for new homework`
                  : 'Click "Scrape Now" to fetch your homework'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {homework.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-2xl font-semibold text-default-400 mb-2">
                    No homework left
                  </p>
                  <p className="text-default-500">
                    {showDeleted 
                      ? "No deleted tasks to show"
                      : "Great job! You're all caught up! 🎉"
                    }
                  </p>
                </div>
              ) : (
                homework.map((item, index) => (
                <div key={item.id} className={`p-4 rounded-lg border ${item.completed ? 'bg-default-50 opacity-70' : 'bg-default-100'} hover:bg-default-200 transition-all`}>
                  <div className="flex items-start gap-4">
                    <div className="pt-1">
                      <input
                        type="checkbox"
                        checked={item.completed}
                        onChange={() => handleToggleComplete(item.id, item.completed)}
                        className="w-5 h-5 rounded cursor-pointer"
                      />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h4 className={`font-semibold text-lg ${item.completed ? 'line-through text-default-400' : ''}`}>
                          {item.title}
                        </h4>
                        <div className="flex gap-2 flex-shrink-0">
                          <Chip
                            size="sm"
                            color={getSiteColor(item.site)}
                            variant="flat"
                          >
                            {item.site}
                          </Chip>
                          {item.synced_to_google_tasks && (
                            <Chip size="sm" color="success" variant="flat">
                              ✓ Synced
                            </Chip>
                          )}
                        </div>
                      </div>
                      <p className={`text-sm mb-3 ${item.completed ? 'text-default-400' : 'text-default-600'}`}>
                        {item.description}
                      </p>
                      <div className="flex items-center gap-4 text-xs flex-wrap">
                        <Chip
                          size="sm"
                          variant="flat"
                          color="default"
                        >
                          📚 {item.subject}
                        </Chip>
                        <Chip
                          size="sm"
                          variant="flat"
                          color={getDueDateColor(item.due_date, item.completed)}
                        >
                          📅 {formatDate(item.due_date)}
                        </Chip>
                        {item.completed && item.completed_at && (
                          <Chip
                            size="sm"
                            variant="flat"
                            color="success"
                          >
                            ✓ Completed {new Date(item.completed_at).toLocaleDateString('lt-LT')}
                          </Chip>
                        )}
                      </div>
                    </div>
                  </div>
                  {index < homework.length - 1 && <Divider className="mt-4" />}
                </div>
              ))
              )}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}