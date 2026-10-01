import React, { useState } from 'react';
import { Eye, Maximize2, X, Image as ImageIcon, Binary } from 'lucide-react';

export default function ImageComparison({ imageAPreview, imageBPreview, maskBase64 }) {
  const [modalImage, setModalImage] = useState(null);

  const cards = [
    {
      title: 'T1 — BEFORE',
      subtitle: 'Pre-change satellite image',
      src: imageAPreview,
      badge: 'Image A'
    },
    {
      title: 'T2 — AFTER',
      subtitle: 'Post-change satellite image',
      src: imageBPreview,
      badge: 'Image B'
    },
    {
      title: 'DETECTED CHANGE',
      subtitle: 'ChangeFormer prediction mask (0/255)',
      src: maskBase64,
      badge: 'Binary Mask'
    }
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-8 shadow-card">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <div>
          <h3 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Eye className="w-5 h-5 text-blue-600" />
            Bi-Temporal Visual Comparison &amp; Change Mask
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Side-by-side alignment of pre-change imagery, post-change imagery, and ChangeFormer segmentation output.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((card, idx) => (
          <div
            key={idx}
            className="bg-slate-50/70 rounded-xl border border-slate-200 overflow-hidden flex flex-col justify-between group hover:border-blue-300 transition-all"
          >
            <div className="p-4 border-b border-slate-200/80 bg-white flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-900 block">{card.title}</span>
                <span className="text-[11px] text-slate-400 font-medium block">{card.subtitle}</span>
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                {card.badge}
              </span>
            </div>

            <div className="p-4 flex items-center justify-center relative min-h-[220px]">
              {card.src ? (
                <div className="relative group/img w-full flex items-center justify-center">
                  <img
                    src={card.src}
                    alt={card.title}
                    className="max-h-56 rounded-lg object-contain border border-slate-200/80 shadow-subtle transition-transform duration-200 group-hover/img:scale-[1.02]"
                  />
                  <button
                    onClick={() => setModalImage({ title: card.title, src: card.src })}
                    className="absolute inset-0 m-auto w-10 h-10 rounded-full bg-slate-900/60 backdrop-blur-sm text-white flex items-center justify-center opacity-0 group-hover/img:opacity-100 transition-opacity shadow-lg"
                    title="Zoom Image"
                  >
                    <Maximize2 className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <div className="text-xs text-slate-400 font-medium text-center">No image data</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Modal for Fullscreen View */}
      {modalImage && (
        <div className="fixed inset-0 z-50 bg-slate-900/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full p-6 relative shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
              <h4 className="text-base font-bold text-slate-900">{modalImage.title}</h4>
              <button
                onClick={() => setModalImage(null)}
                className="w-8 h-8 rounded-full bg-slate-100 text-slate-600 flex items-center justify-center hover:bg-slate-200 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex items-center justify-center min-h-[400px]">
              <img
                src={modalImage.src}
                alt={modalImage.title}
                className="max-h-[70vh] rounded-lg object-contain border border-slate-200"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
