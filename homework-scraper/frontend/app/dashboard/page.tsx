"use client";

import { useState, useEffect } from "react";
import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Progress } from "@heroui/progress";
import { Divider } from "@heroui/divider";
import { Spinner } from "@heroui/spinner";
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
}

type FilterStatus = 'all' | 'upcoming' | 'overdue' | 'completed';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [homework, setHomework] = useState<HomeworkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [filter, setFilter] = useState<FilterStatus>('all');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, [filter]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch stats
      const statsResponse = await fetch('/api/scraper/stats/', {
        credentials: 'include', // Include cookies for authentication
      });
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch homework based on filter
      let homeworkUrl = '/api/scraper/homework/';
      if (filter !== 'all') {
        homeworkUrl += `?status=${filter}`;
      }
      
      const homeworkResponse = await fetch(homeworkUrl, {
        credentials: 'include', // Include cookies for authentication
      });
      if (homeworkResponse.ok) {
        const homeworkData = await homeworkResponse.json();
        // Handle paginated response
        const results = homeworkData.results || homeworkData;
        setHomework(Array.isArray(results) ? results : []);
      } else if (homeworkResponse.status === 404) {
        setError('API endpoint not found. Please ensure the backend server is running.');
        setHomework([]);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to fetch homework data. Please check your connection.');
      setHomework([]);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeNow = async () => {
    setScraping(true);
    setError(null);
    try {
      const response = await fetch('/api/scraper/homework/scrape/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important: include cookies for authentication
      });
      
      if (response.ok) {
        const result = await response.json();
        const message = result.synced_count !== undefined
          ? `✅ Successfully scraped ${result.scraped_count} homework items and synced ${result.synced_count} to Google Tasks!`
          : `✅ Successfully scraped ${result.scraped_count} homework items!`;
        alert(message);
        await fetchDashboardData();
      } else if (response.status === 401) {
        setError('Please sign in with Google to scrape homework.');
        alert('⚠️ Please sign in with Google first to scrape homework.');
        window.location.href = '/auth/google';
      } else {
        const errorData = await response.json();
        const errorMessage = errorData.error || 'Failed to scrape homework';
        setError(errorMessage);
        alert(`❌ ${errorMessage}`);
        
        // If error mentions credentials, suggest going to settings
        if (errorMessage.toLowerCase().includes('credential')) {
          if (confirm('Would you like to go to Settings to add/verify your credentials?')) {
            window.location.href = '/settings?setup=credentials';
          }
        }
      }
    } catch (error) {
      console.error('Error scraping homework:', error);
      setError('Failed to scrape homework. Please try again.');
      alert('❌ Network error: Could not connect to the server. Please ensure both servers are running.');
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
        <h1 className={title()}>Homework Dashboard</h1>
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
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        <Card className="hover:scale-105 transition-transform">
          <CardBody className="text-center py-6">
            <div className="text-4xl font-bold text-primary mb-2">
              {stats?.total_homework || 0}
            </div>
            <div className="text-sm text-default-500">Total</div>
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
            <div className="text-4xl font-bold text-danger mb-2">
              {stats?.overdue_homework || 0}
            </div>
            <div className="text-sm text-default-500">Overdue</div>
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

        <Card className="hover:scale-105 transition-transform">
          <CardBody className="text-center py-6">
            <div className="text-4xl font-bold text-secondary mb-2">
              {stats?.synced_homework || 0}
            </div>
            <div className="text-sm text-default-500">Synced</div>
          </CardBody>
        </Card>
      </div>

      {/* Sync Progress */}
      {stats && stats.total_homework > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <h3 className="text-lg font-semibold">Progress Overview</h3>
          </CardHeader>
          <CardBody>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm">Completion Rate</span>
                  <span className="text-sm text-default-500">
                    {stats.completed_homework}/{stats.total_homework} ({Math.round((stats.completed_homework / stats.total_homework) * 100)}%)
                  </span>
                </div>
                <Progress
                  value={(stats.completed_homework / stats.total_homework) * 100}
                  color="success"
                  size="md"
                />
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm">Google Tasks Sync</span>
                  <span className="text-sm text-default-500">
                    {stats.synced_homework}/{stats.total_homework} ({Math.round((stats.synced_homework / stats.total_homework) * 100)}%)
                  </span>
                </div>
                <Progress
                  value={(stats.synced_homework / stats.total_homework) * 100}
                  color="primary"
                  size="md"
                />
              </div>
            </div>
          </CardBody>
        </Card>
      )}

      {/* Filter Buttons */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <Button
          size="sm"
          color={filter === 'all' ? 'primary' : 'default'}
          variant={filter === 'all' ? 'solid' : 'bordered'}
          onPress={() => setFilter('all')}
        >
          All ({stats?.total_homework || 0})
        </Button>
        <Button
          size="sm"
          color={filter === 'upcoming' ? 'success' : 'default'}
          variant={filter === 'upcoming' ? 'solid' : 'bordered'}
          onPress={() => setFilter('upcoming')}
        >
          Upcoming ({stats?.pending_homework || 0})
        </Button>
        <Button
          size="sm"
          color={filter === 'overdue' ? 'danger' : 'default'}
          variant={filter === 'overdue' ? 'solid' : 'bordered'}
          onPress={() => setFilter('overdue')}
        >
          Overdue ({stats?.overdue_homework || 0})
        </Button>
        <Button
          size="sm"
          color={filter === 'completed' ? 'success' : 'default'}
          variant={filter === 'completed' ? 'solid' : 'bordered'}
          onPress={() => setFilter('completed')}
        >
          Completed ({stats?.completed_homework || 0})
        </Button>
      </div>

      {/* Homework List */}
      <Card>
        <CardHeader className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">
            {filter === 'all' && 'All Homework'}
            {filter === 'upcoming' && 'Upcoming Homework'}
            {filter === 'overdue' && 'Overdue Homework'}
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
              {homework.map((item, index) => (
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
              ))}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}