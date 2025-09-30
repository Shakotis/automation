'use client';

import {
  Navbar as HeroUINavbar,
  NavbarContent,
  NavbarMenu,
  NavbarMenuToggle,
  NavbarBrand,
  NavbarItem,
  NavbarMenuItem,
} from "@heroui/navbar";
import { Button } from "@heroui/button";
import { Link } from "@heroui/link";
import { Avatar } from "@heroui/avatar";
import { Dropdown, DropdownTrigger, DropdownMenu, DropdownItem } from "@heroui/dropdown";
import { link as linkStyles } from "@heroui/theme";
import NextLink from "next/link";
import clsx from "clsx";
import { useState, useEffect } from "react";

import { siteConfig } from "@/config/site";
import { ThemeSwitch } from "@/components/theme-switch";
import { authAPI } from "@/lib/api";
import {
  GithubIcon,
  ScrapingIcon,
  GoogleIcon,
} from "@/components/icons";

interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  has_google_oauth: boolean;
}

export const Navbar = () => {
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

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
      // Redirect to home page
      window.location.href = '/';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const getAvatarText = () => {
    if (!user) return '';
    const firstInitial = user.first_name ? user.first_name[0] : '';
    const lastInitial = user.last_name ? user.last_name[0] : '';
    return (firstInitial + lastInitial).toUpperCase() || user.email[0].toUpperCase();
  };

  const getUserDisplayName = () => {
    if (!user) return '';
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    return user.email;
  };
  return (
    <HeroUINavbar maxWidth="xl" position="sticky">
      <NavbarContent className="basis-1/5 sm:basis-full" justify="start">
        <NavbarBrand as="li" className="gap-3 max-w-fit">
          <NextLink className="flex justify-start items-center gap-2" href="/">
            <ScrapingIcon size={28} />
            <p className="font-bold text-primary">Homework Scraper</p>
          </NextLink>
        </NavbarBrand>
        <ul className="hidden lg:flex gap-4 justify-start ml-2">
          {siteConfig.navItems.map((item) => (
            <NavbarItem key={item.href}>
              <NextLink
                className={clsx(
                  linkStyles({ color: "foreground" }),
                  "data-[active=true]:text-primary data-[active=true]:font-medium",
                )}
                color="foreground"
                href={item.href}
              >
                {item.label}
              </NextLink>
            </NavbarItem>
          ))}
        </ul>
      </NavbarContent>

      <NavbarContent
        className="hidden sm:flex basis-1/5 sm:basis-full"
        justify="end"
      >
        <NavbarItem className="hidden sm:flex gap-2">
          <Link isExternal aria-label="Github" href={siteConfig.links.github}>
            <GithubIcon className="text-default-500" />
          </Link>
          <ThemeSwitch />
        </NavbarItem>
        
        {loading ? (
          <NavbarItem className="hidden md:flex">
            <div className="w-8 h-8 rounded-full bg-default-200 animate-pulse" />
          </NavbarItem>
        ) : user ? (
          <NavbarItem className="hidden md:flex">
            <Dropdown placement="bottom-end">
              <DropdownTrigger>
                <Avatar
                  as="button"
                  className="transition-transform"
                  color="primary"
                  name={getAvatarText()}
                  size="sm"
                />
              </DropdownTrigger>
              <DropdownMenu aria-label="Profile Actions" variant="flat" onAction={(key) => {
                if (key === "logout") {
                  handleLogout();
                }
              }}>
                <DropdownItem key="profile" className="h-14 gap-2">
                  <p className="font-semibold">Signed in as</p>
                  <p className="font-semibold">{getUserDisplayName()}</p>
                </DropdownItem>
                <DropdownItem key="dashboard" as={NextLink} href="/dashboard">
                  Dashboard
                </DropdownItem>
                <DropdownItem key="settings" as={NextLink} href="/settings">
                  Settings
                </DropdownItem>
                <DropdownItem key="homework" as={NextLink} href="/homework">
                  Homework
                </DropdownItem>
                <DropdownItem 
                  key="logout" 
                  color="danger"
                >
                  Log Out
                </DropdownItem>
              </DropdownMenu>
            </Dropdown>
          </NavbarItem>
        ) : (
          <NavbarItem className="hidden md:flex">
            <Button
              as={NextLink}
              className="text-sm font-normal text-white bg-primary"
              href="/auth/google"
              startContent={<GoogleIcon size={16} />}
              variant="solid"
            >
              Sign In
            </Button>
          </NavbarItem>
        )}
      </NavbarContent>

      <NavbarContent className="sm:hidden basis-1 pl-4" justify="end">
        <ThemeSwitch />
        <NavbarMenuToggle />
      </NavbarContent>

      <NavbarMenu>
        <div className="mx-4 mt-2 flex flex-col gap-2">
          {user && (
            <NavbarMenuItem>
              <div className="flex items-center gap-3 py-2">
                <Avatar
                  color="primary"
                  name={getAvatarText()}
                  size="sm"
                />
                <div>
                  <p className="font-semibold text-sm">{getUserDisplayName()}</p>
                  <p className="text-xs text-default-500">{user.email}</p>
                </div>
              </div>
            </NavbarMenuItem>
          )}
          
          {siteConfig.navMenuItems.map((item, index) => (
            <NavbarMenuItem key={`${item}-${index}`}>
              <NextLink
                className={clsx(
                  "w-full",
                  index === siteConfig.navMenuItems.length - 1
                    ? "text-danger"
                    : "text-foreground"
                )}
                href={item.href}
              >
                {item.label}
              </NextLink>
            </NavbarMenuItem>
          ))}
          
          {user ? (
            <>
              <NavbarMenuItem>
                <NextLink className="w-full text-foreground" href="/dashboard">
                  Dashboard
                </NextLink>
              </NavbarMenuItem>
              <NavbarMenuItem>
                <NextLink className="w-full text-foreground" href="/settings">
                  Settings
                </NextLink>
              </NavbarMenuItem>
              <NavbarMenuItem>
                <NextLink className="w-full text-foreground" href="/homework">
                  Homework
                </NextLink>
              </NavbarMenuItem>
              <NavbarMenuItem>
                <button 
                  className="w-full text-left text-danger" 
                  onClick={handleLogout}
                >
                  Log Out
                </button>
              </NavbarMenuItem>
            </>
          ) : (
            <NavbarMenuItem>
              <NextLink className="w-full text-foreground" href="/auth/google">
                Sign In with Google
              </NextLink>
            </NavbarMenuItem>
          )}
        </div>
      </NavbarMenu>
    </HeroUINavbar>
  );
};
