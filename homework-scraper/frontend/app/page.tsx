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

interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  has_google_oauth: boolean;
}

// Demo homework data
const demoHomework = [
  {
    id: 1,
    title: "Matematikos namų darbai - Algebros uždaviniai",
    description: "Spręsti uždavinius 15-20 iš vadovėlio. Ypatingas dėmesys skirtinas kvadratinėms lygtims.",
    due_date: "2025-10-01T10:00:00Z",
    subject: "Matematika",
    site: "manodienynas",
    synced_to_google_tasks: true,
  },
  {
    id: 2,
    title: "Lietuvių kalbos rašinys",
    description: "Parašyti rašinį tema 'Pavasaris mano gyvenime'. Apimtis: 300-400 žodžių.",
    due_date: "2025-10-02T14:00:00Z",
    subject: "Lietuvių kalba",
    site: "eduka",
    synced_to_google_tasks: false,
  },
  {
    id: 3,
    title: "Fizikos laboratorinis darbas",
    description: "Atlikti laboratorinius darbus Nr. 5 ir 6. Parengti ataskaitas.",
    due_date: "2025-10-03T12:00:00Z",
    subject: "Fizika",
    site: "manodienynas",
    synced_to_google_tasks: true,
  },
];

const formatDate = (dateString: string) => {
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

export default function Home() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.getUserProfile();
      setUser(response.user);
    } catch (error) {
      // User not authenticated
      setUser(null);
    } finally {
      setLoading(false);
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
          <Button
            as={Link}
            href="/dashboard"
            radius="full"
            size="lg"
            variant="bordered"
          >
            View Demo
          </Button>
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
            Go to Dashboard
          </Button>
          <Button
            as={Link}
            href="/homework"
            radius="full"
            size="lg"
            variant="bordered"
          >
            View Homework
          </Button>
        </div>
      )}

      {/* Demo Preview Section */}
      <div className="w-full max-w-4xl mt-12">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold mb-2">See It In Action</h2>
          <p className="text-default-500">
            Preview how your homework will be automatically organized and synced
          </p>
        </div>
        
        <div className="space-y-4">
          {demoHomework.map((item) => (
            <Card key={item.id} className="hover:bg-default-50 transition-colors">
              <CardBody>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg">{item.title}</h3>
                      <Chip
                        size="sm"
                        color={getSiteColor(item.site)}
                        variant="flat"
                      >
                        {item.site}
                      </Chip>
                      {item.synced_to_google_tasks ? (
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
        
        <div className="text-center mt-6">
          <p className="text-sm text-default-500 mb-4">
            This is demo data. {user ? 'Go to your dashboard to see real homework assignments!' : 'Sign in to see your actual homework assignments!'}
          </p>
          {!user && <GoogleSignInButton />}
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
