import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UserProfile {
  user_id: string;
  email?: string;
  full_name?: string;
  picture?: string;
  mobile_number: string;
  language: string;
  crop: string;
  location: string;
  sowing_date: string;
  state: string;
  district: string;
  land_size: number;
  category: string;
  is_onboarded: boolean;
}

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
}

interface AppState {
  profile: UserProfile;
  auth: AuthState;
  setProfile: (profile: Partial<UserProfile>) => void;
  setAuth: (auth: Partial<AuthState>) => void;
  resetProfile: () => void;
  logout: () => void;
}

const initialProfile: UserProfile = {
  user_id: '',
  mobile_number: '',
  language: 'hi',
  crop: '',
  location: '',
  sowing_date: '',
  state: '',
  district: '',
  land_size: 0,
  category: 'General',
  is_onboarded: false,
};

const initialAuth: AuthState = {
  token: null,
  isAuthenticated: false,
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      profile: initialProfile,
      auth: initialAuth,
      setProfile: (newProfile) =>
        set((state) => ({
          profile: { ...state.profile, ...newProfile },
        })),
      setAuth: (newAuth) =>
        set((state) => ({
          auth: { ...state.auth, ...newAuth },
        })),
      resetProfile: () => set({ profile: initialProfile }),
      logout: () => set({ profile: initialProfile, auth: initialAuth }),
    }),
    {
      name: 'khetipulse-storage',
    }
  )
);
