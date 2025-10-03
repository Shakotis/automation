"use client";

import { Card, CardBody, CardHeader } from "@heroui/card";
import { Button } from "@heroui/button";
import { Chip } from "@heroui/chip";
import { Divider } from "@heroui/divider";
import { Link } from "@heroui/link";
import { title, subtitle } from "@/components/primitives";
import { GoogleIcon, TaskIcon, ScrapingIcon } from "@/components/icons";
import NextLink from "next/link";

export default function HowToUsePage() {
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className={title()}>How to Use</h1>
        <p className={subtitle({ class: "mt-4" })}>
          Simple steps to automate your homework management
        </p>
      </div>

      {/* Step 1: Sign In */}
      <Card className="mb-8">
        <CardHeader className="flex gap-3">
          <div className="flex justify-center items-center w-12 h-12 rounded-full bg-primary text-white text-xl font-bold">
            1
          </div>
          <div className="flex flex-col">
            <h2 className="text-2xl font-bold">Sign In with Google</h2>
            <p className="text-default-500">Connect your Google account to get started</p>
          </div>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <p className="text-lg">
              Click <strong>"Sign In with Google"</strong> to allow the app to save homework to Google Tasks.
            </p>
            <Chip color="success" variant="flat">
              ✓ Safe & Secure - OAuth 2.0 Protected
            </Chip>
          </div>
        </CardBody>
      </Card>

      {/* Step 2: Add School Credentials */}
      <Card className="mb-8">
        <CardHeader className="flex gap-3">
          <div className="flex justify-center items-center w-12 h-12 rounded-full bg-primary text-white text-xl font-bold">
            2
          </div>
          <div className="flex flex-col">
            <h2 className="text-2xl font-bold">Add School Website Login</h2>
            <p className="text-default-500">Enter your Manodienynas or Eduka credentials</p>
          </div>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <p className="text-lg">
              Go to <strong>Settings</strong> and add your login details for:
            </p>
            <div className="grid md:grid-cols-2 gap-4">
              <Card className="bg-primary-50">
                <CardBody>
                  <h3 className="font-semibold mb-2">📚 Manodienynas.lt</h3>
                  <p className="text-sm text-default-600">
                    Enter your username and password used to log into Manodienynas
                  </p>
                </CardBody>
              </Card>
              <Card className="bg-secondary-50">
                <CardBody>
                  <h3 className="font-semibold mb-2">📖 Eduka.lt</h3>
                  <p className="text-sm text-default-600">
                    Enter your username and password used to log into Eduka
                  </p>
                </CardBody>
              </Card>
            </div>
            <Chip color="warning" variant="flat">
              🔒 Your credentials are encrypted and stored securely
            </Chip>
          </div>
        </CardBody>
      </Card>

      {/* Step 3: Automatic Scraping */}
      <Card className="mb-8">
        <CardHeader className="flex gap-3">
          <div className="flex justify-center items-center w-12 h-12 rounded-full bg-primary text-white text-xl font-bold">
            3
          </div>
          <div className="flex flex-col">
            <h2 className="text-2xl font-bold">Sit Back & Relax</h2>
            <p className="text-default-500">Homework is automatically collected for you</p>
          </div>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <p className="text-lg">
              That's it! The app automatically scrapes your homework <strong>6 times per day</strong> at: 
              9 AM, 11 AM, 1 PM, 2 PM, 3 PM, and 4 PM.
            </p>
            <p className="text-default-600">
              All homework is automatically synced to your Google Tasks - no manual work needed!
            </p>
          </div>
        </CardBody>
      </Card>

      {/* Step 4: Check Google Tasks */}
      <Card className="mb-8">
        <CardHeader className="flex gap-3">
          <div className="flex justify-center items-center w-12 h-12 rounded-full bg-primary text-white text-xl font-bold">
            4
          </div>
          <div className="flex flex-col">
            <h2 className="text-2xl font-bold">View on Google Tasks</h2>
            <p className="text-default-500">Access your homework anywhere, anytime</p>
          </div>
        </CardHeader>
        <CardBody>
          <div className="space-y-4">
            <p className="text-lg">
              Open the <strong>Google Tasks app</strong> on your phone or computer to see all your homework!
            </p>
            
            {/* Mobile: Clickable image link */}
            <div className="md:hidden">
              <p className="text-sm text-default-600 mb-3">
                👇 Tap the image below to download Google Tasks app
              </p>
              <Link
                href="https://play.google.com/store/apps/details?id=com.google.android.apps.tasks"
                isExternal
                className="block"
              >
                <Card className="hover:scale-105 transition-transform cursor-pointer border-2 border-primary">
                  <CardBody className="text-center p-6">
                    <div className="text-6xl mb-3">📱</div>
                    <h3 className="text-xl font-bold mb-2">Download Google Tasks</h3>
                    <p className="text-sm text-default-600 mb-3">
                      Tap here to get the app
                    </p>
                    <Chip color="primary" variant="solid">
                      Download for Android
                    </Chip>
                  </CardBody>
                </Card>
              </Link>
              <Link
                href="https://apps.apple.com/us/app/google-tasks-get-things-done/id1353634006"
                isExternal
                className="block mt-4"
              >
                <Card className="hover:scale-105 transition-transform cursor-pointer border-2 border-secondary">
                  <CardBody className="text-center p-6">
                    <div className="text-6xl mb-3">📱</div>
                    <h3 className="text-xl font-bold mb-2">Download Google Tasks</h3>
                    <p className="text-sm text-default-600 mb-3">
                      Tap here to get the app
                    </p>
                    <Chip color="secondary" variant="solid">
                      Download for iOS
                    </Chip>
                  </CardBody>
                </Card>
              </Link>
            </div>

            {/* Desktop: Regular buttons */}
            <div className="hidden md:flex gap-4 justify-center">
              <Button
                as={Link}
                href="https://play.google.com/store/apps/details?id=com.google.android.apps.tasks"
                isExternal
                color="primary"
                size="lg"
                startContent={<TaskIcon size={20} />}
              >
                Download for Android
              </Button>
              <Button
                as={Link}
                href="https://apps.apple.com/us/app/google-tasks-get-things-done/id1353634006"
                isExternal
                color="secondary"
                size="lg"
                startContent={<TaskIcon size={20} />}
              >
                Download for iOS
              </Button>
              <Button
                as={Link}
                href="https://tasks.google.com"
                isExternal
                variant="bordered"
                size="lg"
                startContent={<TaskIcon size={20} />}
              >
                Open Web Version
              </Button>
            </div>

            <div className="bg-success-50 p-4 rounded-lg mt-4">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <TaskIcon size={20} />
                Find Your Homework
              </h4>
              <p className="text-sm text-default-700">
                Look for the <strong>"Homework"</strong> task list in Google Tasks. 
                All your assignments will be organized there with due dates!
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      <Divider className="my-12" />

      {/* Quick Tips */}
      <Card className="mb-8 bg-gradient-to-br from-primary-50 to-secondary-50">
        <CardHeader>
          <h2 className="text-2xl font-bold">💡 Quick Tips</h2>
        </CardHeader>
        <CardBody>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                ✅ Mark as Complete
              </h3>
              <p className="text-sm text-default-700">
                Check off tasks in Google Tasks when you finish them. The app will track your progress!
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                🔄 Manual Sync
              </h3>
              <p className="text-sm text-default-700">
                Need homework now? Click "Scrape Now" on the Dashboard to get the latest homework immediately.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                📅 Exam Dates
              </h3>
              <p className="text-sm text-default-700">
                Go to the Exams page to manually add exam dates to your Google Calendar.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                ⚙️ Settings
              </h3>
              <p className="text-sm text-default-700">
                Change your school credentials or sync preferences in the Settings page anytime.
              </p>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* CTA */}
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-4">Ready to Get Started?</h2>
        <div className="flex gap-4 justify-center flex-wrap">
          <Button
            as={NextLink}
            href="/"
            color="primary"
            size="lg"
            variant="shadow"
          >
            Go to Home
          </Button>
          <Button
            as={NextLink}
            href="/settings"
            color="secondary"
            size="lg"
            variant="bordered"
          >
            Set Up Credentials
          </Button>
          <Button
            as={NextLink}
            href="/dashboard"
            variant="bordered"
            size="lg"
          >
            View Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}
