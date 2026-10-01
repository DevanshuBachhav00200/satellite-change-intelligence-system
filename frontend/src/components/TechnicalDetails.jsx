import React, { useState } from 'react';
import { Cpu, ChevronDown, ChevronUp, Code2, Server, Database, Image as ImageIcon } from 'lucide-react';

export default function TechnicalDetails() {
  const [isOpen, setIsOpen] = useState(false);

  const specs = [
    { label: 'Model Architecture', value: 'ChangeFormerV6 (CNN + Transformer Hybrid)' },
    { label: 'Pretrained Checkpoint', value: 'ChangeFormer_LEVIR (best_ckpt.pt)' },
    { label: 'Benchmark Dataset', value: 'LEVIR-CD256 (Bitemporal Building Change Detection)' },
    { label: 'Input Modality', value: 'Bi-temporal Optical Satellite Imagery (T1, T2)' },
    { label: 'Image Resolution', value: '256 × 256 pixels (3-channel RGB)' },
    { label: 'Hardware Acceleration', value: 'PyTorch CUDA GPU Engine (Automatic fallback to CPU)' },
    { label: 'Segmentation Strategy', value: 'Binary Semantic Change Segmentation (0 = Background, 255 = Change)' },
    { label: 'Impact Index Formulation', value: 'CII = 100 × (0.40 · f_extent + 0.35 · f_conc + 0.25 · f_scale)' },
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 mb-8 shadow-card overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-6 flex items-center justify-between text-left bg-white hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center">
            <Code2 className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">Technical Specifications &amp; Architecture Details</h3>
            <p className="text-xs text-slate-500">
              Deep learning model parameters, dataset benchmarks, hardware engine, and mathematical index specs.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-blue-600 bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-100">
          <span>{isOpen ? 'Hide Specs' : 'View Specs'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="px-6 pb-6 pt-2 border-t border-slate-100 bg-slate-50/50">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mt-4">
            {specs.map((item, idx) => (
              <div key={idx} className="bg-white p-3.5 rounded-xl border border-slate-200/80 shadow-subtle flex justify-between gap-4">
                <span className="font-semibold text-slate-500">{item.label}:</span>
                <span className="font-bold text-slate-900 text-right">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
