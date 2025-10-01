// API configuration
// Use relative path to leverage Next.js API proxy
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// Types
export interface HomeworkItem {
  id: number;
  title: string;
  description: string;
  due_date: string | null;
  subject: string;
  site: string;
  url: string;
  synced_to_google_tasks: boolean;
  scraped_at: string;
  google_task_id: string;
}

export interface UserPreferences {
  enable_manodienynas: boolean;
  enable_eduka: boolean;
  auto_sync_to_google_tasks: boolean;
  scraping_frequency_hours: number;
  last_scraped_manodienynas: string | null;
  last_scraped_eduka: string | null;
}

export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  has_google_oauth: boolean;
}

export interface SyncResult {
  synced_count: number;
  errors: string[];
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

// Generic API function
async function apiCall<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    },
    credentials: 'include', // Include cookies for session auth
    ...options,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// Authentication API
export const authAPI = {
  async getGoogleAuthUrl(): Promise<{ authorization_url: string }> {
    return apiCall('/auth/google/login/');
  },

  async handleGoogleCallback(code: string, state: string): Promise<{ user: UserProfile }> {
    return apiCall(`/auth/google/callback/?code=${code}&state=${state}`);
  },

  async logout(): Promise<{ message: string }> {
    return apiCall('/auth/logout/', { method: 'POST' });
  },

  async getUserProfile(): Promise<{ user: UserProfile }> {
    return apiCall('/auth/user/');
  },

  // Credential management
  async storeCredentials(data: {
    site: string;
    username: string;
    password: string;
    additional_data?: any;
  }): Promise<{ message: string; site: string; username: string; is_verified: boolean }> {
    return apiCall('/auth/credentials/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getCredentials(): Promise<{ credentials: Record<string, any> }> {
    return apiCall('/auth/credentials/');
  },

  async verifyCredentials(data: {
    site: string;
    url?: string;
  }): Promise<{ success: boolean; message: string; site: string; verified: boolean }> {
    return apiCall('/auth/verify-credentials/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async deleteCredentials(site: string): Promise<{ message: string; site: string }> {
    return apiCall('/auth/credentials/', {
      method: 'DELETE',
      body: JSON.stringify({ site }),
    });
  },

  // Site selection
  async getAvailableSites(): Promise<{ available_sites: Array<{ id: string; name: string; description: string }> }> {
    return apiCall('/auth/sites/');
  },

  async saveSiteSelections(selectedSites: string[]): Promise<{ message: string; selected_sites: string[] }> {
    return apiCall('/auth/sites/', {
      method: 'POST',
      body: JSON.stringify({ selected_sites: selectedSites }),
    });
  },
};

// Homework/Scraper API
export const scraperAPI = {
  async getHomework(params: {
    page?: number;
    site?: string;
    synced?: boolean;
    search?: string;
  } = {}): Promise<PaginatedResponse<HomeworkItem>> {
    const searchParams = new URLSearchParams();
    
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.site && params.site !== 'all') searchParams.append('site', params.site);
    if (params.synced !== undefined) searchParams.append('synced', params.synced.toString());
    if (params.search) searchParams.append('search', params.search);

    const query = searchParams.toString();
    return apiCall(`/scraper/homework/${query ? `?${query}` : ''}`);
  },

  async scrapeHomework(): Promise<{ 
    message: string; 
    scraped_count: number;
    synced_count?: number;
    sync_errors?: string[];
  }> {
    return apiCall('/scraper/homework/scrape/', { method: 'POST' });
  },

  async getPreferences(): Promise<UserPreferences> {
    return apiCall('/scraper/preferences/');
  },

  async updatePreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    return apiCall('/scraper/preferences/', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  },
};

// Google Tasks API
export const tasksAPI = {
  async syncHomeworkToTasks(homeworkIds?: number[]): Promise<SyncResult> {
    return apiCall('/tasks/sync/', {
      method: 'POST',
      body: JSON.stringify({ homework_ids: homeworkIds }),
    });
  },

  async getTaskLists(): Promise<{ task_lists: any[] }> {
    return apiCall('/tasks/lists/');
  },

  async getTasks(listId: string): Promise<{ tasks: any[] }> {
    return apiCall(`/tasks/lists/${listId}/tasks/`);
  },
};

// Dashboard API
export const dashboardAPI = {
  async getStats(): Promise<{
    total_homework: number;
    synced_homework: number;
    sites_enabled: string[];
    last_scrape: string | null;
  }> {
    // This could be a specific dashboard endpoint or derived from other APIs
    const homework = await scraperAPI.getHomework({ page: 1 });
    const preferences = await scraperAPI.getPreferences();
    
    return {
      total_homework: homework.count,
      synced_homework: homework.results.filter(hw => hw.synced_to_google_tasks).length,
      sites_enabled: [
        ...(preferences.enable_manodienynas ? ['manodienynas'] : []),
        ...(preferences.enable_eduka ? ['eduka'] : []),
      ],
      last_scrape: preferences.last_scraped_manodienynas || preferences.last_scraped_eduka,
    };
  },

  async getRecentHomework(limit = 5): Promise<HomeworkItem[]> {
    const response = await scraperAPI.getHomework({ page: 1 });
    return response.results.slice(0, limit);
  },
};

// Error handling wrapper for React components
export function withErrorHandling<T extends any[], R>(
  apiFunction: (...args: T) => Promise<R>
) {
  return async (...args: T): Promise<R | null> => {
    try {
      return await apiFunction(...args);
    } catch (error) {
      console.error('API Error:', error);
      
      // You can add toast notifications here
      // toast.error(error.message);
      
      return null;
    }
  };
}

// Hooks for React Query (if you want to use it)
export const queryKeys = {
  homework: (params?: any) => ['homework', params],
  preferences: () => ['preferences'],
  userProfile: () => ['userProfile'],
  dashboardStats: () => ['dashboardStats'],
  taskLists: () => ['taskLists'],
  tasks: (listId: string) => ['tasks', listId],
} as const;