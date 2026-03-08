"use client";
import React, { useState } from 'react';
import { useAppStore } from '@/lib/store';
import { useTranslation } from '@/lib/i18n';
import { authService } from '@/services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, Sparkles, ShieldCheck, Globe, User, Lock, Phone, UserPlus, LogIn } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const { setAuth, setProfile, auth, _hasHydrated } = useAppStore();
  const { t } = useTranslation();
  const router = useRouter();

  React.useEffect(() => {
    if (_hasHydrated && auth.isAuthenticated) {
      router.replace('/');
    }
  }, [_hasHydrated, auth.isAuthenticated, router]);

  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    full_name: '',
    mobile_number: '',
  });

  if (!_hasHydrated) {
    console.log("LoginPage waiting for hydration...");
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLocalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (isRegister) {
        await authService.register(formData);
        // After successful registration, log in
        const { access_token } = await authService.login({
          username: formData.username,
          password: formData.password
        });
        await finalizeLogin(access_token);
      } else {
        const { access_token } = await authService.login({
          username: formData.username,
          password: formData.password
        });
        await finalizeLogin(access_token);
      }
    } catch (err: any) {
      console.error(err);
      let errorMessage = 'Authentication failed. Please check your credentials.';
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          // Handle standard FastAPI/Pydantic validation error list
          errorMessage = `Validation Error: ${err.response.data.detail.map((e: any) => e.msg).join(', ')}`;
        } else if (typeof err.response.data.detail === 'object') {
          errorMessage = JSON.stringify(err.response.data.detail);
        }
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const finalizeLogin = async (token: string) => {
    // Update store with token
    setAuth({ token: token, isAuthenticated: true });

    try {
      // Fetch user profile from backend
      const user = await authService.getMe();
      const crops: string[] = Array.isArray(user.crops)
        ? user.crops
        : (user.crop ? [user.crop] : []);
      const profileData = {
        user_id: user.username,
        full_name: user.full_name,
        mobile_number: user.mobile_number || '',
        language: user.language || 'en',
        state: user.state || '',
        district: user.district || '',
        location: user.location || user.district || '',
        crop: user.crop || crops[0] || '',
        crops,
        sowing_date: user.sowing_date || '',
        is_onboarded: user.is_onboarded || false,
      };
      setProfile(profileData);
    } catch (profileErr) {
      console.error("Failed to fetch profile after login:", profileErr);
    }

    // Decide where to send user
    router.replace('/');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6 max-w-md mx-auto relative overflow-hidden">
      {/* Background Decorative Elements */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/10 rounded-full blur-3xl -mr-32 -mt-32"></div>
      <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent-500/10 rounded-full blur-3xl -ml-32 -mb-32"></div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full space-y-8 relative z-10"
      >
        {/* Logo Section */}
        <div className="text-center space-y-4">
          <div className="bg-primary-600 w-16 h-16 rounded-2xl flex items-center justify-center text-white shadow-2xl shadow-primary-200 mx-auto rotate-3">
            <LayoutDashboard size={32} />
          </div>
          <div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight leading-none">KhetiPulse</h1>
            <p className="text-[10px] font-bold text-primary-600 uppercase tracking-[0.3em] mt-2">{t('common.smartAgri')}</p>
          </div>
        </div>

        {/* Login/Register Card */}
        <div className="bg-white p-8 rounded-[2.5rem] shadow-xl shadow-slate-200 border border-slate-100 space-y-6">
          <div className="flex bg-slate-100 p-1.5 rounded-2xl mb-4">
            <button 
              onClick={() => { setIsRegister(false); setError(''); }}
              className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all ${!isRegister ? 'bg-white text-primary-600 shadow-sm' : 'text-slate-500'}`}
            >
              {t('common.login')}
            </button>
            <button 
              onClick={() => { setIsRegister(true); setError(''); }}
              className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all ${isRegister ? 'bg-white text-primary-600 shadow-sm' : 'text-slate-500'}`}
            >
              {t('common.register')}
            </button>
          </div>

          <form onSubmit={handleLocalSubmit} className="space-y-4">
            <div className="space-y-1">
              <div className="relative">
                <User size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type="text" 
                  name="username"
                  required
                  placeholder={t('common.username')}
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all text-sm font-semibold text-slate-800"
                  value={formData.username}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            {isRegister && (
              <>
                <div className="space-y-1">
                  <div className="relative">
                    <UserPlus size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input 
                      type="text" 
                      name="full_name"
                      placeholder={t('common.fullName')}
                      className="w-full pl-12 pr-4 py-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all text-sm font-semibold text-slate-800"
                      value={formData.full_name}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="relative">
                    <Phone size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input 
                      type="text" 
                      name="mobile_number"
                      placeholder={t('common.mobile')}
                      className="w-full pl-12 pr-4 py-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all text-sm font-semibold text-slate-800"
                      value={formData.mobile_number}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </>
            )}

            <div className="space-y-1">
              <div className="relative">
                <Lock size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type="password" 
                  name="password"
                  required
                  placeholder={t('common.password')}
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all text-sm font-semibold text-slate-800"
                  value={formData.password}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-4 rounded-2xl font-bold text-sm uppercase tracking-widest flex items-center justify-center gap-3 shadow-lg shadow-primary-200 active:scale-95 transition-all disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                isRegister ? <><UserPlus size={18} /> {t('common.register')}</> : <><LogIn size={18} /> {t('common.login')}</>
              )}
            </button>
          </form>

          <AnimatePresence>
            {error && (
              <motion.p 
                initial={{ opacity: 0, height: 0 }} 
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="text-xs font-bold text-rose-500 bg-rose-50 p-3 rounded-xl border border-rose-100 overflow-hidden"
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-2 gap-3 px-2">
          <div className="bg-white/50 backdrop-blur-sm p-3 rounded-2xl border border-white flex flex-col items-center text-center gap-1">
            <Sparkles className="text-amber-500 w-5 h-5" />
            <span className="text-[8px] font-bold text-slate-500 uppercase tracking-wider">AI Advisory</span>
          </div>
          <div className="bg-white/50 backdrop-blur-sm p-3 rounded-2xl border border-white flex flex-col items-center text-center gap-1">
            <Globe className="text-blue-500 w-5 h-5" />
            <span className="text-[8px] font-bold text-slate-500 uppercase tracking-wider">Multilingual</span>
          </div>
        </div>
      </motion.div>

      <p className="mt-8 text-[10px] font-bold text-slate-300 uppercase tracking-[0.2em]">
        Empowering Indian Farmers
      </p>
    </div>
  );
}
