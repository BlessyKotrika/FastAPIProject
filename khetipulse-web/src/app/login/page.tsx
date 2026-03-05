"use client";
import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAppStore } from '@/lib/store';
import { authService } from '@/services/api';
import { motion } from 'framer-motion';
import { LayoutDashboard, Sparkles, ShieldCheck, Globe } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const { setAuth, setProfile } = useAppStore();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSuccess = async (credentialResponse: any) => {
    setLoading(true);
    setError('');
    try {
      const { access_token } = await authService.loginWithGoogle(credentialResponse.credential);
      
      // Update store with token
      setAuth({ token: access_token, isAuthenticated: true });

      // Fetch user profile from /me
      const user = await authService.getMe();
      setProfile({
        user_id: user.username,
        email: user.email,
        full_name: user.full_name,
        picture: user.picture,
        mobile_number: user.mobile_number || '',
      });

      // Redirect to home/onboarding
      router.push('/');
    } catch (err: any) {
      console.error(err);
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
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
          <div className="bg-primary-600 w-20 h-20 rounded-[2rem] flex items-center justify-center text-white shadow-2xl shadow-primary-200 mx-auto rotate-3">
            <LayoutDashboard size={40} />
          </div>
          <div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tight leading-none">KhetiPulse</h1>
            <p className="text-sm font-bold text-primary-600 uppercase tracking-[0.3em] mt-2">Smart Agriculture</p>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 gap-3">
          {[
            { icon: Sparkles, text: "AI-Powered Farm Advisory", color: "text-amber-500", bg: "bg-amber-50" },
            { icon: ShieldCheck, text: "Secure Google Authentication", color: "text-emerald-500", bg: "bg-emerald-50" },
            { icon: Globe, text: "Multilingual Support", color: "text-blue-500", bg: "bg-blue-50" },
          ].map((feature, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * (i + 1) }}
              className="flex items-center gap-4 bg-white p-4 rounded-2xl border border-slate-100 shadow-sm"
            >
              <div className={`${feature.bg} p-2 rounded-xl ${feature.color}`}>
                <feature.icon size={20} />
              </div>
              <span className="text-sm font-bold text-slate-700">{feature.text}</span>
            </motion.div>
          ))}
        </div>

        {/* Login Section */}
        <div className="bg-white p-8 rounded-[2.5rem] shadow-xl shadow-slate-200 border border-slate-100 text-center space-y-6">
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-slate-900">Welcome Back</h2>
            <p className="text-xs font-medium text-slate-400">Sign in with your Google account to continue</p>
          </div>

          <div className="flex justify-center">
            {loading ? (
              <div className="flex items-center gap-3 text-primary-600 font-bold animate-pulse">
                <div className="w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                Authenticating...
              </div>
            ) : (
              <GoogleLogin
                onSuccess={handleSuccess}
                onError={() => setError('Google Login Failed')}
                useOneTap
                theme="filled_blue"
                shape="pill"
                text="continue_with"
                width="280"
              />
            )}
          </div>

          {error && (
            <motion.p 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }}
              className="text-xs font-bold text-rose-500 bg-rose-50 p-3 rounded-xl border border-rose-100"
            >
              {error}
            </motion.p>
          )}

          <p className="text-[10px] text-slate-400 font-medium leading-relaxed">
            By signing in, you agree to our <span className="underline">Terms of Service</span> and <span className="underline">Privacy Policy</span>.
          </p>
        </div>
      </motion.div>

      {/* Footer Branding */}
      <p className="mt-12 text-[10px] font-bold text-slate-300 uppercase tracking-[0.2em] relative z-10">
        Empowering Indian Farmers
      </p>
    </div>
  );
}
