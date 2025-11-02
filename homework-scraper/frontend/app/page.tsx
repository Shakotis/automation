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
    <section className="flex flex-col items-center justify-center gap-8 py-8 md:py-10 px-4">
      {/* Hero Section */}
      <div className="inline-block max-w-lg text-center justify-center">
        <h1 className={title()}>Automate Your&nbsp;</h1>
        <h1 className={title({ color: "violet" })}>Homework&nbsp;</h1>
        <br />
        <h1 className={title()}>Management</h1>
        <h2 className={subtitle({ class: "mt-4" })}>
          Automatically scrape homework from Lithuanian educational websites 
          (Manodienynas.lt & Eduka.lt) and sync them to your Google Tasks.
        </h2>
      </div>

      {/* CTA Buttons - Only show for non-authenticated users */}
      {!loading && !user && (
        <div className="flex flex-col items-center gap-3">
          <GoogleSignInButton />
          <p className="text-sm text-default-500 text-center max-w-md mt-2">
            By signing in, you agree to our{" "}
            <Link
              href="/terms"
              className="text-primary hover:underline"
              size="sm"
            >
              Terms of Service
            </Link>
            {" "}and{" "}
            <Link
              href="/privacy"
              className="text-primary hover:underline"
              size="sm"
            >
              Privacy Policy
            </Link>
          </p>
        </div>
      )}

      {/* Authenticated user actions */}
      {!loading && user && (
        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            as={Link}
            href="/dashboard"
            radius="full"
            size="lg"
            color="primary"
            variant="shadow"
            className="w-full sm:w-auto"
          >
            View Homework
          </Button>
          <Button
            as={Link}
            href="/exams"
            radius="full"
            size="lg"
            variant="bordered"
            className="w-full sm:w-auto"
          >
            View Exams
          </Button>
        </div>
      )}

      {/* Preview Section - Shows real homework for logged in users, demo for guests */}
      <div className="w-full max-w-4xl mt-8">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold mb-2">
            {user ? 'Your Upcoming Homework' : 'See It In Action'}
          </h2>
          <p className="text-default-500 px-4 sm:px-0">
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
              <div className="flex flex-col items-center gap-4 px-4">
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
        ) : (
          <div className="space-y-4">
            {(user ? homework : demoHomework).map((item) => (
              <Card key={item.id} className={`hover:bg-default-50 transition-colors ${item.completed ? 'opacity-60' : ''}`}>
                <CardBody>
                  <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <h3 className={`font-semibold text-lg leading-tight ${item.completed ? 'line-through' : ''}`}>
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
                      
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 text-sm text-default-500">
                        <span>📚 {item.subject}</span>
                        <span>📅 {formatDate(item.due_date)}</span>
                      </div>
                    </div>
                    
                    {!user && (
                      <div className="flex sm:flex-col gap-2 self-start sm:self-center mt-2 sm:mt-0">
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
        
        <div className="text-center mt-8">
          {user && homework.length > 0 ? (
            <Button
              as={Link}
              href="/dashboard"
              color="primary"
              variant="flat"
              size="lg"
            >
              View All Homework
            </Button>
          ) : !user ? (
            <div className="flex flex-col items-center gap-4 mt-6">
              <p className="text-sm text-default-500">
                This is demo data. Sign in to see your actual homework!
              </p>
              <GoogleSignInButton />
            </div>
          ) : null}
        </div>
      </div>

      {/* Features */}
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <Card className="py-4">
          <CardBody className="text-center">
            <div className="flex justify-center mb-4">
              <ScrapingIcon size={48} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Automated Scraping</h3>
            <p className="text-default-500 px-4">
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
            <p className="text-default-500 px-4">
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
            <p className="text-default-500 px-4">
              Organize homework by subject, due date, and source with 
              intelligent duplicate detection.
            </p>
          </CardBody>
        </Card>
      </div>

      {/* Status Indicators */}
      <div className="flex flex-wrap justify-center gap-2 mt-8">
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

      {/* Privacy & Data Usage Section */}
      <Card className="w-full max-w-4xl mt-8 bg-primary-50 dark:bg-primary-950/20 border-2 border-primary-200 dark:border-primary-800">
        <CardBody className="py-6 px-6">
          <div className="flex flex-col md:flex-row items-start gap-4">
            <div className="text-4xl">🔒</div>
            <div className="flex-1">
              <h3 className="text-lg font-bold mb-2 text-primary-900 dark:text-primary-100">
                Your Privacy & Data Security
              </h3>
              <div className="text-sm text-primary-800 dark:text-primary-200 space-y-2">
                <p>
                  <strong>How we use your Google data:</strong> We only use your Google account for 
                  authentication and to sync homework to your Google Tasks (with your permission).
                </p>
                <p>
                  <strong>Educational platform credentials:</strong> Your Manodienynas and Eduka 
                  credentials are encrypted and stored securely. We only use them to fetch your 
                  homework assignments.
                </p>
                <p>
                  <strong>Data retention:</strong> You can delete your account and all associated 
                  data at any time from the Settings page.
                </p>
                <div className="flex flex-wrap gap-3 mt-3">
                  <Link
                    href="/privacy"
                    className="text-primary hover:underline font-semibold"
                    size="sm"
                  >
                    📄 Read Full Privacy Policy →
                  </Link>
                  <Link
                    href="/terms"
                    className="text-primary hover:underline font-semibold"
                    size="sm"
                  >
                    📋 Terms of Service →
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </CardBody>
      </Card>
    </section>
  );
}
