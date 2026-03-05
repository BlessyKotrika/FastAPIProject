"use client";
import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/lib/store';
import { sellSmartService } from '@/services/api';
import Layout from '@/components/Layout';
import { TrendingUp, MapPin, Info, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';
import { motion } from 'framer-motion';

export default function MandiPage() {
  const { profile } = useAppStore();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMandi();
  }, [profile]);

  const fetchMandi = async () => {
    try {
      setLoading(true);
      const res = await sellSmartService.getMandiData({
        crop: profile.crop || 'Wheat',
        location: profile.location || 'Barabanki',
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
              <TrendingUp size={20} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 leading-tight">Mandi Insights</h2>
          </div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mt-1">Live rates for {profile.crop}</p>
        </section>

        {/* Price Card */}
        <motion.div 
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="bg-white rounded-[2rem] p-6 shadow-xl shadow-slate-200 border border-slate-100 relative overflow-hidden"
        >
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary-50 rounded-full -mr-16 -mt-16 blur-3xl opacity-50"></div>
          
          <div className="flex justify-between items-start mb-8 relative z-10">
            <div>
              <p className="text-slate-400 text-[10px] font-bold uppercase tracking-[0.2em] mb-2">Best Market</p>
              <div className="flex items-center gap-2 text-slate-900">
                <MapPin className="w-5 h-5 text-primary-600" />
                <h3 className="text-2xl font-bold">{loading ? 'Searching...' : data?.best_mandi}</h3>
              </div>
            </div>
            <div className="bg-primary-600 text-white px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider shadow-md">
              {loading ? '...' : Math.round(data?.confidence_score * 100)}% Match
            </div>
          </div>

          <div className="flex items-baseline gap-2 mb-8 relative z-10">
            <span className="text-5xl font-bold text-slate-900 tracking-tighter">₹{loading ? '---' : data?.net_price}</span>
            <span className="text-slate-400 font-semibold text-sm uppercase tracking-widest">/ quintal</span>
          </div>

          <div className="grid grid-cols-2 gap-4 relative z-10">
            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">7D Trend</p>
              <div className="flex items-center gap-1 font-bold text-primary-600">
                <ArrowUpRight className="w-4 h-4" />
                {data?.trend_7d || 'Stable'}
              </div>
            </div>
            <div className="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Forecast</p>
              <p className="font-bold text-slate-700">{data?.forecast_band || '---'}</p>
            </div>
          </div>
        </motion.div>

        {/* Nearby Markets List */}
        <section className="space-y-4 px-1">
          <div className="flex justify-between items-center">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-widest">Nearby Markets</h3>
            <button className="text-[10px] font-bold text-primary-600 uppercase tracking-widest">See All</button>
          </div>
          {[
            { name: 'Lucknow Central', dist: '22 km', price: '₹2410' },
            { name: 'Haidergarh Mandi', dist: '35 km', price: '₹2380' }
          ].map((m, i) => (
            <motion.div 
              key={i} 
              whileTap={{ scale: 0.98 }}
              className="bg-white p-4 rounded-2xl flex justify-between items-center shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 border border-slate-100">
                  <MapPin className="w-5 h-5" />
                </div>
                <div>
                  <p className="font-bold text-slate-800 text-sm leading-tight">{m.name}</p>
                  <p className="text-[10px] font-medium text-slate-400 mt-0.5">{m.dist} away</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-primary-600 text-lg tracking-tight">{m.price}</p>
              </div>
            </motion.div>
          ))}
        </section>

        {/* Recommendation Tip */}
        <div className="bg-slate-900 rounded-[1.5rem] p-5 flex gap-4 shadow-xl shadow-slate-200">
          <div className="bg-white/10 p-3 rounded-xl shrink-0">
            <Info className="w-6 h-6 text-primary-400" />
          </div>
          <p className="text-xs font-medium text-slate-300 leading-relaxed">
            Prices are rising in neighboring districts. Consider holding your {profile.crop} for 3 more days to maximize profit.
          </p>
        </div>
      </div>
    </Layout>
  );
}
