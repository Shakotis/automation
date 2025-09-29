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
}

interface DashboardStats {
  total_homework: number;
  synced_homework: number;
  sites_enabled: string[];
  last_scrape: string | null;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentHomework, setRecentHomework] = useState<HomeworkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch stats
      const statsResponse = await fetch('/api/scraper/homework/?limit=1');
      const homeworkResponse = await fetch('/api/scraper/homework/?limit=5');
      
      // Mock data for demo
      setStats({
        total_homework: 42,
        synced_homework: 38,
        sites_enabled: ['manodienynas', 'eduka'],
        last_scrape: new Date().toISOString(),
      });

      setRecentHomework([
        {
          id: 1,
          title: "Matematikos namų darbai",
          description: "Spręsti uždavinius 15-20",
          due_date: "2025-10-01T10:00:00Z",
          subject: "Matematika",
          site: "manodienynas",
          synced_to_google_tasks: true,
          scraped_at: new Date().toISOString(),
        },
        {
          id: 2,
          title: "Lietuvių kalbos rašinys",
          description: "Parašyti rašinį tema 'Pavasaris'",
          due_date: "2025-10-02T14:00:00Z",
          subject: "Lietuvių kalba",
          site: "eduka",
          synced_to_google_tasks: false,
          scraped_at: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScrapeNow = async () => {
    setScraping(true);
    try {
      const response = await fetch('/api/scraper/homework/scrape/', {
        method: 'POST',
      });
      
      if (response.ok) {
        await fetchDashboardData();
      }
    } catch (error) {
      console.error('Error scraping homework:', error);
    } finally {
      setScraping(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'No due date';
    return new Date(dateString).toLocaleDateString('lt-LT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getSiteColor = (site: string) => {
    return site === 'manodienynas' ? 'primary' : 'secondary';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className={title()}>Dashboard</h1>
        <Button
          color="primary"
          onPress={handleScrapeNow}
          isLoading={scraping}
          disabled={scraping}
        >
          {scraping ? 'Scraping...' : 'Scrape Now'}
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardBody className="text-center">
            <div className="text-3xl font-bold text-primary mb-2">
              {stats?.total_homework || 0}
            </div>
            <div className="text-default-500">Total Homework</div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <div className="text-3xl font-bold text-success mb-2">
              {stats?.synced_homework || 0}
            </div>
            <div className="text-default-500">Synced to Google</div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <div className="text-3xl font-bold text-secondary mb-2">
              {stats?.sites_enabled.length || 0}
            </div>
            <div className="text-default-500">Sites Enabled</div>
          </CardBody>
        </Card>

        <Card>
          <CardBody className="text-center">
            <div className="text-sm text-success mb-2">
              Last Scrape
            </div>
            <div className="text-default-500 text-xs">
              {stats?.last_scrape ? formatDate(stats.last_scrape) : 'Never'}
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Sync Progress */}
      <Card className="mb-8">
        <CardHeader>
          <h3 className="text-lg font-semibold">Sync Progress</h3>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Google Tasks Sync</span>
              <span className="text-sm text-default-500">
                {stats?.synced_homework}/{stats?.total_homework}
              </span>
            </div>
            <Progress
              value={stats ? (stats.synced_homework / stats.total_homework) * 100 : 0}
              color="success"
              size="sm"
            />
          </div>
        </CardBody>
      </Card>

      {/* Recent Homework */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Recent Homework</h3>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            {recentHomework.map((item, index) => (
              <div key={item.id}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium">{item.title}</h4>
                      <Chip
                        size="sm"
                        color={getSiteColor(item.site)}
                        variant="flat"
                      >
                        {item.site}
                      </Chip>
                      {item.synced_to_google_tasks && (
                        <Chip size="sm" color="success" variant="flat">
                          Synced
                        </Chip>
                      )}
                    </div>
                    <p className="text-sm text-default-500 mb-2">
                      {item.description}
                    </p>
                    <div className="flex items-center gap-4 text-xs text-default-400">
                      <span>Subject: {item.subject}</span>
                      <span>Due: {formatDate(item.due_date)}</span>
                    </div>
                  </div>
                </div>
                {index < recentHomework.length - 1 && <Divider className="mt-4" />}
              </div>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  );
}