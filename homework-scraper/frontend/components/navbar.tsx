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
import { addToast } from "@heroui/toast";
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
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.getUserProfile();
      setUser(response.user);
    } catch (error) {
      // User not authenticated - this is normal and expected
      // Don't log errors to avoid cluttering the console
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      setUser(null);
      setIsMenuOpen(false); // Close mobile menu
      addToast({
        title: 'Signed Out',
        description: 'You have been successfully signed out',
        color: 'success',
      });
      // Redirect to home page
      window.location.href = '/';
    } catch (error) {
      console.error('Logout failed:', error);
      // Silently handle logout errors - user will be redirected anyway
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      const data = await authAPI.getGoogleAuthUrl();
      window.location.href = data.authorization_url;
    } catch (error) {
      // Silently handle - toast will show the error
      addToast({
        title: 'Connection Error',
        description: 'Cannot connect to backend server. Please ensure the backend is running.',
        color: 'danger',
      });
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
    <HeroUINavbar 
      maxWidth="xl" 
      position="sticky"
      isMenuOpen={isMenuOpen}
      onMenuOpenChange={setIsMenuOpen}
    >
      <NavbarContent className="basis-1/5 sm:basis-full" justify="start">
        <NavbarBrand as="li" className="gap-2 sm:gap-3 max-w-fit">
          <NextLink className="flex justify-start items-center gap-1 sm:gap-2" href="/">
            <ScrapingIcon size={24} className="sm:w-7 sm:h-7" />
            <p className="font-bold text-primary text-sm sm:text-base">Homework Scraper</p>
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
                  Homework
                </DropdownItem>
                <DropdownItem key="settings" as={NextLink} href="/settings">
                  Settings
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
              className="text-sm font-normal text-black dark:text-white bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600"
              startContent={<GoogleIcon size={16} />}
              variant="bordered"
              onPress={handleGoogleSignIn}
            >
              Sign In
            </Button>
          </NavbarItem>
        )}
      </NavbarContent>

      <NavbarContent className="sm:hidden basis-1 pl-4" justify="end">
        <NavbarMenuToggle />
      </NavbarContent>

      <NavbarMenu>
        <div className="mx-4 mt-2 flex flex-col gap-3">
          {user && (
            <NavbarMenuItem className="border-b border-default-200 pb-3">
              <div className="flex items-center gap-3 py-2">
                <Avatar
                  color="primary"
                  name={getAvatarText()}
                  size="sm"
                />
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm truncate">{getUserDisplayName()}</p>
                  <p className="text-xs text-default-500 truncate">{user.email}</p>
                </div>
              </div>
            </NavbarMenuItem>
          )}
          
          {siteConfig.navMenuItems.map((item, index) => (
            <NavbarMenuItem key={`${item}-${index}`}>
              <NextLink
                className={clsx(
                  "w-full block py-2 px-2 rounded-lg hover:bg-default-100",
                  index === siteConfig.navMenuItems.length - 1
                    ? "text-danger"
                    : "text-foreground"
                )}
                href={item.href}
                onClick={() => setIsMenuOpen(false)}
              >
                {item.label}
              </NextLink>
            </NavbarMenuItem>
          ))}
          
          {user ? (
            <>
              <NavbarMenuItem>
                <NextLink 
                  className="w-full block py-2 px-2 rounded-lg hover:bg-default-100 text-foreground" 
                  href="/dashboard"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Homework
                </NextLink>
              </NavbarMenuItem>
              <NavbarMenuItem>
                <NextLink 
                  className="w-full block py-2 px-2 rounded-lg hover:bg-default-100 text-foreground" 
                  href="/settings"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Settings
                </NextLink>
              </NavbarMenuItem>
              <NavbarMenuItem className="border-t border-default-200 pt-3">
                <button 
                  className="w-full text-left py-2 px-2 rounded-lg hover:bg-danger-50 text-danger font-semibold" 
                  onClick={handleLogout}
                >
                  Log Out
                </button>
              </NavbarMenuItem>
            </>
          ) : (
            <NavbarMenuItem className="border-t border-default-200 pt-3">
              <button 
                className="w-full text-left py-2 px-2 rounded-lg hover:bg-primary-50 text-primary font-semibold flex items-center gap-2"
                onClick={handleGoogleSignIn}
              >
                <GoogleIcon size={16} />
                Sign In with Google
              </button>
            </NavbarMenuItem>
          )}
        </div>
      </NavbarMenu>
    </HeroUINavbar>
  );
};
