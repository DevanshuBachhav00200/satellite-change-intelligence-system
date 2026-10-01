import React from 'react';
import { Satellite, Cpu, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function Header({ healthStatus }) {
  const isGpu = healthStatus?.device?.startsWith('cuda');
  const isHealthy = healthStatus?.status === 'healthy';

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-subtle">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4">
        {/* Left Branding */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Satellite className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">
                Satellite Change Intelligence
              </span>
              <span className="px-2 py-0.5 text-xs font-semibold bg-blue-50 text-blue-700 rounded-md border border-blue-200/60">
                SCI
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">
              Temporal Satellite Change Detection &amp; Explainable Impact Assessment
            </p>
          </div>
        </div>

        {/* Right System Indicators */}
        <div className="flex items-center gap-3">
          {/* Model Spec Badge */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100/80 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700">
            <span className="text-slate-400">Model:</span>
            <span className="text-blue-700 font-bold">ChangeFormerV6</span>
          </div>

          {/* Hardware Engine Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-100/80 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700">
            <Cpu className="w-3.5 h-3.5 text-slate-500" />
            <span>{isGpu ? 'GPU Accelerated (CUDA)' : 'CPU Mode'}</span>
            <span className="relative flex h-2 w-2">
              <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isHealthy ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
              <span className={`relative inline-flex rounded-full h-2 w-2 ${isHealthy ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
            </span>
          </div>

          {/* Backend Health Indicator */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${isHealthy ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
            {isHealthy ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Backend Ready</span>
              </>
            ) : (
              <>
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span>Backend Offline</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
