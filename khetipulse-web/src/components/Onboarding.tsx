"use client";

import React, { useState, useEffect } from "react";
import { useAppStore } from "@/lib/store";
import { useTranslation } from "@/lib/i18n";
import { Tractor, MapPin, Languages, ChevronRight, Check, Search } from "lucide-react";
import { motion } from "framer-motion";
import { authService } from "@/services/api";

const API = process.env.NEXT_PUBLIC_API_URL;

export default function Onboarding() {
  const { setProfile, profile } = useAppStore();
  const { t, tCrop, getCropCode } = useTranslation();

  const steps = [
    { id: "lang", title: t("onboarding.selectLang"), icon: Languages },
    { id: "loc", title: t("onboarding.location"), icon: MapPin },
    { id: "farm", title: t("onboarding.farmDetails"), icon: Tractor },
  ];

  const [states, setStates] = useState<string[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [crops, setCrops] = useState<string[]>([]);

  const [form, setForm] = useState({
    language: profile.language || "",
    state: profile.state || "",
    district: profile.district || "",
    crops: (profile.crops && profile.crops.length > 0)
      ? Array.from(new Set(profile.crops.map((c) => getCropCode(c)).filter(Boolean)))
      : (profile.crop ? [getCropCode(profile.crop)] : []),
    sowing_date: profile.sowing_date || "",
  });

  const [step, setStep] = useState(0);
  const [cropSearch, setCropSearch] = useState("");

  const filteredCrops = crops.filter(crop => {
    const label = (tCrop(crop) || crop).toLowerCase();
    return label.includes(cropSearch.toLowerCase());
  });

  useEffect(() => {
    async function loadOnboardingData() {
      try {
        const statesRes = await fetch(`${API}/onboarding/states`);
        const statesData = await statesRes.json();
        setStates(statesData);

        const cropsRes = await fetch(`${API}/onboarding/crops`);
        const cropsData = await cropsRes.json();
        const normalized = Array.isArray(cropsData)
          ? Array.from(new Set(cropsData.map((c: string) => getCropCode(c)).filter(Boolean)))
          : [];
        setCrops(normalized);
      } catch (e) {
        console.error("Failed loading onboarding data", e);
      }
    }

    loadOnboardingData();

  }, []);

  const handleStateChange = async (state: string) => {
    setForm({ ...form, state, district: "" });

    try {
      const res = await fetch(`${API}/onboarding/districts/${state}`);
      const data = await res.json();
      setDistricts(data);
    } catch (e) {
      console.error("Failed loading districts", e);
    }

  };

  const handleNext = async () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      const updatedProfile = {
        ...form,
        crop: form.crops[0] || "",
        district: form.district,
        state: form.state,
        crops: form.crops,
        location: form.district,
        is_onboarded: true,
      };

      setProfile(updatedProfile);

      try {
        await authService.updateProfile(updatedProfile);
      } catch (e) {
        console.error("Failed to save profile", e);
      }
    }

  };

  return (<div className="min-h-screen bg-slate-50 p-6 flex flex-col max-w-md mx-auto">

    {/* Progress Bar */}

    <div className="flex justify-between mb-12 relative">
      <div className="absolute top-5 left-0 w-full h-[2px] bg-slate-200 -z-10"></div>

      {steps.map((s, i) => (
        <div key={s.id} className="flex flex-col items-center gap-2">
          <div
            className={`w-10 h-10 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 shadow-sm ${i <= step
                ? "bg-primary-600 border-primary-600 text-white scale-110 shadow-primary-200"
                : "bg-white border-slate-200 text-slate-300"
              }`}
          >
            {i < step ? <Check size={20} /> : <s.icon size={20} />}
          </div>

          <span
            className={`text-[8px] font-bold uppercase tracking-wider ${i <= step ? "text-primary-600" : "text-slate-400"
              }`}
          >
            {s.title}
          </span>
        </div>
      ))}
    </div>

    <div className="flex-1">

      {/* LANGUAGE STEP */}

      {step === 0 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h2 className="text-3xl font-bold mb-6">
            {t("onboarding.pickLang")}
          </h2>

          <div className="grid gap-3">
            {[
              { code: "hi", name: "हिन्दी", sub: "Hindi" },
              { code: "en", name: "English", sub: "Global" },
              { code: "te", name: "తెలుగు", sub: "Telugu" },
              { code: "ta", name: "தமிழ்", sub: "Tamil" },
              { code: "bn", name: "বাংলা", sub: "Bengali" },
            ].map((l) => (
              <button
                key={l.code}
                onClick={() => {
                  setForm({ ...form, language: l.code });
                  setProfile({ language: l.code });
                }}
                className={`p-4 rounded-2xl border-2 flex justify-between ${form.language === l.code
                    ? "border-primary-600"
                    : "border-slate-200"
                  }`}
              >
                <div>
                  <p className="font-bold">{l.name}</p>
                  <p className="text-xs opacity-60">{l.sub}</p>
                </div>

                {form.language === l.code && <Check size={18} />}
              </button>
            ))}
          </div>
        </motion.div>
      )}

      {/* LOCATION STEP */}

      {step === 1 && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h2 className="text-3xl font-bold mb-6">
            {t("onboarding.landLocation")}
          </h2>

          <div className="space-y-6">

            {/* STATE */}

            <select
              className="w-full p-4 bg-white rounded-xl border"
              value={form.state}
              onChange={(e) => handleStateChange(e.target.value)}
            >
              <option value="">{t("onboarding.state")}</option>

              {states.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>

            {/* DISTRICT */}

            <select
              className="w-full p-4 bg-white rounded-xl border"
              value={form.district}
              onChange={(e) =>
                setForm({ ...form, district: e.target.value })
              }
              disabled={!form.state}
            >
              <option value="">{t("onboarding.district")}</option>

              {districts.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>

          </div>
        </motion.div>
      )}

      {/* FARM STEP */}

      {step === 2 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="mb-6">
            <h2 className="text-3xl font-bold mb-2">
              {t("onboarding.mainCrop")}
            </h2>
            <p className="text-slate-500 text-sm">
              {t("onboarding.mainCropSub") || "Select the crops you are currently growing."}
            </p>
          </div>

          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="text"
                placeholder={t("onboarding.searchCrop") || "Search crops..."}
                className="w-full pl-10 pr-4 py-3 bg-white rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                value={cropSearch}
                onChange={(e) => setCropSearch(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-3 max-h-[40vh] overflow-y-auto p-1">
              {filteredCrops.map((crop) => {
                const selected = form.crops.includes(crop);
                return (
                  <button
                    key={crop}
                    onClick={() => {
                      const next = selected
                        ? form.crops.filter((c) => c !== crop)
                        : [...form.crops, crop];
                      setForm({ ...form, crops: next });
                    }}
                    className={`flex flex-col items-center justify-center p-4 rounded-2xl border-2 transition-all duration-200 relative ${
                      selected
                        ? "border-primary-600 bg-primary-50 shadow-md shadow-primary-100 scale-[1.02]"
                        : "border-slate-100 bg-white hover:border-slate-200"
                    }`}
                  >
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-3 ${
                      selected ? "bg-primary-600 text-white" : "bg-slate-50 text-slate-400"
                    }`}>
                      <Tractor size={24} />
                    </div>
                    
                    <span className={`text-sm font-bold text-center ${
                      selected ? "text-primary-700" : "text-slate-600"
                    }`}>
                      {tCrop(crop) || crop}
                    </span>

                    {selected && (
                      <div className="absolute top-2 right-2 bg-primary-600 text-white rounded-full p-0.5">
                        <Check size={12} strokeWidth={3} />
                      </div>
                    )}
                  </button>
                );
              })}
              
              {filteredCrops.length === 0 && (
                <div className="col-span-2 py-8 text-center text-slate-400 italic">
                  No crops found matching "{cropSearch}"
                </div>
              )}
            </div>

            <div className="pt-2">
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 ml-1">
                {t("onboarding.sowingDate") || "Sowing Date"}
              </label>
              <div className="relative">
                <input
                  type="date"
                  className="w-full p-4 bg-white rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 transition-all outline-none"
                  value={form.sowing_date}
                  onChange={(e) =>
                    setForm({ ...form, sowing_date: e.target.value })
                  }
                />
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>

    {/* NEXT BUTTON */}

    <button
      onClick={handleNext}
      disabled={
        (step === 1 && (!form.state || !form.district)) ||
        (step === 2 && form.crops.length === 0)
      }
      className="bg-primary-600 text-white w-full py-5 rounded-2xl font-bold flex items-center justify-center gap-3 mt-8"
    >
      {step === steps.length - 1
        ? t("common.startFarming")
        : t("common.continue")}

      <ChevronRight size={22} />
    </button>

  </div>

  );
}
