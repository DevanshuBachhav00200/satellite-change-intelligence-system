import React from 'react';
import { Download, FileImage, Layers } from 'lucide-react';

export default function DownloadBar({ result, sampleName }) {
  if (!result || !result.prediction_mask || !result.analysis_visualization) return null;

  const handleDownload = (dataUri, filename) => {
    const link = document.createElement('a');
    link.href = dataUri;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const nameTag = sampleName ? sampleName.replace('.png', '') : 'custom_pair';

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-8 shadow-card flex flex-wrap items-center justify-between gap-4">
      <div>
        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <Download className="w-4 h-4 text-blue-600" />
          Export &amp; Download Artifacts
        </h4>
        <p className="text-xs text-slate-500 mt-0.5">
          Download high-resolution binary prediction mask and annotated analysis visualization figures.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <button
          onClick={() => handleDownload(result.prediction_mask, `predict_mask_${nameTag}.png`)}
          className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-bold transition-all border border-slate-200 shadow-subtle"
        >
          <FileImage className="w-4 h-4 text-slate-600" />
          Download Prediction Mask (.png)
        </button>

        <button
          onClick={() => handleDownload(result.analysis_visualization, `vis_analysis_${nameTag}.png`)}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-blue-500/20"
        >
          <Layers className="w-4 h-4 text-white" />
          Download Analysis Visualization (.png)
        </button>
      </div>
    </div>
  );
}
