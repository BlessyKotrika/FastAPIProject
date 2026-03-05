"use client";
import React, { useState } from 'react';
import { useAppStore } from '@/lib/store';
import { useTranslation } from '@/lib/i18n';
import { Tractor, MapPin, Languages, ChevronRight, Check } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Onboarding() {
  const { setProfile } = useAppStore();
  const { t } = useTranslation();
  const [step, setStep] = useState(0);

  const steps = [
    { id: 'lang', title: t('onboarding.selectLang'), icon: Languages },
    { id: 'loc', title: t('onboarding.location'), icon: MapPin },
    { id: 'farm', title: t('onboarding.farmDetails'), icon: Tractor },
  ];
  const [form, setForm] = useState({
    language: 'hi',
    state: '',
    district: '',
    crop: '',
    sowing_date: '',
  });

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      setProfile({ 
        ...form, 
        district: form.district,
        state: form.state,
        location: form.district, // for backward compatibility in some components
        is_onboarded: true, 
        user_id: 'user_' + Math.random().toString(36).substr(2, 9) 
      });
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6 flex flex-col max-w-md mx-auto">
      {/* Progress */}
      <div className="flex justify-between mb-12 relative">
        <div className="absolute top-5 left-0 w-full h-[2px] bg-slate-200 -z-10"></div>
        {steps.map((s, i) => (
          <div key={s.id} className="flex flex-col items-center gap-2">
            <div className={`w-10 h-10 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 shadow-sm ${
              i <= step ? 'bg-primary-600 border-primary-600 text-white scale-110 shadow-primary-200' : 'bg-white border-slate-200 text-slate-300'
            }`}>
              {i < step ? <Check size={20} className="stroke-[3px]" /> : <s.icon size={20} />}
            </div>
            <span className={`text-[8px] font-bold uppercase tracking-wider ${
              i <= step ? 'text-primary-600' : 'text-slate-400'
            }`}>{s.title}</span>
          </div>
        ))}
      </div>

      <div className="flex-1">
        {step === 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h2 className="text-3xl font-bold text-slate-900 mb-2 leading-tight">{t('onboarding.pickLang')}</h2>
            <p className="text-slate-500 text-sm mb-8 font-medium">{t('onboarding.pickLangSub')}</p>
            <div className="grid grid-cols-1 gap-3">
              {[
                { code: 'hi', name: 'हिन्दी', sub: 'Hindi' },
                { code: 'en', name: 'English', sub: 'Global' },
                { code: 'te', name: 'తెలుగు', sub: 'Telugu' },
                { code: 'ta', name: 'தமிழ்', sub: 'Tamil' },
                { code: 'bn', name: 'বাংলা', sub: 'Bengali' },
              ].map((l) => (
                <button
                  key={l.code}
                  onClick={() => setForm({ ...form, language: l.code })}
                  className={`p-4 rounded-2xl border-2 text-left flex justify-between items-center transition-all ${
                    form.language === l.code ? 'border-primary-600 bg-white shadow-xl shadow-primary-100 text-primary-700' : 'border-slate-100 bg-white hover:border-primary-200'
                  }`}
                >
                  <div>
                    <p className="text-lg font-bold">{l.name}</p>
                    <p className="text-[10px] opacity-60 uppercase font-bold tracking-widest">{l.sub}</p>
                  </div>
                  {form.language === l.code && <div className="bg-primary-600 text-white p-1 rounded-full"><Check size={16} /></div>}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        {step === 1 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h2 className="text-3xl font-bold text-slate-900 mb-2 leading-tight">{t('onboarding.landLocation')}</h2>
            <p className="text-slate-500 text-sm mb-8 font-medium">{t('onboarding.landLocationSub')}</p>
            <div className="space-y-6">
              <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
                <label className="text-[10px] font-bold text-slate-400 uppercase mb-2 block tracking-widest px-2">{t('onboarding.state')}</label>
                <input
                  type="text"
                  placeholder="e.g. Uttar Pradesh"
                  className="w-full p-4 bg-slate-50 rounded-xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all font-semibold text-slate-800"
                  value={form.state}
                  onChange={(e) => setForm({ ...form, state: e.target.value })}
                />
              </div>
              <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
                <label className="text-[10px] font-bold text-slate-400 uppercase mb-2 block tracking-widest px-2">{t('onboarding.district')}</label>
                <input
                  type="text"
                  placeholder="e.g. Barabanki"
                  className="w-full p-4 bg-slate-50 rounded-xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all font-semibold text-slate-800"
                  value={form.district}
                  onChange={(e) => setForm({ ...form, district: e.target.value })}
                />
              </div>
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h2 className="text-3xl font-bold text-slate-900 mb-2 leading-tight">{t('onboarding.mainCrop')}</h2>
            <p className="text-slate-500 text-sm mb-8 font-medium">{t('onboarding.mainCropSub')}</p>
            <div className="space-y-6">
              <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
                <label className="text-[10px] font-bold text-slate-400 uppercase mb-2 block tracking-widest px-2">{t('onboarding.cropName')}</label>
                <select 
                  className="w-full p-4 bg-slate-50 rounded-xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all appearance-none font-semibold text-slate-800"
                  value={form.crop}
                  onChange={(e) => setForm({ ...form, crop: e.target.value })}
                >
                  <option value="">{t('onboarding.selectCrop')}</option>
                  <option value="wheat">{t('onboarding.crops.wheat')} (गेहूं)</option>
                  <option value="paddy">{t('onboarding.crops.paddy')} (धान)</option>
                  <option value="cotton">{t('onboarding.crops.cotton')} (कपास)</option>
                  <option value="maize">{t('onboarding.crops.maize')} (मक्का)</option>
                </select>
              </div>
              <div className="bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
                <label className="text-[10px] font-bold text-slate-400 uppercase mb-2 block tracking-widest px-2">{t('onboarding.sowingDate')}</label>
                <input
                  type="date"
                  className="w-full p-4 bg-slate-50 rounded-xl border border-slate-100 focus:outline-none focus:border-primary-300 focus:bg-white transition-all font-semibold text-slate-800"
                  value={form.sowing_date}
                  onChange={(e) => setForm({ ...form, sowing_date: e.target.value })}
                />
              </div>
            </div>
          </motion.div>
        )}
      </div>

      <button
        onClick={handleNext}
        disabled={(step === 1 && (!form.state || !form.district)) || (step === 2 && !form.crop)}
        className="bg-primary-600 text-white w-full py-5 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 shadow-xl shadow-primary-200 disabled:opacity-50 disabled:shadow-none transition-all active:scale-95 mt-8 mb-4"
      >
        {step === steps.length - 1 ? t('common.startFarming') : t('common.continue')}
        <ChevronRight size={24} className="stroke-[3px]" />
      </button>
    </div>
  );
}
