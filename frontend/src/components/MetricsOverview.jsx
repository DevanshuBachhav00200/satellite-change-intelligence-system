import React from 'react';
import { Percent, Hash, Grid, Activity } from 'lucide-react';

export default function MetricsOverview({ result }) {
  if (!result) return null;

  const {
    change_percentage,
    changed_pixel_count,
    total_pixel_count,
    connected_region_count,
    largest_region_area,
    cii_score,
    impact_category
  } = result;

  let badgeColor = "bg-slate-100 text-slate-700 border-slate-200";
  if (impact_category === "Low Impact") badgeColor = "bg-emerald-50 text-emerald-800 border-emerald-200";
  else if (impact_category === "Moderate Impact") badgeColor = "bg-amber-50 text-amber-800 border-amber-200";
  else if (impact_category === "High Impact") badgeColor = "bg-rose-50 text-rose-800 border-rose-200";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
      {/* 1. Changed Area */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-card shadow-card-hover">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Changed Area
          </span>
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <Percent className="w-4 h-4" />
          </div>
        </div>
        <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
          {change_percentage.toFixed(2)}%
        </div>
        <p className="text-xs text-slate-500 mt-1 font-medium">
          Spatial coverage of image
        </p>
      </div>

      {/* 2. Changed Pixels */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-card shadow-card-hover">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Changed Pixels
          </span>
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <Hash className="w-4 h-4" />
          </div>
        </div>
        <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
          {changed_pixel_count.toLocaleString()}
        </div>
        <p className="text-xs text-slate-500 mt-1 font-medium">
          out of {total_pixel_count.toLocaleString()} total px
        </p>
      </div>

      {/* 3. Changed Regions */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-card shadow-card-hover">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Changed Regions
          </span>
          <div className="w-8 h-8 rounded-lg bg-teal-50 text-teal-600 flex items-center justify-center">
            <Grid className="w-4 h-4" />
          </div>
        </div>
        <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
          {connected_region_count}
        </div>
        <p className="text-xs text-slate-500 mt-1 font-medium">
          Largest: {Math.round(largest_region_area)} px
        </p>
      </div>

      {/* 4. CII Score */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-card shadow-card-hover relative overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            CII Score
          </span>
          <div className="w-8 h-8 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center">
            <Activity className="w-4 h-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <div className="text-3xl font-extrabold text-slate-900 tracking-tight">
            {cii_score.toFixed(2)}
          </div>
          <span className="text-xs font-bold text-slate-400">/ 100</span>
        </div>
        <div className="mt-1.5">
          <span className={`inline-block text-[11px] font-bold px-2 py-0.5 rounded-full border ${badgeColor}`}>
            {impact_category}
          </span>
        </div>
      </div>
    </div>
  );
}
