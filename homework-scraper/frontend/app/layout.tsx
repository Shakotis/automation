import "@/styles/globals.css";
import { Metadata, Viewport } from "next";
import { Link } from "@heroui/link";
import clsx from "clsx";

import { Providers } from "./providers";

import { siteConfig } from "@/config/site";
import { fontSans } from "@/config/fonts";
import { Navbar } from "@/components/navbar";
import AuthGuard from "@/components/AuthGuard";

export const metadata: Metadata = {
  title: {
    default: siteConfig.name,
    template: `%s - ${siteConfig.name}`,
  },
  description: siteConfig.description,
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "black" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html suppressHydrationWarning lang="en">
      <head />
      <body
        className={clsx(
          "min-h-screen text-foreground bg-background font-sans antialiased",
          fontSans.variable,
        )}
      >
        <Providers themeProps={{ attribute: "class", defaultTheme: "dark" }}>
          <AuthGuard>
            <div className="relative flex flex-col min-h-screen">
              <Navbar />
              <main className="container mx-auto max-w-7xl pt-4 sm:pt-16 px-4 sm:px-6 flex-grow">
                {children}
              </main>
              <footer className="w-full flex items-center justify-center py-6 border-t border-default-200">
                <div className="container max-w-7xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <p className="text-sm text-default-600">
                    © {new Date().getFullYear()} Homework Scraper. All rights reserved.
                  </p>
                  <div className="flex gap-4 text-sm">
                    <Link
                      isExternal
                      className="text-default-600 hover:text-primary"
                      href={siteConfig.links.privacy}
                    >
                      Privacy Policy
                    </Link>
                    <Link
                      isExternal
                      className="text-default-600 hover:text-primary"
                      href={siteConfig.links.terms}
                    >
                      Terms of Service
                    </Link>
                    <Link
                      isExternal
                      className="text-default-600 hover:text-primary"
                      href={siteConfig.links.github}
                    >
                      GitHub
                    </Link>
                  </div>
                </div>
              </footer>
            </div>
          </AuthGuard>
        </Providers>
      </body>
    </html>
  );
}
