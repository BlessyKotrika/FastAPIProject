"use client";
import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/lib/store';
import { useTranslation } from '@/lib/i18n';
import { schemeService } from '@/services/api';
import Layout from '@/components/Layout';
import { BookOpen, ExternalLink, FileCheck, Landmark, ShieldCheck, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function PoliciesPage() {
  const { profile } = useAppStore();
  const { t, tCrop } = useTranslation();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSchemes();
  }, [profile]);

  const fetchSchemes = async () => {
    try {
      setLoading(true);
      const res = await schemeService.getSchemes({
        state: profile.state || 'Uttar Pradesh',
        land_size: 2.5,
        category: 'Small',
        crop: profile.crop || 'wheat',
        language: profile.language,
      });
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-4 space-y-6">
        <section className="px-1">
          <div className="flex items-center gap-3">
            <div className="bg-primary-600 p-2 rounded-xl text-white shadow-lg shadow-primary-100">
              <Landmark size={20} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 leading-tight">{t('policies.title')}</h2>
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-1">
            {t('policies.subtitle', { state: profile.state || t('onboarding.location') })}
          </p>
        </section>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <Loader2 className="w-10 h-10 text-primary-500 animate-spin" />
            <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{t('policies.finding')}</p>
          </div>
        ) : (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            {/* Eligible Schemes List */}
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-widest px-1">{t('policies.recommendations')}</h3>
              {data?.schemes?.map((scheme: any, i: number) => (
                <motion.div 
                  key={i}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-white p-5 rounded-[2rem] shadow-sm border border-slate-100 flex flex-col gap-4 hover:shadow-md transition-shadow group"
                >
                  <div className="flex items-start gap-4">
                    <div className="bg-primary-50 p-3 rounded-2xl text-primary-600 group-hover:bg-primary-600 group-hover:text-white transition-colors shrink-0">
                      <ShieldCheck size={24} />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-slate-900 mb-1 leading-tight">{scheme.name}</h4>
                      <p className="text-xs text-slate-500 leading-relaxed">
                        {scheme.description || t('policies.support', { crop: tCrop(profile.crop) || profile.crop })}
                      </p>
                      <div className="mt-2">
                        <span className="text-[10px] font-bold text-primary-600 bg-primary-50 px-2.5 py-1 rounded-lg uppercase tracking-wider">{t('policies.eligible')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Documents for this scheme */}
                  {scheme.documents && scheme.documents.length > 0 && (
                    <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                        <FileCheck size={12} /> {t('policies.docsNeeded')}
                      </p>
                      <ul className="space-y-2">
                        {scheme.documents.map((doc: string, idx: number) => (
                          <li key={idx} className="flex items-center gap-2 text-[11px] font-medium text-slate-600">
                            <div className="w-1 h-1 bg-primary-400 rounded-full"></div>
                            {doc}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Button for this scheme */}
                  <button 
                    onClick={() => {
                      if (scheme.link) {
                        window.open(scheme.link, '_blank');
                      } else {
                        alert('Application link not available.');
                      }
                    }}
                    className="w-full bg-primary-600 hover:bg-primary-500 text-white py-3.5 rounded-2xl font-bold text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all active:scale-[0.98] shadow-lg shadow-primary-100"
                  >
                    {t('policies.applyNow')} <ExternalLink size={14} />
                  </button>
                </motion.div>
              ))}
            </div>

            {/* General Info or Disclaimer Card */}
            <motion.div 
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="bg-slate-900 rounded-[2.5rem] p-6 text-white shadow-xl shadow-slate-200"
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="bg-white/10 p-3 rounded-2xl">
                  <BookOpen className="w-6 h-6 text-primary-400" />
                </div>
                <div>
                  <h3 className="font-bold text-lg tracking-tight">Farmer's Guide</h3>
                  <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">Important Information</p>
                </div>
              </div>
              
              <p className="text-sm font-medium opacity-80 leading-relaxed mb-4">
                Keep your Aadhaar Card and Land Records updated to ensure a smooth application process for all government schemes.
              </p>
              
              <div className="bg-white/5 p-4 rounded-2xl border border-white/5">
                <p className="text-[10px] font-bold text-primary-400 uppercase tracking-widest mb-2">Pro Tip</p>
                <p className="text-xs italic opacity-70">
                  "Most schemes require a bank account linked to your Aadhaar for direct benefit transfer (DBT)."
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </Layout>
  );
}


