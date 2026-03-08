"use client";

import React, { useEffect, useRef, useState } from "react";
import { useAppStore } from "@/lib/store";
import { useTranslation } from "@/lib/i18n";
import { todayService } from "@/services/api";
import Layout from "@/components/Layout";
import Onboarding from "@/components/Onboarding";
import { useRouter } from "next/navigation";
import {
  CloudRain,
  Wind,
  Thermometer,
  Tractor,
  Ban,
  Calendar,
  ChevronRight,
} from "lucide-react";
import { motion } from "framer-motion";

export default function Dashboard() {
  const { profile, auth, _hasHydrated } = useAppStore();
  const { t, tCrop } = useTranslation();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isReady, setIsReady] = useState(false);
  const lastRequestKeyRef = useRef<string>("");
  const inFlightRef = useRef(false);
  const router = useRouter();

  useEffect(() => {
    if (!_hasHydrated) return;
    if (!auth.isAuthenticated) {
      setIsReady(true);
      router.replace("/login");
      return;
    }
    setIsReady(true);
    if (!profile.is_onboarded) {
      return;
    }
    fetchDashboard();
  }, [
    auth.isAuthenticated,
    profile.is_onboarded,
    profile.user_id,
    profile.crop,
    profile.location,
    profile.sowing_date,
    profile.language,
    router,
    _hasHydrated,
  ]);

  const fetchDashboard = async () => {
    const requestKey = [
      profile.user_id,
      profile.crop,
      profile.location,
      profile.sowing_date,
      profile.language,
    ].join("|");

    if (inFlightRef.current || lastRequestKeyRef.current === requestKey) {
      return;
    }
    if (!profile.crop || !profile.location || !profile.sowing_date) {
      setLoading(false);
      return;
    }

    try {
      inFlightRef.current = true;
      lastRequestKeyRef.current = requestKey;
      setLoading(true);
      const res = await todayService.getActions({
        user_id: profile.user_id || "user",
        crop: profile.crop,
        location: profile.location,
        sowing_date: profile.sowing_date,
        language: profile.language,
      });
      setData(res);
    } catch (err) {
      console.error(err);
      lastRequestKeyRef.current = "";
    } finally {
      inFlightRef.current = false;
      setLoading(false);
    }
  };

  if (!_hasHydrated || !isReady) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!profile.is_onboarded) {
    return <Onboarding />;
  }

  const currentWeather = data?.current_weather || {};
  const currentTemp =
    typeof currentWeather.temp === "number" ? Math.round(currentWeather.temp) : null;
  const currentCondition = currentWeather.description || currentWeather.condition || "N/A";
  const humidity =
    typeof currentWeather.humidity === "number" ? `${Math.round(currentWeather.humidity)}%` : "--";
  const windSpeed =
    typeof currentWeather.wind_speed === "number"
      ? `${Math.round(currentWeather.wind_speed)} km/h`
      : "--";
  const rainForecast = data?.weather_risk?.rain_forecast ? "Yes" : "No";

  return (
    <Layout>
      <div className="p-4 space-y-6">
        <section className="flex justify-between items-end px-1">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 leading-tight">{t("common.namaste")}</h2>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              {tCrop(profile.crop) || profile.crop} | {profile.location}
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] font-bold text-primary-600 uppercase tracking-tighter">
              {t("dashboard.farmHealth")}
            </p>
            <div className="flex gap-1 mt-1">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className={`w-3 h-1 rounded-full ${i <= 4 ? "bg-primary-500" : "bg-slate-200"}`}
                />
              ))}
            </div>
          </div>
        </section>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900 rounded-[2rem] p-6 text-white shadow-2xl shadow-slate-200 relative overflow-hidden"
        >
          <div className="absolute -right-4 -top-4 w-32 h-32 bg-primary-500/10 rounded-full blur-3xl" />
          <div className="absolute -left-4 -bottom-4 w-24 h-24 bg-accent-500/10 rounded-full blur-2xl" />

          <div className="flex justify-between items-start mb-6 relative z-10">
            <div>
              <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">
                {t("dashboard.liveForecast")}
              </p>
              <h3 className="text-4xl font-bold mt-1">
                {currentTemp !== null ? `${currentTemp}` : "--"}
                <span className="text-xl opacity-50">C</span>
              </h3>
              <p className="text-sm font-medium opacity-80 mt-1 text-primary-400">{currentCondition}</p>
            </div>
            <div className="bg-white/5 backdrop-blur-md p-3 rounded-2xl border border-white/10">
              <CloudRain className="w-8 h-8 text-primary-400" />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 bg-white/5 p-4 rounded-2xl backdrop-blur-md border border-white/5 relative z-10">
            <div className="text-center">
              <div className="text-slate-400 mb-1 flex justify-center">
                <CloudRain size={16} />
              </div>
              <p className="text-[10px] font-medium opacity-60 uppercase">{t("dashboard.rain")}</p>
              <p className="text-sm font-bold">{rainForecast}</p>
            </div>
            <div className="text-center border-x border-white/5 px-2">
              <div className="text-slate-400 mb-1 flex justify-center">
                <Wind size={16} />
              </div>
              <p className="text-[10px] font-medium opacity-60 uppercase">{t("dashboard.wind")}</p>
              <p className="text-sm font-bold">{windSpeed}</p>
            </div>
            <div className="text-center">
              <div className="text-slate-400 mb-1 flex justify-center">
                <Thermometer size={16} />
              </div>
              <p className="text-[10px] font-medium opacity-60 uppercase">{t("dashboard.humidity")}</p>
              <p className="text-sm font-bold">{humidity}</p>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-2 gap-4">
          <motion.div
            whileTap={{ scale: 0.96 }}
            className="bg-white p-4 rounded-[1.5rem] shadow-sm border border-slate-100 flex flex-col hover:shadow-md transition-shadow"
          >
            <div className="bg-emerald-50 w-10 h-10 rounded-xl flex items-center justify-center text-emerald-600 mb-3">
              <Tractor className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-800 text-xs mb-2 uppercase tracking-wide">
              {t("dashboard.doToday")}
            </h3>
            {loading ? (
              <div className="space-y-2">
                <div className="h-2 bg-slate-50 rounded w-full animate-pulse" />
                <div className="h-2 bg-slate-50 rounded w-2/3 animate-pulse" />
              </div>
            ) : (
              <ul className="space-y-2 flex-1">
                {data?.do?.slice(0, 2).map((item: string, i: number) => (
                  <li key={i} className="text-[10px] font-medium text-slate-600 leading-snug">
                    - {item}
                  </li>
                ))}
              </ul>
            )}
          </motion.div>

          <motion.div
            whileTap={{ scale: 0.96 }}
            className="bg-white p-4 rounded-[1.5rem] shadow-sm border border-slate-100 flex flex-col hover:shadow-md transition-shadow"
          >
            <div className="bg-rose-50 w-10 h-10 rounded-xl flex items-center justify-center text-rose-600 mb-3">
              <Ban className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-slate-800 text-xs mb-2 uppercase tracking-wide">
              {t("dashboard.avoidToday")}
            </h3>
            {loading ? (
              <div className="space-y-2">
                <div className="h-2 bg-slate-50 rounded w-full animate-pulse" />
                <div className="h-2 bg-slate-50 rounded w-2/3 animate-pulse" />
              </div>
            ) : (
              <ul className="space-y-2 flex-1">
                {data?.avoid?.slice(0, 2).map((item: string, i: number) => (
                  <li key={i} className="text-[10px] font-medium text-slate-600 leading-snug">
                    - {item}
                  </li>
                ))}
              </ul>
            )}
          </motion.div>
        </div>

        <motion.div
          whileTap={{ scale: 0.98 }}
          className="bg-accent-600 rounded-[1.5rem] p-4 text-white flex justify-between items-center shadow-lg shadow-accent-100"
        >
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2.5 rounded-xl">
              <Calendar className="w-5 h-5 text-white" />
            </div>
            <div>
              <h4 className="font-bold text-sm tracking-tight">{t("dashboard.next48h")}</h4>
              <p className="text-[10px] opacity-80">{t("dashboard.checkSpray")}</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 opacity-50" />
        </motion.div>
      </div>
    </Layout>
  );
}
