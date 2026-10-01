import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import ImageUploader from './components/ImageUploader';
import MetricsOverview from './components/MetricsOverview';
import ImageComparison from './components/ImageComparison';
import CIIGaugeCard from './components/CIIGaugeCard';
import FactorBreakdown from './components/FactorBreakdown';
import SpatialDistribution from './components/SpatialDistribution';
import TechnicalDetails from './components/TechnicalDetails';
import LoadingOverlay from './components/LoadingOverlay';
import DownloadBar from './components/DownloadBar';
import {
  fetchHealthStatus,
  fetchSamplesList,
  analyzeImagePair,
  analyzeSamplePair
} from './services/api';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [samplesList, setSamplesList] = useState([]);
  const [selectedSample, setSelectedSample] = useState('test_100_10.png');

  const [imageA, setImageA] = useState(null);
  const [imageB, setImageB] = useState(null);
  const [previewA, setPreviewA] = useState(null);
  const [previewB, setPreviewB] = useState(null);

  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize backend connection and load samples list
  useEffect(() => {
    async function init() {
      const health = await fetchHealthStatus();
      setHealthStatus(health);

      const samples = await fetchSamplesList();
      setSamplesList(samples);
      if (samples && samples.length > 0 && !samples.includes(selectedSample)) {
        setSelectedSample(samples[0]);
      }
    }
    init();
  }, []);

  // Handler to load benchmark LEVIR sample pair
  const handleLoadSample = async () => {
    setIsLoading(true);
    setError(null);
    setImageA(null);
    setImageB(null);

    try {
      const res = await analyzeSamplePair(selectedSample);
      setAnalysisResult(res);
      if (res.image_a_preview) setPreviewA(res.image_a_preview);
      if (res.image_b_preview) setPreviewB(res.image_b_preview);
    } catch (err) {
      setError(err.message || 'Failed to process sample pair.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handler to execute pipeline on custom uploaded images
  const handleAnalyzeCustom = async () => {
    if (!imageA || !imageB) {
      setError('Please provide both Image A (T1) and Image B (T2) before analyzing.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await analyzeImagePair(imageA, imageB);
      setAnalysisResult(res);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please check image formats.');
    } finally {
      setIsLoading(false);
    }
  };

  // Wrapper for analyze button click
  const handleAnalyze = () => {
    if (imageA && imageB) {
      handleAnalyzeCustom();
    } else {
      handleLoadSample();
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Top Header Navigation */}
      <Header healthStatus={healthStatus} />

      {/* Main Content Area */}
      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Compact Hero Banner */}
        <Hero />

        {/* Error Notification Banner */}
        {error && (
          <div className="mb-6 p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-3 text-rose-800 text-sm shadow-subtle">
            <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0 mt-0.5" />
            <div className="flex-grow">
              <span className="font-bold block">Analysis Error</span>
              <span className="text-xs text-rose-700">{error}</span>
            </div>
            <button
              onClick={() => setError(null)}
              className="text-xs font-bold text-rose-600 hover:text-rose-800 underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Image Input Section */}
        <ImageUploader
          imageA={imageA}
          setImageA={(file) => {
            setImageA(file);
            setPreviewA(null);
          }}
          imageB={imageB}
          setImageB={(file) => {
            setImageB(file);
            setPreviewB(null);
          }}
          samplesList={samplesList}
          selectedSample={selectedSample}
          setSelectedSample={setSelectedSample}
          onLoadSample={handleLoadSample}
          onAnalyze={handleAnalyze}
          isLoading={isLoading}
          previewA={previewA}
          previewB={previewB}
        />

        {/* Loading Overlay State */}
        {isLoading && <LoadingOverlay />}

        {/* Results Sections */}
        {analysisResult && (
          <>
            {/* 4 Primary Metric Cards */}
            <MetricsOverview result={analysisResult} />

            {/* 3-Panel Visual Comparison */}
            <ImageComparison
              imageAPreview={imageA ? URL.createObjectURL(imageA) : previewA}
              imageBPreview={imageB ? URL.createObjectURL(imageB) : previewB}
              maskBase64={analysisResult.prediction_mask}
            />

            {/* CII Score & Gauge Card */}
            <CIIGaugeCard
              ciiScore={analysisResult.cii_score}
              impactCategory={analysisResult.impact_category}
              primaryDriver={analysisResult.primary_driver}
            />

            {/* Factor Breakdown Bars */}
            <FactorBreakdown factorContributions={analysisResult.factor_contributions} />

            {/* Spatial Density Heatmap & Visualization */}
            <SpatialDistribution
              visualizationBase64={analysisResult.analysis_visualization}
              gridDensityStats={analysisResult.grid_density_statistics}
            />

            {/* Downloads Bar */}
            <DownloadBar result={analysisResult} sampleName={selectedSample} />
          </>
        )}

        {/* Technical Details Collapsible Card */}
        <TechnicalDetails />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500 font-medium">
        <div className="max-w-7xl mx-auto px-4">
          <p>Satellite Change Intelligence System • Temporal Satellite Image Analysis for Change Detection (CNN–Transformer)</p>
          <p className="mt-1 text-[11px] text-slate-400">Powered by ChangeFormerV6 &amp; Explainable Change Impact Index (CII)</p>
        </div>
      </footer>
    </div>
  );
}
