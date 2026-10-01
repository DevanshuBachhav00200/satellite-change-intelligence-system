import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, Play, RefreshCw, FileCheck, Sparkles } from 'lucide-react';

export default function ImageUploader({
  imageA,
  setImageA,
  imageB,
  setImageB,
  samplesList,
  selectedSample,
  setSelectedSample,
  onLoadSample,
  onAnalyze,
  isLoading,
  previewA,
  previewB
}) {
  const fileInputARef = useRef(null);
  const fileInputBRef = useRef(null);

  const handleFileChangeA = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImageA(e.target.files[0]);
    }
  };

  const handleFileChangeB = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImageB(e.target.files[0]);
    }
  };

  const renderUploadBox = (title, imageFile, previewUrl, inputRef, onChange) => {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-subtle hover:border-blue-300 transition-all flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-2.5 py-1 rounded-md">
              {title}
            </span>
            {imageFile || previewUrl ? (
              <span className="flex items-center gap-1 text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                <FileCheck className="w-3.5 h-3.5" /> RGB 256×256 Verified
              </span>
            ) : (
              <span className="text-xs text-slate-400">Target: 256×256 RGB</span>
            )}
          </div>

          <div
            onClick={() => inputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[200px] ${
              previewUrl || imageFile
                ? 'border-blue-300 bg-blue-50/20'
                : 'border-slate-300 bg-slate-50/50 hover:bg-slate-100/70 hover:border-slate-400'
            }`}
          >
            <input
              type="file"
              ref={inputRef}
              onChange={onChange}
              accept="image/png, image/jpeg, image/tiff"
              className="hidden"
            />

            {previewUrl || imageFile ? (
              <div className="relative group w-full flex flex-col items-center">
                <img
                  src={imageFile ? URL.createObjectURL(imageFile) : previewUrl}
                  alt={title}
                  className="max-h-40 rounded-lg object-cover shadow-sm border border-slate-200"
                />
                <div className="mt-2 text-xs font-semibold text-slate-700 truncate max-w-full">
                  {imageFile ? imageFile.name : selectedSample || title}
                </div>
                <span className="text-[11px] text-slate-400">Click to replace image</span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <span className="text-sm font-semibold text-slate-700">Click to upload image</span>
                <span className="text-xs text-slate-400 max-w-[200px]">
                  Supports PNG, JPG, JPEG, TIF satellite imagery
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const isReady = (imageA || previewA) && (imageB || previewB);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 mb-8 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-slate-100">
        <div>
          <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <ImageIcon className="w-5 h-5 text-blue-600" />
            Bi-Temporal Image Analysis Input
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Select a test sample pair from LEVIR-CD benchmark or upload custom bi-temporal satellite images.
          </p>
        </div>

        {/* Preset sample selector */}
        <div className="flex items-center gap-2 bg-slate-50 p-1.5 rounded-xl border border-slate-200">
          <span className="text-xs font-semibold text-slate-600 pl-2">Sample Test Pair:</span>
          <select
            value={selectedSample}
            onChange={(e) => setSelectedSample(e.target.value)}
            className="text-xs font-semibold text-slate-800 bg-white border border-slate-300 rounded-lg px-2.5 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {samplesList && samplesList.length > 0 ? (
              samplesList.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))
            ) : (
              <option value="test_100_10.png">test_100_10.png</option>
            )}
          </select>
          <button
            onClick={onLoadSample}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all disabled:opacity-50"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Load Sample
          </button>
        </div>
      </div>

      {/* Upload Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {renderUploadBox("T1 — BEFORE", imageA, previewA, fileInputARef, handleFileChangeA)}
        {renderUploadBox("T2 — AFTER", imageB, previewB, fileInputBRef, handleFileChangeB)}
      </div>

      {/* Action CTA Button */}
      <div className="flex justify-end">
        <button
          onClick={onAnalyze}
          disabled={!isReady || isLoading}
          className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2.5 transition-all shadow-md ${
            isReady && !isLoading
              ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/25 hover:shadow-lg'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
          }`}
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-white" />
              <span>Executing Pipeline...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Analyze Change Intelligence</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
