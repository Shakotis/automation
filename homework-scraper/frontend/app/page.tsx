'use client';

import { useState, useEffect } from "react";
import { Link } from "@heroui/link";
import { Button } from "@heroui/button";
import { Card, CardBody } from "@heroui/card";
import { Chip } from "@heroui/chip";

import { title, subtitle } from "@/components/primitives";
import { GoogleIcon, TaskIcon, ScrapingIcon } from "@/components/icons";
import GoogleSignInButton from "@/components/GoogleSignInButton";
import { authAPI } from "@/lib/api";

// Get API base URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';
console.log('[Home] Using API_BASE_URL:', API_BASE_URL);

interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  has_google_oauth: boolean;
}

interface HomeworkItem {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  subject: string;
  site: string;
  synced_to_google_tasks: boolean;
  completed: boolean;
}

// Demo homework data (shown to non-authenticated users)
const demoHomework: HomeworkItem[] = [
  {
    id: 1,
    title: "Matematikos namų darbai - Algebros uždaviniai",
    description: "Spręsti uždavinius 15-20 iš vadovėlio. Ypatingas dėmesys skirtinas kvadratinėms lygtims.",
    due_date: "2025-10-01T10:00:00Z",
    subject: "Matematika",
    site: "manodienynas",
    synced_to_google_tasks: true,
    completed: false,
  },
  {
    id: 2,
    title: "Lietuvių kalbos rašinys",
    description: "Parašyti rašinį tema 'Pavasaris mano gyvenime'. Apimtis: 300-400 žodžių.",
    due_date: "2025-10-02T14:00:00Z",
    subject: "Lietuvių kalba",
    site: "eduka",
    synced_to_google_tasks: false,
    completed: false,
  },
  {
    id: 3,
    title: "Fizikos laboratorinis darbas",
    description: "Atlikti laboratorinius darbus Nr. 5 ir 6. Parengti ataskaitas.",
    due_date: "2025-10-03T12:00:00Z",
    subject: "Fizika",
    site: "manodienynas",
    synced_to_google_tasks: true,
    completed: false,
  },
];

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'No due date';
  return new Date(dateString).toLocaleDateString('lt-LT', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const getSiteColor = (site: string) => {
  return site === 'manodienynas' ? 'primary' : 'secondary';
};

export default function Home() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [homework, setHomework] = useState<HomeworkItem[]>(demoHomework);
  const [loadingHomework, setLoadingHomework] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.getUserProfile();
      setUser(response.user);
      // Fetch real homework for authenticated users
      await fetchRealHomework();
    } catch (error) {
      // User not authenticated - this is normal for first-time visitors
      setUser(null);
      setHomework(demoHomework); // Show demo data
    } finally {
      setLoading(false);
    }
  };

  const fetchRealHomework = async () => {
    try {
      setLoadingHomework(true);
      const response = await fetch(`${API_BASE_URL}/scraper/homework?status=upcoming`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        const results = data.results || data;
        if (Array.isArray(results) && results.length > 0) {
          // Show first 3 items
          setHomework(results.slice(0, 3));
        } else {
          // No homework found, show empty array (not demo)
          setHomework([]);
        }
      } else {
        // API error, show empty array
        setHomework([]);
      }
    } catch (error) {
      console.error('Error fetching homework:', error);
      setHomework([]);
    } finally {
      setLoadingHomework(false);
    }
  };

  return (
    <section className="flex flex-col items-center justify-center gap-8 py-8 md:py-10">
      {/* Hero Section */}
      <div className="inline-block max-w-4xl text-center justify-center">
        <span className={title()}>Automate Your&nbsp;</span>
        <span className={title({ color: "violet" })}>Homework&nbsp;</span>
        <br />
        <span className={title()}>Management</span>
        <div className={subtitle({ class: "mt-4" })}>
          Automatically scrape homework from Lithuanian educational websites 
          (Manodienynas.lt & Eduka.lt) and sync them to your Google Tasks.
        </div>
      </div>

      {/* CTA Buttons - Only show for non-authenticated users */}
      {!loading && !user && (
        <div className="flex gap-3">
          <GoogleSignInButton />
        </div>
      )}

      {/* Authenticated user actions */}
      {!loading && user && (
        <div className="flex gap-3">
          <Button
            as={Link}
            href="/dashboard"
            radius="full"
            size="lg"
            color="primary"
            variant="shadow"
          >
            View Homework
          </Button>
          <Button
            as={Link}
            href="/exams"
            radius="full"
            size="lg"
            variant="bordered"
          >
            View Exams
          </Button>
        </div>
      )}

      {/* Preview Section - Shows real homework for logged in users, demo for guests */}
      <div className="w-full max-w-4xl mt-12">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold mb-2">
            {user ? 'Your Upcoming Homework' : 'See It In Action'}
          </h2>
          <p className="text-default-500">
            {user 
              ? 'Your latest homework assignments from Manodienynas and Eduka'
              : 'Preview how your homework will be automatically organized and synced'
            }
          </p>
        </div>
        
        {loadingHomework ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : user && homework.length === 0 ? (
          <Card className="py-8">
            <CardBody className="text-center">
              <div className="flex flex-col items-center gap-4">
                <div className="text-6xl">📚</div>
                <h3 className="text-xl font-semibold">No Homework Yet</h3>
                <p className="text-default-500 max-w-md">
                  You don't have any homework assignments yet. Click "Scrape Now" on your dashboard to fetch homework from Manodienynas and Eduka.
                </p>
                <Button
                  as={Link}
                  href="/dashboard"
                  color="primary"
                  variant="shadow"
                  size="lg"
                >
                  Go to Dashboard
                </Button>
              </div>
            </CardBody>
          </Card>
        ) : !user && homework.length === 0 ? (
          <div className="space-y-4">
            {demoHomework.map((item) => (
              <Card key={item.id} className={`hover:bg-default-50 transition-colors ${item.completed ? 'opacity-60' : ''}`}>
                <CardBody>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className={`font-semibold text-lg ${item.completed ? 'line-through' : ''}`}>
                          {item.title}
                        </h3>
                        <Chip
                          size="sm"
                          color={getSiteColor(item.site)}
                          variant="flat"
                        >
                          {item.site}
                        </Chip>
                        {item.completed ? (
                          <Chip size="sm" color="success" variant="flat">
                            ✓ Completed
                          </Chip>
                        ) : item.synced_to_google_tasks ? (
                          <Chip size="sm" color="success" variant="flat">
                            ✓ Synced
                          </Chip>
                        ) : (
                          <Chip size="sm" color="warning" variant="flat">
                            Not Synced
                          </Chip>
                        )}
                      </div>
                      
                      <p className="text-default-600 mb-3 line-clamp-2">
                        {item.description}
                      </p>
                      
                      <div className="flex items-center gap-6 text-sm text-default-500">
                        <span>📚 {item.subject}</span>
                        <span>📅 {formatDate(item.due_date)}</span>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 ml-4">
                      {!item.synced_to_google_tasks && (
                        <Button
                          size="sm"
                          color="success"
                          variant="flat"
                          disabled
                        >
                          Sync
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="light"
                        disabled
                      >
                        View Source
                      </Button>
                    </div>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {homework.map((item) => (
              <Card key={item.id} className={`hover:bg-default-50 transition-colors ${item.completed ? 'opacity-60' : ''}`}>
                <CardBody>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className={`font-semibold text-lg ${item.completed ? 'line-through' : ''}`}>
                          {item.title}
                        </h3>
                        <Chip
                          size="sm"
                          color={getSiteColor(item.site)}
                          variant="flat"
                        >
                          {item.site}
                        </Chip>
                        {item.completed ? (
                          <Chip size="sm" color="success" variant="flat">
                            ✓ Completed
                          </Chip>
                        ) : item.synced_to_google_tasks ? (
                          <Chip size="sm" color="success" variant="flat">
                            ✓ Synced
                          </Chip>
                        ) : (
                          <Chip size="sm" color="warning" variant="flat">
                            Not Synced
                          </Chip>
                        )}
                      </div>
                      
                      <p className="text-default-600 mb-3 line-clamp-2">
                        {item.description}
                      </p>
                      
                      <div className="flex items-center gap-6 text-sm text-default-500">
                        <span>📚 {item.subject}</span>
                        <span>📅 {formatDate(item.due_date)}</span>
                      </div>
                    </div>
                    
                    {!user && (
                      <div className="flex gap-2 ml-4">
                        {!item.synced_to_google_tasks && (
                          <Button
                            size="sm"
                            color="success"
                            variant="flat"
                            disabled
                          >
                            Sync
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="light"
                          disabled
                        >
                          View Source
                        </Button>
                      </div>
                    )}
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}
        
        <div className="text-center mt-6">
          {user && homework.length === 0 ? (
            null  // Already showing message in the card above
          ) : user ? (
            <Button
              as={Link}
              href="/dashboard"
              color="primary"
              variant="flat"
              size="lg"
            >
              View All Homework
            </Button>
          ) : (
            <>
              <p className="text-sm text-default-500 mb-4">
                This is demo data. Sign in to see your actual homework assignments!
              </p>
              <GoogleSignInButton />
            </>
          )}
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-5xl">
        <Card className="py-4">
          <CardBody className="text-center">
            <div className="flex justify-center mb-4">
              <ScrapingIcon size={48} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Automated Scraping</h3>
            <p className="text-default-500">
              Automatically scrape homework from Manodienynas.lt and Eduka.lt 
              at configurable intervals.
            </p>
          </CardBody>
        </Card>

        <Card className="py-4">
          <CardBody className="text-center">
            <div className="flex justify-center mb-4">
              <GoogleIcon size={48} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Google Tasks Sync</h3>
            <p className="text-default-500">
              Seamlessly sync scraped homework to your Google Tasks "Homework" 
              list for easy access across all devices.
            </p>
          </CardBody>
        </Card>

        <Card className="py-4">
          <CardBody className="text-center">
            <div className="flex justify-center mb-4">
              <TaskIcon size={48} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Smart Organization</h3>
            <p className="text-default-500">
              Organize homework by subject, due date, and source with 
              intelligent duplicate detection.
            </p>
          </CardBody>
        </Card>
      </div>

      {/* Status Indicators */}
      <div className="flex gap-2 mt-8">
        <Chip color="success" variant="flat">
          <span className="flex items-center gap-1">
            ✓ Manodienynas.lt Support
          </span>
        </Chip>
        <Chip color="success" variant="flat">
          <span className="flex items-center gap-1">
            ✓ Eduka.lt Support
          </span>
        </Chip>
        <Chip color="primary" variant="flat">
          <span className="flex items-center gap-1">
            ⚡ Real-time Sync
          </span>
        </Chip>
      </div>
    </section>
  );
}
