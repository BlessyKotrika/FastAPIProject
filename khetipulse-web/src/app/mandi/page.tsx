"use client";
import React, { useState, useEffect, useMemo } from 'react';
import { useAppStore } from '@/lib/store';
import { useTranslation } from '@/lib/i18n';
import { sellSmartService } from '@/services/api';
import Layout from '@/components/Layout';
import { TrendingUp, MapPin, Info, ArrowUpRight, RefreshCw, Search, Calculator } from 'lucide-react';
import { motion } from 'framer-motion';

const DEFAULT_CROPS = ["Wheat", "Rice", "Cotton", "Maize", "Soybean", "Chana", "Groundnut", "Mustard"];

const INDIAN_STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
  "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
  "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
  "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
  "Uttarakhand","West Bengal"
];

const YIELD_QTL_PER_ACRE: Record<string, number> = {
  Wheat: 18,
  Rice: 20,
  Cotton: 8,
  Maize: 22,
  Soybean: 10,
  Chana: 7,
  Groundnut: 9,
  Mustard: 6,
};

const safeNumber = (v: any) => {
  const n = parseFloat(String(v ?? "").replace(/[^\d.]/g, ""));
  return Number.isFinite(n) ? n : 0;
};

export default function MandiPage() {
  const { profile } = useAppStore();
  const { t } = useTranslation();

  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [showAllMarkets, setShowAllMarkets] = useState(false);

  // Top search (for main mandi insights)
  const [searchInput, setSearchInput] = useState(profile.location || '');
  const [selectedLocation, setSelectedLocation] = useState(profile.location || 'Barabanki');

  // Calculator controls
  const [selectedCrop, setSelectedCrop] = useState(profile.crop || "Wheat");
  const [areaAcres, setAreaAcres] = useState<number>(profile.land_size > 0 ? profile.land_size : 2);
  const [calcState, setCalcState] = useState(profile.state || "");
  const [selectedMarketKey, setSelectedMarketKey] = useState<string>("");

  const cropOptions = useMemo(() => {
    const set = new Set(DEFAULT_CROPS);
    if (profile.crop) set.add(profile.crop);
    return Array.from(set);
  }, [profile.crop]);

  const allMarkets = useMemo(() => data?.all_markets || [], [data]);

  // ONLY for calculator
  const calculatorMarkets = useMemo(() => {
    if (!calcState) return allMarkets;
    return allMarkets.filter((m: any) => {
      const s = (m?.State || m?.state || "").toString().trim().toLowerCase();
      return s === calcState.toLowerCase();
    });
  }, [allMarkets, calcState]);

  useEffect(() => {
    const initialLocation = profile.location || 'Barabanki';
    const initialCrop = profile.crop || "Wheat";
    setSearchInput(initialLocation);
    setSelectedLocation(initialLocation);
    setSelectedCrop(initialCrop);
    setCalcState(profile.state || "");
    fetchMandi(initialLocation, initialCrop);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile.language]);

  useEffect(() => {
    const source = calculatorMarkets.length > 0 ? calculatorMarkets : allMarkets;
    if (source.length > 0) {
      const first = source[0];
      const key = `${first?.Market || first?.name || "Unknown"}|${first?.District || first?.dist || ""}`;
      setSelectedMarketKey(key);
    } else {
      setSelectedMarketKey("");
    }
  }, [calculatorMarkets, allMarkets]);

  const fetchMandi = async (locationOverride?: string, cropOverride?: string) => {
    const locationToUse = (locationOverride || selectedLocation || profile.location || 'Barabanki').trim();
    const cropToUse = (cropOverride || selectedCrop || profile.crop || 'Wheat').trim();

    try {
      setLoading(true);
      setErrorMsg(null);

      // Main insights are based on location search (+ optional profile.state)
      const res = await sellSmartService.getMandiData({
        crop: cropToUse,
        location: locationToUse,
        state: profile.state || '',
        language: profile.language,
      });

      setData(res);
    } catch (err: any) {
      setErrorMsg(err?.message || "Couldn’t fetch live mandi prices. Please refresh.");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    const q = searchInput.trim();
    if (!q) return;
    setSelectedLocation(q);
    setShowAllMarkets(false);
    fetchMandi(q, selectedCrop);
  };

  const handleCropChange = (crop: string) => {
    setSelectedCrop(crop);
    fetchMandi(selectedLocation, crop);
  };

  const selectedMarket = useMemo(() => {
    const source = calculatorMarkets.length > 0 ? calculatorMarkets : allMarkets;
    if (!source.length || !selectedMarketKey) return null;
    return source.find((m: any) => {
      const key = `${m?.Market || m?.name || "Unknown"}|${m?.District || m?.dist || ""}`;
      return key === selectedMarketKey;
    }) || null;
  }, [calculatorMarkets, allMarkets, selectedMarketKey]);

  const selectedMarketPrice = useMemo(() => {
    if (!selectedMarket) return safeNumber(data?.net_price);
    return safeNumber(selectedMarket?.Modal_Price ?? selectedMarket?.price);
  }, [selectedMarket, data?.net_price]);

  const yieldPerAcre = YIELD_QTL_PER_ACRE[selectedCrop] || 10;
  const estimatedProductionQtl = +(areaAcres * yieldPerAcre).toFixed(2);
  const estimatedGrossValue = Math.round(estimatedProductionQtl * selectedMarketPrice);

  return (
    <Layout>
      <div className="p-4 space-y-6">
        {/* Header */}
        <section className="px-1">
          <div className="flex items-center gap-3 justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-primary-600 p-2 rounded-xl text-white shadow-lg shadow-primary-100">
                <TrendingUp size={20} />
              </div>
              <h2 className="text-2xl font-bold text-slate-900 leading-tight">{t('mandi.title')}</h2>
            </div>

            <button
              onClick={() => fetchMandi(selectedLocation, selectedCrop)}
              disabled={loading}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-bold text-slate-700 bg-white disabled:opacity-60"
            >
              <RefreshCw size={14} />
              Refresh
            </button>
          </div>

          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-1">
            {t('mandi.liveRates', { crop: t(`onboarding.crops.${selectedCrop}`) || selectedCrop })}
          </p>
        </section>

        {/* Search */}
        <section className="px-1">
          <div className="bg-white rounded-2xl p-2 border border-slate-200 shadow-sm flex items-center gap-2">
            <Search className="w-4 h-4 text-slate-400 ml-2" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search mandi by district/city..."
              className="flex-1 bg-transparent px-2 py-2 text-sm font-semibold text-slate-800 placeholder:text-slate-400 focus:outline-none"
            />
            <button
              onClick={handleSearch}
              disabled={loading || !searchInput.trim()}
              className="bg-primary-600 text-white px-4 py-2 rounded-xl text-xs font-bold disabled:opacity-50"
            >
              Search
            </button>
          </div>
          <p className="text-[11px] text-slate-500 mt-2">
            Showing results for: <span className="font-bold text-slate-700">{selectedLocation}</span>
          </p>
        </section>

        {/* Error state */}
        {!loading && errorMsg && (
          <div className="bg-white rounded-2xl p-5 border border-rose-200 shadow-sm">
            <p className="text-sm font-semibold text-rose-600">{errorMsg}</p>
            <button
              onClick={() => fetchMandi(selectedLocation, selectedCrop)}
              className="mt-3 inline-flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-xl text-sm font-bold"
            >
              <RefreshCw size={16} />
              Refresh
            </button>
          </div>
        )}

        {/* Price Card */}
        {!errorMsg && (
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-[2rem] p-6 shadow-xl shadow-slate-200 border border-slate-100 relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary-50 rounded-full -mr-16 -mt-16 blur-3xl opacity-50"></div>

            <div className="flex justify-between items-start mb-8 relative z-10">
              <div>
                <p className="text-slate-400 text-[10px] font-bold uppercase tracking-[0.2em] mb-2">{t('mandi.bestMarket')}</p>
                <div className="flex items-center gap-2 text-slate-900">
                  <MapPin className="w-5 h-5 text-primary-600" />
                  <h3 className="text-2xl font-bold">{loading ? t('mandi.searching') : (data?.best_mandi || "--")}</h3>
                </div>
              </div>
              <div className="bg-primary-600 text-white px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider shadow-md">
                {loading ? '...' : `${Math.round((data?.confidence_score || 0) * 100)}% ${t('mandi.match')}`}
              </div>
            </div>

            <div className="flex items-baseline gap-2 mb-8 relative z-10">
              <span className="text-5xl font-bold text-slate-900 tracking-tighter">
                ₹{loading ? '---' : (data?.net_price ?? '--')}
              </span>
              <span className="text-slate-400 font-semibold text-sm uppercase tracking-widest">{t('mandi.perQuintal')}</span>
            </div>

            <div className="grid grid-cols-2 gap-4 relative z-10">
              <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">{t('mandi.trend7d')}</p>
                <div className="flex items-center gap-1 font-bold text-primary-600">
                  <ArrowUpRight className="w-4 h-4" />
                  {data?.trend_7d || '--'}
                </div>
              </div>
              <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">{t('mandi.forecast')}</p>
                <p className="font-bold text-slate-700">{data?.forecast_band || '--'}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Nearby Markets (main section unaffected by calculator state) */}
        {!errorMsg && (
          <section className="space-y-4 px-1">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-bold text-slate-800 uppercase tracking-widest">{t('mandi.nearbyMarkets')}</h3>
              {!showAllMarkets && (allMarkets?.length || 0) > 2 && (
                <button
                  onClick={() => setShowAllMarkets(true)}
                  className="text-[10px] font-bold text-primary-600 uppercase tracking-widest"
                >
                  {t('mandi.seeAll')}
                </button>
              )}
            </div>

            {(showAllMarkets ? allMarkets : allMarkets.slice(0, 2)).map((m: any, i: number) => (
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
                    <p className="font-bold text-slate-800 text-sm leading-tight">{m.Market || m.name || '--'}</p>
                    <p className="text-[10px] font-medium text-slate-400 mt-0.5">
                      {m.District || m.dist || '--'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-bold text-primary-600 text-lg tracking-tight">₹{m.Modal_Price || m.price || '--'}</p>
                </div>
              </motion.div>
            ))}

            {showAllMarkets && (
              <button
                onClick={() => setShowAllMarkets(false)}
                className="w-full py-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest hover:text-primary-600 transition-colors"
              >
                Show Less
              </button>
            )}
          </section>
        )}

        {/* Estimated Sale Calculator */}
        {!errorMsg && (
          <section className="bg-white rounded-[1.8rem] p-5 border border-slate-100 shadow-lg space-y-5">
            <div className="flex items-center gap-2">
              <div className="bg-primary-50 text-primary-700 p-2 rounded-xl">
                <Calculator size={18} />
              </div>
              <h3 className="text-base font-bold text-slate-900">Estimated Sale Calculator</h3>
            </div>

            <div className="grid grid-cols-1 gap-3">
              <div>
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">State (Calculator)</label>
                <select
                  value={calcState}
                  onChange={(e) => setCalcState(e.target.value)}
                  className="mt-1 w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm font-semibold text-slate-800"
                >
                  <option value="">All States</option>
                  {INDIAN_STATES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Crop</label>
                <select
                  value={selectedCrop}
                  onChange={(e) => handleCropChange(e.target.value)}
                  className="mt-1 w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm font-semibold text-slate-800"
                >
                  {cropOptions.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Select Mandi</label>
                <select
                  value={selectedMarketKey}
                  onChange={(e) => setSelectedMarketKey(e.target.value)}
                  className="mt-1 w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-sm font-semibold text-slate-800"
                >
                  {(calculatorMarkets.length > 0 ? calculatorMarkets : allMarkets).map((m: any, idx: number) => {
                    const marketName = m?.Market || m?.name || "Unknown";
                    const district = m?.District || m?.dist || "";
                    const price = m?.Modal_Price || m?.price || "--";
                    const state = m?.State || m?.state || "";
                    const key = `${marketName}|${district}`;
                    return (
                      <option key={`${key}-${idx}`} value={key}>
                        {marketName} {district ? `(${district})` : ""} {state ? `- ${state}` : ""} - ₹{price}
                      </option>
                    );
                  })}
                </select>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Area of Land</label>
                <p className="text-sm font-bold text-slate-800">{areaAcres} acres</p>
              </div>
              <input
                type="range"
                min={1}
                max={50}
                step={0.5}
                value={areaAcres}
                onChange={(e) => setAreaAcres(parseFloat(e.target.value))}
                className="w-full mt-2 accent-primary-600"
              />
            </div>

            <div className="grid grid-cols-1 gap-3">
              <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100 flex justify-between">
                <span className="text-sm font-semibold text-slate-600">Estimated yield</span>
                <span className="text-sm font-bold text-slate-900">{estimatedProductionQtl} quintals</span>
              </div>

              <div className="bg-primary-50 rounded-2xl p-4 border border-primary-100 flex justify-between">
                <span className="text-sm font-semibold text-primary-700">Estimated gross value</span>
                <span className="text-lg font-extrabold text-primary-800">₹{estimatedGrossValue.toLocaleString('en-IN')}</span>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 leading-relaxed">
              * Estimate = Area (acres) × assumed crop yield (qtl/acre) × selected mandi modal price.
              Actual output depends on weather, variety, irrigation, and farm practices.
            </p>
          </section>
        )}

        {/* Tip */}
        <div className="bg-slate-900 rounded-[1.5rem] p-5 flex gap-4 shadow-xl shadow-slate-200">
          <div className="bg-white/10 p-3 rounded-xl shrink-0">
            <Info className="w-6 h-6 text-primary-400" />
          </div>
          <p className="text-xs font-medium text-slate-300 leading-relaxed">
            {t('mandi.tip', { crop: t(`onboarding.crops.${selectedCrop}`) || selectedCrop })}
          </p>
        </div>
      </div>
    </Layout>
  );
}