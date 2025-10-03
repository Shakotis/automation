'use client';

import { useEffect } from 'react';

interface AuthGuardProps {
  children: React.ReactNode;
}

/**
 * AuthGuard component - Currently allows all navigation.
 * Pages handle their own authentication checks and display appropriate content.
 */
export default function AuthGuard({ children }: AuthGuardProps) {
  // No authentication blocking - let users navigate freely
  // Each page will handle its own auth state and show appropriate content
  return <>{children}</>;
}
