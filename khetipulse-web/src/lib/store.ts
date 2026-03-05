import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UserProfile {
  user_id: string;
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

interface AppState {
  profile: UserProfile;
  setProfile: (profile: Partial<UserProfile>) => void;
  resetProfile: () => void;
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

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      profile: initialProfile,
      setProfile: (newProfile) =>
        set((state) => ({
          profile: { ...state.profile, ...newProfile },
        })),
      resetProfile: () => set({ profile: initialProfile }),
    }),
    {
      name: 'khetipulse-storage',
    }
  )
);
