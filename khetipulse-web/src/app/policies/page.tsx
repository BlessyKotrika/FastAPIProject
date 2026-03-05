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
  const { t } = useTranslation();
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
              {data?.eligible_schemes?.map((scheme: string, i: number) => (
                <motion.div 
                  key={i}
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-white p-5 rounded-[2rem] shadow-sm border border-slate-100 flex items-start gap-4 hover:shadow-md transition-shadow group"
                >
                  <div className="bg-primary-50 p-3 rounded-2xl text-primary-600 group-hover:bg-primary-600 group-hover:text-white transition-colors">
                    <ShieldCheck size={24} />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-slate-900 mb-1 leading-tight">{scheme}</h4>
                    <p className="text-xs text-slate-500 leading-relaxed">
                      {t('policies.support', { crop: t(`onboarding.crops.${profile.crop}`) || profile.crop })}
                    </p>
                    <div className="flex items-center gap-2 mt-3">
                      <span className="text-[10px] font-bold text-primary-600 bg-primary-50 px-2.5 py-1 rounded-lg uppercase tracking-wider">{t('policies.eligible')}</span>
                      <button className="ml-auto flex items-center gap-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-widest hover:text-primary-600 transition-colors">
                        {t('common.details')} <ExternalLink size={12} />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Required Documents Card */}
            <motion.div 
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              className="bg-slate-900 rounded-[2.5rem] p-6 text-white shadow-xl shadow-slate-200"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="bg-white/10 p-2.5 rounded-xl">
                  <FileCheck className="w-5 h-5 text-primary-400" />
                </div>
                <h3 className="font-bold text-lg tracking-tight">{t('policies.docsNeeded')}</h3>
              </div>
              
              <ul className="grid grid-cols-1 gap-3">
                {data?.documents_required?.map((doc: string, i: number) => (
                  <li key={i} className="flex items-center gap-3 bg-white/5 p-3 rounded-2xl border border-white/5">
                    <div className="w-1.5 h-1.5 bg-primary-500 rounded-full shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
                    <span className="text-sm font-medium opacity-90">{doc}</span>
                  </li>
                ))}
              </ul>

              <div className="mt-8">
                <button className="w-full bg-primary-600 hover:bg-primary-500 text-white py-4 rounded-2xl font-bold text-sm uppercase tracking-widest flex items-center justify-center gap-2 transition-all active:scale-95 shadow-lg shadow-primary-900/20">
                  {t('policies.applyNow')} <ExternalLink size={16} />
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </div>
    </Layout>
  );
}
