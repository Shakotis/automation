import { Link } from "@heroui/link";
import { Button } from "@heroui/button";
import { Card, CardBody } from "@heroui/card";
import { Chip } from "@heroui/chip";

import { title, subtitle } from "@/components/primitives";
import { GoogleIcon, TaskIcon, ScrapingIcon } from "@/components/icons";

export default function Home() {
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

      {/* CTA Buttons */}
      <div className="flex gap-3">
        <Button
          as={Link}
          color="primary"
          href="/auth/google"
          radius="full"
          size="lg"
          variant="shadow"
          startContent={<GoogleIcon size={20} />}
        >
          Sign in with Google
        </Button>
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
