import React from 'react';
import { Activity, Compass, Info } from 'lucide-react';

export default function CIIGaugeCard({ ciiScore, impactCategory, primaryDriver }) {
  if (ciiScore === undefined || ciiScore === null) return null;

  const scorePct = Math.min(100, Math.max(0, ciiScore));

  let badgeStyle = {
    bg: 'bg-emerald-50',
    text: 'text-emerald-800',
    border: 'border-emerald-200',
    progress: 'bg-emerald-500'
  };

  if (impactCategory === 'Moderate Impact') {
    badgeStyle = {
      bg: 'bg-amber-50',
      text: 'text-amber-800',
      border: 'border-amber-200',
      progress: 'bg-amber-500'
    };
  } else if (impactCategory === 'High Impact') {
    badgeStyle = {
      bg: 'bg-rose-50',
      text: 'text-rose-800',
      border: 'border-rose-200',
      progress: 'bg-rose-500'
    };
  } else if (impactCategory === 'Zero Impact') {
    badgeStyle = {
      bg: 'bg-slate-50',
      text: 'text-slate-700',
      border: 'border-slate-200',
      progress: 'bg-slate-400'
    };
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-8 shadow-card">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Change Impact Index (CII) Assessment
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Composite explainable index $S \in [0, 100]$ evaluating spatial extent, local concentration, and structural scale.
          </p>
        </div>

        <div className={`px-3 py-1 rounded-full text-xs font-bold border ${badgeStyle.bg} ${badgeStyle.text} ${badgeStyle.border}`}>
          {impactCategory}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
        {/* Score Display */}
        <div className="flex flex-col items-center justify-center p-6 bg-slate-50 rounded-xl border border-slate-200/80">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
            Composite CII Score
          </span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight">
              {ciiScore.toFixed(2)}
            </span>
            <span className="text-sm font-bold text-slate-400">/ 100</span>
          </div>
          <span className="text-[11px] font-medium text-slate-500 mt-2">
            Empirical Threshold: 0–30 (Low), 30–55 (Mod), &gt;55 (High)
          </span>
        </div>

        {/* Progress Gauge & Primary Driver */}
        <div className="lg:col-span-2 space-y-5">
          {/* Horizontal Gauge Bar */}
          <div>
            <div className="flex justify-between items-center text-xs font-bold text-slate-700 mb-2">
              <span>0 (Zero)</span>
              <span>30 (Low)</span>
              <span>55 (Moderate)</span>
              <span>100 (High)</span>
            </div>
            <div className="w-full bg-slate-100 h-4 rounded-full overflow-hidden p-0.5 border border-slate-200 relative">
              {/* Threshold lines */}
              <div className="absolute left-[30%] top-0 bottom-0 w-0.5 bg-slate-300 z-10"></div>
              <div className="absolute left-[55%] top-0 bottom-0 w-0.5 bg-slate-300 z-10"></div>
              
              <div
                className={`h-full rounded-full transition-all duration-700 ease-out ${badgeStyle.progress}`}
                style={{ width: `${scorePct}%` }}
              ></div>
            </div>
          </div>

          {/* Primary Driver */}
          <div className="bg-blue-50/50 rounded-xl border border-blue-100 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                <Compass className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs text-slate-500 font-semibold block">Primary Impact Driver</span>
                <span className="text-sm font-bold text-slate-900">{primaryDriver}</span>
              </div>
            </div>
            <div className="hidden sm:flex items-center gap-1 text-xs text-blue-700 font-medium bg-white px-2.5 py-1 rounded-md border border-blue-200">
              <Info className="w-3.5 h-3.5" /> Dominant Factor
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
