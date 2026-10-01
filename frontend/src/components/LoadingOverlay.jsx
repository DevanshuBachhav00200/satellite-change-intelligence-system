import React, { useEffect, useState } from 'react';
import { RefreshCw, CheckCircle2, Loader2, Sparkles } from 'lucide-react';

export default function LoadingOverlay() {
  const [activeStep, setActiveStep] = useState(0);

  const steps = [
    'Loading bitemporal image pair',
    'Executing ChangeFormerV6 inference',
    'Computing spatial change & connected components',
    'Calculating Change Impact Index (CII)',
    'Preparing visual maps & structured response'
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 400);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-md flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-8 shadow-2xl border border-slate-100 relative overflow-hidden text-center">
        {/* Top Accent bar */}
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-teal-500"></div>

        <div className="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4 shadow-sm">
          <RefreshCw className="w-8 h-8 animate-spin" />
        </div>

        <h3 className="text-xl font-bold text-slate-900 tracking-tight mb-1">
          Analyzing Satellite Imagery...
        </h3>
        <p className="text-xs text-slate-500 mb-6 font-medium">
          Deep learning pipeline running GPU inference &amp; explainable spatial analysis.
        </p>

        {/* Multi-stage step checklist */}
        <div className="space-y-3 text-left bg-slate-50 p-4 rounded-xl border border-slate-200/80 mb-2">
          {steps.map((stepText, idx) => {
            const isCompleted = idx < activeStep;
            const isCurrent = idx === activeStep;

            return (
              <div key={idx} className="flex items-center gap-3 text-xs">
                {isCompleted ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-blue-600 animate-spin flex-shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-300 flex-shrink-0"></div>
                )}
                <span
                  className={`font-semibold ${
                    isCompleted
                      ? 'text-slate-700'
                      : isCurrent
                      ? 'text-blue-700 font-bold'
                      : 'text-slate-400'
                  }`}
                >
                  {stepText}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
