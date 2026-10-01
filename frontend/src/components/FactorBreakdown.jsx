import React from 'react';
import { BarChart2, Layers, Target, Maximize } from 'lucide-react';

export default function FactorBreakdown({ factorContributions }) {
  if (!factorContributions) return null;

  const { extent_pct = 0, concentration_pct = 0, scale_pct = 0 } = factorContributions;

  const factors = [
    {
      title: 'Extent',
      weight: 'W = 0.40',
      pct: extent_pct,
      desc: 'Overall spatial coverage of detected change across the bitemporal scene.',
      icon: Layers,
      color: 'bg-blue-600',
      barBg: 'bg-blue-50'
    },
    {
      title: 'Concentration',
      weight: 'W = 0.35',
      pct: concentration_pct,
      desc: 'Local density and clustering severity of detected change regions.',
      icon: Target,
      color: 'bg-indigo-600',
      barBg: 'bg-indigo-50'
    },
    {
      title: 'Scale',
      weight: 'W = 0.25',
      pct: scale_pct,
      desc: 'Structural footprint and area scale of the largest connected changed region.',
      icon: Maximize,
      color: 'bg-teal-600',
      barBg: 'bg-teal-50'
    }
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-8 shadow-card">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-blue-600" />
            CII Factor Contribution Breakdown
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Normalized percentage breakdown of the three non-redundant feature dimensions.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {factors.map((f, idx) => {
          const IconComponent = f.icon;
          return (
            <div
              key={idx}
              className="bg-slate-50/70 rounded-xl border border-slate-200 p-5 flex flex-col justify-between hover:border-slate-300 transition-all"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-7 h-7 rounded-lg ${f.barBg} text-slate-800 flex items-center justify-center`}>
                      <IconComponent className="w-4 h-4" />
                    </div>
                    <span className="text-sm font-bold text-slate-900">{f.title}</span>
                  </div>
                  <span className="text-[11px] font-bold text-slate-400 bg-white px-2 py-0.5 rounded border border-slate-200">
                    {f.weight}
                  </span>
                </div>

                <div className="flex items-baseline justify-between mb-2">
                  <span className="text-2xl font-extrabold text-slate-900">{f.pct.toFixed(2)}%</span>
                  <span className="text-xs font-medium text-slate-500">Contribution</span>
                </div>

                <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden mb-3">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${f.color}`}
                    style={{ width: `${Math.min(100, Math.max(0, f.pct))}%` }}
                  ></div>
                </div>

                <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
