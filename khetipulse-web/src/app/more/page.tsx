"use client";
import React, { useState } from 'react';
import { useAppStore } from '@/lib/store';
import { useTranslation } from '@/lib/i18n';
import Layout from '@/components/Layout';
import { 
  User, 
  Settings, 
  Languages, 
  Bell, 
  HelpCircle, 
  LogOut, 
  ChevronRight, 
  UserCircle2,
  Phone,
  MapPin,
  Sprout,
  Check
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function MorePage() {
  const { profile, setProfile, logout } = useAppStore();
  const { t } = useTranslation();
  const [showLangModal, setShowLangModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState({
    full_name: profile.full_name || '',
    mobile_number: profile.mobile_number || '',
    district: profile.district || '',
    state: profile.state || '',
    crop: profile.crop || '',
    sowing_date: profile.sowing_date || '',
  });

  const handleEditSave = () => {
    setProfile({
      ...editForm,
      location: editForm.district, // for backward compatibility
    });
    setShowEditModal(false);
  };

  const menuItems = [
    { id: 'lang', label: t('more.langSettings'), icon: Languages, value: profile.language.toUpperCase(), color: 'bg-blue-50 text-blue-600' },
    { id: 'notify', label: t('more.notifications'), icon: Bell, value: 'On', color: 'bg-amber-50 text-amber-600' },
    { id: 'help', label: t('more.help'), icon: HelpCircle, color: 'bg-purple-50 text-purple-600' },
    { id: 'terms', label: t('more.terms'), icon: Settings, color: 'bg-slate-50 text-slate-600' },
  ];

  const languages = [
    { code: 'hi', name: 'हिन्दी', sub: 'Hindi' },
    { code: 'en', name: 'English', sub: 'Global' },
    { code: 'te', name: 'తెలుగు', sub: 'Telugu' },
    { code: 'ta', name: 'தமிழ்', sub: 'Tamil' },
    { code: 'bn', name: 'বাংলা', sub: 'Bengali' },
  ];

  return (
    <Layout>
      <div className="p-4 space-y-6">
        <section className="px-1">
          <h2 className="text-2xl font-bold text-slate-900 leading-tight">{t('more.title')}</h2>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-1">{t('more.subtitle')}</p>
        </section>

        {/* Profile Card */}
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-[2rem] p-6 shadow-sm border border-slate-100 relative group"
        >
          <button 
            onClick={() => {
              setEditForm({
                full_name: profile.full_name || '',
                mobile_number: profile.mobile_number || '',
                district: profile.district || '',
                state: profile.state || '',
                crop: profile.crop || '',
                sowing_date: profile.sowing_date || '',
              });
              setShowEditModal(true);
            }}
            className="absolute top-6 right-6 p-2 bg-primary-50 text-primary-600 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"
          >
            <Settings size={18} />
          </button>
          <div className="flex items-center gap-4 mb-6">
            <div className="bg-primary-600 w-16 h-16 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-primary-200 overflow-hidden">
              <UserCircle2 size={40} />
            </div>
            <div>
              <h3 className="font-bold text-lg text-slate-900 leading-tight">{profile.full_name || t('more.profile')}</h3>
              <p className="text-sm font-medium text-slate-400 mt-1">{profile.user_id}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4">
            <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-100">
              <Phone size={16} className="text-slate-400" />
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{t('more.mobile')}</p>
                <p className="text-sm font-bold text-slate-700">{profile.mobile_number || t('more.notLinked')}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-100">
              <MapPin size={16} className="text-slate-400" />
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{t('more.location')}</p>
                <p className="text-sm font-bold text-slate-700">{profile.district}, {profile.state}</p>
              </div>
            </div>
            <div className="flex items-center gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-100">
              <Sprout size={16} className="text-slate-400" />
              <div>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{t('more.primaryCrop')}</p>
                <p className="text-sm font-bold text-slate-700">
                  {t(`onboarding.crops.${profile.crop}`) || profile.crop} ({t('more.sown')}: {profile.sowing_date})
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Menu Items */}
        <div className="space-y-3">
          {menuItems.map((item, i) => (
            <motion.button
              key={i}
              whileTap={{ scale: 0.98 }}
              onClick={() => item.id === 'lang' && setShowLangModal(true)}
              className="w-full bg-white p-4 rounded-2xl flex justify-between items-center shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-3">
                <div className={`${item.color} p-2.5 rounded-xl`}>
                  <item.icon size={20} />
                </div>
                <span className="font-bold text-slate-700 text-sm">{item.label}</span>
              </div>
              <div className="flex items-center gap-2">
                {item.value && (
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest bg-slate-50 px-2 py-1 rounded-lg border border-slate-100">
                    {item.value}
                  </span>
                )}
                <ChevronRight size={18} className="text-slate-300" />
              </div>
            </motion.button>
          ))}
        </div>

        {/* Logout Button */}
        <motion.button
          onClick={() => {
            if (confirm(t('more.confirmReset'))) {
              logout();
              window.location.href = '/login';
            }
          }}
          whileTap={{ scale: 0.98 }}
          className="w-full bg-rose-50 p-5 rounded-2xl flex items-center justify-center gap-3 text-rose-600 border border-rose-100 font-bold text-sm uppercase tracking-widest mt-8 mb-4 hover:bg-rose-100 transition-colors"
        >
          <LogOut size={20} />
          {t('more.logout')}
        </motion.button>

        {/* Language Selection Modal */}
        <AnimatePresence>
          {showLangModal && (
            <>
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowLangModal(false)}
                className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50"
              />
              <motion.div 
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 100, opacity: 0 }}
                className="fixed bottom-0 left-0 right-0 bg-white rounded-t-[2.5rem] p-6 z-50 shadow-2xl max-w-md mx-auto"
              >
                <div className="w-12 h-1.5 bg-slate-200 rounded-full mx-auto mb-8" />
                <h3 className="text-2xl font-bold text-slate-900 mb-6">{t('more.langSettings')}</h3>
                <div className="space-y-3 mb-8">
                  {languages.map((l) => (
                    <button
                      key={l.code}
                      onClick={() => {
                        setProfile({ language: l.code });
                        setShowLangModal(false);
                      }}
                      className={`w-full p-4 rounded-2xl border-2 text-left flex justify-between items-center transition-all ${
                        profile.language === l.code ? 'border-primary-600 bg-primary-50 text-primary-700' : 'border-slate-50 bg-slate-50'
                      }`}
                    >
                      <div>
                        <p className="text-lg font-bold">{l.name}</p>
                        <p className="text-[10px] opacity-60 uppercase font-bold tracking-widest">{l.sub}</p>
                      </div>
                      {profile.language === l.code && <div className="bg-primary-600 text-white p-1 rounded-full"><Check size={16} /></div>}
                    </button>
                  ))}
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Edit Profile Modal */}
        <AnimatePresence>
          {showEditModal && (
            <>
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setShowEditModal(false)}
                className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50"
              />
              <motion.div 
                initial={{ y: 100, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                exit={{ y: 100, opacity: 0 }}
                className="fixed bottom-0 left-0 right-0 bg-white rounded-t-[2.5rem] p-6 z-50 shadow-2xl max-w-md mx-auto overflow-y-auto max-h-[90vh]"
              >
                <div className="w-12 h-1.5 bg-slate-200 rounded-full mx-auto mb-8" />
                <h3 className="text-2xl font-bold text-slate-900 mb-6">{t('more.profile')}</h3>
                
                <div className="space-y-4 mb-8">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase px-2">{t('common.fullName')}</label>
                    <input 
                      type="text"
                      className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 font-semibold text-slate-800"
                      value={editForm.full_name}
                      onChange={(e) => setEditForm({...editForm, full_name: e.target.value})}
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase px-2">{t('more.mobile')}</label>
                    <input 
                      type="text"
                      className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 font-semibold text-slate-800"
                      value={editForm.mobile_number}
                      onChange={(e) => setEditForm({...editForm, mobile_number: e.target.value})}
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <label className="text-[10px] font-bold text-slate-400 uppercase px-2">{t('onboarding.state')}</label>
                      <input 
                        type="text"
                        className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 font-semibold text-slate-800"
                        value={editForm.state}
                        onChange={(e) => setEditForm({...editForm, state: e.target.value})}
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] font-bold text-slate-400 uppercase px-2">{t('onboarding.district')}</label>
                      <input 
                        type="text"
                        className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 font-semibold text-slate-800"
                        value={editForm.district}
                        onChange={(e) => setEditForm({...editForm, district: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase px-2">{t('onboarding.cropName')}</label>
                    <select 
                      className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 font-semibold text-slate-800 appearance-none"
                      value={editForm.crop}
                      onChange={(e) => setEditForm({...editForm, crop: e.target.value})}
                    >
                      <option value="wheat">{t('onboarding.crops.wheat')}</option>
                      <option value="paddy">{t('onboarding.crops.paddy')}</option>
                      <option value="cotton">{t('onboarding.crops.cotton')}</option>
                      <option value="maize">{t('onboarding.crops.maize')}</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase px-2">{t('onboarding.sowingDate')}</label>
                    <input 
                      type="date"
                      className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:outline-none focus:border-primary-300 font-semibold text-slate-800"
                      value={editForm.sowing_date}
                      onChange={(e) => setEditForm({...editForm, sowing_date: e.target.value})}
                    />
                  </div>
                </div>

                <button 
                  onClick={handleEditSave}
                  className="w-full bg-primary-600 text-white py-4 rounded-2xl font-bold text-sm uppercase tracking-widest shadow-lg shadow-primary-100 active:scale-95 transition-all mb-4"
                >
                  {t('common.continue')}
                </button>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    </Layout>
  );
}
