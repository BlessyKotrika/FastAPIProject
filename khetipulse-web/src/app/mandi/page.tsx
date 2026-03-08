"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useAppStore } from "@/lib/store";
import { useTranslation } from "@/lib/i18n";
import { sellSmartService } from "@/services/api";
import Layout from "@/components/Layout";
import { TrendingUp, MapPin, Info, ArrowUpRight } from "lucide-react";
import { motion } from "framer-motion";

export default function MandiPage() {
  const { profile } = useAppStore();
  const { t, tCrop, getCropCode } = useTranslation();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAllMarkets, setShowAllMarkets] = useState(false);

  const cropOptions = useMemo(() => {
    const raw = profile.crops && profile.crops.length > 0 ? profile.crops : profile.crop ? [profile.crop] : [];
    const normalized = raw.map((c) => getCropCode(c)).filter(Boolean);
    return Array.from(new Set(normalized));
  }, [profile.crops, profile.crop, getCropCode]);

  const [selectedCrop, setSelectedCrop] = useState(cropOptions[0] || "");

  useEffect(() => {
    setSelectedCrop(cropOptions[0] || "");
  }, [cropOptions]);

  useEffect(() => {
    fetchMandi();
  }, [selectedCrop, profile.location, profile.state, profile.language]);

  const fetchMandi = async () => {
    if (!selectedCrop || !profile.location) {
      setLoading(false);
      setData({
        best_mandi: "Data not available for the selected crop.",
        net_price: 0,
        trend_7d: "N/A",
        forecast_band: "N/A",
        confidence_score: 0,
        all_markets: [],
      });
      return;
    }

    try {
      setLoading(true);
      const res = await sellSmartService.getMandiData({
        crop: selectedCrop,
        location: profile.location || "",
        state: profile.state || "",
        language: profile.language,
      });
      setData(res);
    } catch (err) {
      console.error(err);
      setData({
        best_mandi: "Data not available for the selected crop.",
        net_price: 0,
        trend_7d: "N/A",
        forecast_band: "N/A",
        confidence_score: 0,
        all_markets: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const noData = !loading && (!data?.all_markets || data.all_markets.length === 0);

  return (
    <Layout>
      <div className="p-4 space-y-6">
        <section className="px-1">
          <div className="flex items-center gap-3">
            <div className="bg-primary-600 p-2 rounded-xl text-white shadow-lg shadow-primary-100">
              <TrendingUp size={20} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 leading-tight">{t("mandi.title")}</h2>
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-1">
            {t("mandi.liveRates", { crop: tCrop(selectedCrop) || selectedCrop || "-" })}
          </p>
          <div className="mt-3 rounded-2xl border border-slate-200 bg-white p-3">
            <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block mb-2">
              {t("onboarding.cropName")}
            </label>
            <select
              className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm font-semibold rounded-xl px-3 py-2"
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
            >
              <option value="">{t("onboarding.selectCrop")}</option>
              {cropOptions.map((crop) => (
                <option key={crop} value={crop}>
                  {tCrop(crop) || crop}
                </option>
              ))}
            </select>
          </div>
        </section>

        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-white rounded-[2rem] p-6 shadow-xl shadow-slate-200 border border-slate-100 relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary-50 rounded-full -mr-16 -mt-16 blur-3xl opacity-50" />

          <div className="flex justify-between items-start mb-8 relative z-10">
            <div>
              <p className="text-slate-400 text-[10px] font-bold uppercase tracking-[0.2em] mb-2">
                {t("mandi.bestMarket")}
              </p>
              <div className="flex items-center gap-2 text-slate-900">
                <MapPin className="w-5 h-5 text-primary-600" />
                <h3 className="text-2xl font-bold">{loading ? t("mandi.searching") : data?.best_mandi}</h3>
              </div>
            </div>
            <div className="bg-primary-600 text-white px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider shadow-md">
              {loading ? "..." : Math.round((data?.confidence_score || 0) * 100)}% {t("mandi.match")}
            </div>
          </div>

          <div className="flex items-baseline gap-2 mb-8 relative z-10">
            <span className="text-5xl font-bold text-slate-900 tracking-tighter">
              INR {loading ? "---" : data?.net_price}
            </span>
            <span className="text-slate-400 font-semibold text-sm uppercase tracking-widest">
              {t("mandi.perQuintal")}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 relative z-10">
            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">
                {t("mandi.trend7d")}
              </p>
              <div className="flex items-center gap-1 font-bold text-primary-600">
                <ArrowUpRight className="w-4 h-4" />
                {data?.trend_7d || "N/A"}
              </div>
            </div>
            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">
                {t("mandi.forecast")}
              </p>
              <p className="font-bold text-slate-700">{data?.forecast_band || "N/A"}</p>
            </div>
          </div>
        </motion.div>

        <section className="space-y-4 px-1">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-widest">
              {t("mandi.nearbyMarkets")}
            </h3>
            {!showAllMarkets && data?.all_markets?.length > 2 && (
              <button
                onClick={() => setShowAllMarkets(true)}
                className="text-[10px] font-bold text-primary-600 uppercase tracking-widest"
              >
                {t("mandi.seeAll")}
              </button>
            )}
          </div>

          {noData && (
            <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 text-sm font-semibold text-amber-800">
              Data not available for the selected crop.
            </div>
          )}

          {!noData &&
            (showAllMarkets ? data?.all_markets : data?.all_markets?.slice(0, 2) || []).map(
              (m: any, i: number) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  whileTap={{ scale: 0.98 }}
                  className="bg-white p-4 rounded-2xl flex justify-between items-center shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 border border-slate-100">
                      <MapPin className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="font-bold text-slate-800 text-sm leading-tight">{m.Market || m.name}</p>
                      <p className="text-[10px] font-medium text-slate-400 mt-0.5">{m.District || m.dist}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-primary-600 text-lg tracking-tight">INR {m.Modal_Price || m.price}</p>
                  </div>
                </motion.div>
              )
            )}

          {showAllMarkets && !noData && (
            <button
              onClick={() => setShowAllMarkets(false)}
              className="w-full py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest hover:text-primary-600 transition-colors"
            >
              Show Less
            </button>
          )}
        </section>

        <div className="bg-slate-900 rounded-[1.5rem] p-5 flex gap-4 shadow-xl shadow-slate-200">
          <div className="bg-white/10 p-3 rounded-xl shrink-0">
            <Info className="w-6 h-6 text-primary-400" />
          </div>
          <p className="text-xs font-medium text-slate-300 leading-relaxed">
            {t("mandi.tip", { crop: tCrop(selectedCrop) || selectedCrop || "-" })}
          </p>
        </div>
      </div>
    </Layout>
  );
}
