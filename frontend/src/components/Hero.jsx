import React from 'react';
import { Layers, ShieldCheck, Sparkles } from 'lucide-react';

export default function Hero() {
  return (
    <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 sm:p-8 mb-8 shadow-card relative overflow-hidden">
      {/* Decorative subtle background grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff0a_1px,transparent_1px),linear-gradient(to_bottom,#ffffff0a_1px,transparent_1px)] bg-[size:24px_24px]"></div>
      
      <div className="relative z-10 max-w-4xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-xs font-semibold text-blue-200 border border-white/15 mb-3">
          <Sparkles className="w-3.5 h-3.5 text-blue-300" />
          <span>Final Year Deep Learning Research Project</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mb-2">
          Detect • Analyze • Explain
        </h1>

        <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl font-normal">
          AI-powered bi-temporal satellite image change detection with explainable spatial impact assessment using CNN–Transformer architectures and the Change Impact Index (CII).
        </p>

        <div className="flex flex-wrap items-center gap-4 mt-5 text-xs text-slate-300 font-medium">
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
            <Layers className="w-3.5 h-3.5 text-blue-400" />
            <span>Benchmark Dataset: LEVIR-CD256</span>
          </div>
          <div className="flex items-center gap-1.5 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Verified Intelligence Pipeline</span>
          </div>
        </div>
      </div>
    </div>
  );
}
