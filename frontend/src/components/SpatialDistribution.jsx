import React from 'react';
import { MapPin, Grid, Layers } from 'lucide-react';

export default function SpatialDistribution({ visualizationBase64, gridDensityStats }) {
  if (!visualizationBase64) return null;

  const gridMatrix = gridDensityStats?.grid || [];
  const maxDensity = gridDensityStats?.max || 0;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-8 shadow-card">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-600" />
            Spatial Change Distribution &amp; Density Analysis
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Annotated region detection, spatial centroids, and 4x4 spatial grid density matrix.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Annotated Change Visualization Image */}
        <div className="lg:col-span-8 bg-slate-50/70 rounded-xl border border-slate-200 p-4 flex flex-col items-center">
          <span className="text-xs font-bold text-slate-700 mb-3 flex items-center gap-1.5 self-start">
            <Layers className="w-4 h-4 text-blue-600" />
            Annotated Regions, Centroids &amp; Spatial Heatmap
          </span>
          <img
            src={visualizationBase64}
            alt="Annotated Spatial Change Analysis"
            className="w-full h-auto rounded-lg border border-slate-200 shadow-subtle object-contain max-h-[420px]"
          />
        </div>

        {/* 4x4 Spatial Density Grid Matrix */}
        <div className="lg:col-span-4 bg-slate-50/70 rounded-xl border border-slate-200 p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                <Grid className="w-4 h-4 text-indigo-600" />
                4×4 Spatial Cell Density (%)
              </span>
              <span className="text-[11px] font-semibold text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                Max: {maxDensity.toFixed(1)}%
              </span>
            </div>

            <p className="text-xs text-slate-500 mb-4 leading-relaxed">
              Spatial breakdown of change density percentage across 16 uniform grid cells.
            </p>

            {gridMatrix.length > 0 ? (
              <div className="grid grid-cols-4 gap-2 bg-slate-200/60 p-2 rounded-xl border border-slate-300/60">
                {gridMatrix.map((row, rIdx) =>
                  row.map((val, cIdx) => {
                    const intensity = Math.min(100, Math.max(0, val));
                    // Heatmap color calculation
                    const bgStyle =
                      intensity === 0
                        ? 'bg-white text-slate-400'
                        : intensity < 15
                        ? 'bg-blue-100 text-blue-900 font-semibold'
                        : intensity < 35
                        ? 'bg-indigo-200 text-indigo-950 font-bold'
                        : 'bg-indigo-600 text-white font-extrabold shadow-sm';

                    return (
                      <div
                        key={`${rIdx}-${cIdx}`}
                        className={`h-12 rounded-lg flex flex-col items-center justify-center text-xs transition-all ${bgStyle}`}
                        title={`Cell (${rIdx+1}, ${cIdx+1}): ${val.toFixed(2)}% change`}
                      >
                        <span className="text-[11px]">{val.toFixed(1)}%</span>
                      </div>
                    );
                  })
                )}
              </div>
            ) : (
              <div className="text-xs text-slate-400 text-center py-6">No grid statistics</div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-500 flex justify-between">
            <span>Cell dimensions: 64×64 px</span>
            <span>Scale: 0.0% – 100.0%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
