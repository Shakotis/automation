export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "Homework Scraper",
  description: "Automatically scrape homework from Lithuanian educational websites and sync to Google Tasks.",
  navItems: [
    {
      label: "Homework",
      href: "/dashboard",
    },
    {
      label: "Exams",
      href: "/exams",
    },
    {
      label: "Logs",
      href: "/logs",
    },
    {
      label: "Settings",
      href: "/settings",
    },
    {
      label: "How to Use",
      href: "/how-to-use",
    },
  ],
  navMenuItems: [
    {
      label: "Homework",
      href: "/dashboard",
    },
    {
      label: "Exams",
      href: "/exams",
    },
    {
      label: "Logs",
      href: "/logs",
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
    {
      label: "How to Use",
      href: "/how-to-use",
    },
  ],
  links: {
    github: "https://github.com/yourusername/homework-scraper",
    docs: "/docs",
  },
};
