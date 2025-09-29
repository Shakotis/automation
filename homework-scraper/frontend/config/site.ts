export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "Homework Scraper",
  description: "Automatically scrape homework from Lithuanian educational websites and sync to Google Tasks.",
  navItems: [
    {
      label: "Dashboard",
      href: "/dashboard",
    },
    {
      label: "Homework",
      href: "/homework",
    },
    {
      label: "Settings",
      href: "/settings",
    },
  ],
  navMenuItems: [
    {
      label: "Dashboard",
      href: "/dashboard",
    },
    {
      label: "Homework",
      href: "/homework",
    },
    {
      label: "Settings",
      href: "/settings",
    },
    {
      label: "Profile",
      href: "/profile",
    },
    {
      label: "Logout",
      href: "/logout",
    },
  ],
  links: {
    github: "https://github.com/yourusername/homework-scraper",
    docs: "/docs",
  },
};
