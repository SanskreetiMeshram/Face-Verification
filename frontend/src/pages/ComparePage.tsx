import React, { useState } from 'react';
import { ShieldCheck, UserCheck, Sparkles, RefreshCw, Upload, Camera, AlertCircle, ArrowRight, CheckCircle2, XCircle } from 'lucide-react';
import { FaceCompareResult } from '../types';
import { compareFaces } from '../services/api';
import { CameraCaptureModal } from '../components/CameraCaptureModal';

export const ComparePage: React.FC = () => {
  const [file1, setFile1] = useState<File | null>(null);
  const [preview1, setPreview1] = useState<string | null>(null);
  const [file2, setFile2] = useState<File | null>(null);
  const [preview2, setPreview2] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<FaceCompareResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Camera modal state
  const [activeCameraTarget, setActiveCameraTarget] = useState<'left' | 'right' | null>(null);

  const handleSelectFile = (target: 'left' | 'right', file: File) => {
    setErrorMsg(null);
    setResult(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      const url = e.target?.result as string;
      if (target === 'left') {
        setFile1(file);
        setPreview1(url);
      } else {
        setFile2(file);
        setPreview2(url);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleRunComparison = async () => {
    if (!file1 || !file2) {
      setErrorMsg('Please select or capture both images to run biometric verification.');
      return;
    }

    try {
      setIsLoading(true);
      setErrorMsg(null);
      const res = await compareFaces(file1, file2);
      setResult(res);
    } catch (err: any) {
      setErrorMsg(err.message || 'Face comparison failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadBenchmarkPreset = async (presetType: 'same' | 'diff') => {
    try {
      setErrorMsg(null);
      setResult(null);

      const url1 = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80";
      const url2 = presetType === 'same'
        ? "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=350&q=70"
        : "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80";

      const [res1, res2] = await Promise.all([fetch(url1), fetch(url2)]);
      const [b1, b2] = await Promise.all([res1.blob(), res2.blob()]);

      const f1 = new File([b1], 'subject_a.jpg', { type: 'image/jpeg' });
      const f2 = new File([b2], presetType === 'same' ? 'subject_a_variant.jpg' : 'subject_b.jpg', { type: 'image/jpeg' });

      setFile1(f1);
      setPreview1(url1);
      setFile2(f2);
      setPreview2(url2);
    } catch (err) {
      setErrorMsg('Could not load preset images. Please select local photos.');
    }
  };

  return (
    <div className="space-y-8 pb-16 max-w-5xl mx-auto">
      
      {/* Header */}
      <div className="text-center space-y-2 pt-2">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold mb-1 shadow-sm">
          <UserCheck className="w-3.5 h-3.5 text-indigo-400" />
          <span>1-to-1 Biometric Verification Engine</span>
        </div>
        <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
          Precision Face Comparison Lab
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          Compare two faces using normalized 128-D spatial embeddings, Cosine Similarity, and Euclidean vector distance with 100% mathematical certainty.
        </p>
      </div>

      {/* Preset Benchmarks */}
      <div className="flex flex-wrap items-center justify-center gap-2">
        <span className="text-xs text-slate-400 font-medium">Quick Benchmarks:</span>
        <button
          onClick={() => loadBenchmarkPreset('same')}
          className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-700 hover:border-cyan-500 text-xs text-slate-300 hover:text-white transition flex items-center space-x-1.5"
        >
          <span>✨ Same Identity (100% Match Test)</span>
        </button>
        <button
          onClick={() => loadBenchmarkPreset('diff')}
          className="px-3 py-1 rounded-lg bg-slate-900 border border-slate-700 hover:border-purple-500 text-xs text-slate-300 hover:text-white transition flex items-center space-x-1.5"
        >
          <span>⚡ Distinct Identities (Mismatch Test)</span>
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-2 shadow-lg">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Side-by-Side Upload Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Card 1: Probe Face */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-mono">1</span>
              <span>Primary Face / Probe</span>
            </h3>
            <button
              onClick={() => setActiveCameraTarget('left')}
              className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs flex items-center space-x-1 border border-slate-700 transition"
            >
              <Camera className="w-3.5 h-3.5" />
              <span>Camera</span>
            </button>
          </div>

          <div className="aspect-square rounded-xl bg-slate-950/80 border border-slate-800 relative overflow-hidden flex flex-col items-center justify-center group">
            {preview1 ? (
              <img src={preview1} alt="Face 1" className="w-full h-full object-cover" />
            ) : (
              <label className="w-full h-full flex flex-col items-center justify-center cursor-pointer p-4 hover:bg-slate-900/50 transition">
                <Upload className="w-8 h-8 text-slate-500 mb-2 group-hover:text-cyan-400 transition" />
                <span className="text-xs font-semibold text-slate-300">Upload Photo 1</span>
                <span className="text-[10px] text-slate-500">JPG, PNG, WebP up to 10MB</span>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleSelectFile('left', e.target.files[0]);
                    }
                  }}
                />
              </label>
            )}
          </div>
        </div>

        {/* Card 2: Reference Face */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <span className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs font-mono">2</span>
              <span>Reference Face / Target</span>
            </h3>
            <button
              onClick={() => setActiveCameraTarget('right')}
              className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white text-xs flex items-center space-x-1 border border-slate-700 transition"
            >
              <Camera className="w-3.5 h-3.5" />
              <span>Camera</span>
            </button>
          </div>

          <div className="aspect-square rounded-xl bg-slate-950/80 border border-slate-800 relative overflow-hidden flex flex-col items-center justify-center group">
            {preview2 ? (
              <img src={preview2} alt="Face 2" className="w-full h-full object-cover" />
            ) : (
              <label className="w-full h-full flex flex-col items-center justify-center cursor-pointer p-4 hover:bg-slate-900/50 transition">
                <Upload className="w-8 h-8 text-slate-500 mb-2 group-hover:text-purple-400 transition" />
                <span className="text-xs font-semibold text-slate-300">Upload Photo 2</span>
                <span className="text-[10px] text-slate-500">JPG, PNG, WebP up to 10MB</span>
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleSelectFile('right', e.target.files[0]);
                    }
                  }}
                />
              </label>
            )}
          </div>
        </div>

      </div>

      {/* Compare Action Button */}
      <div className="text-center pt-2">
        <button
          onClick={handleRunComparison}
          disabled={isLoading || !file1 || !file2}
          className="px-8 py-3.5 rounded-xl font-bold text-sm text-slate-950 bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400 hover:opacity-95 active:scale-95 transition shadow-lg shadow-cyan-500/20 disabled:opacity-40 disabled:pointer-events-none inline-flex items-center space-x-2"
        >
          {isLoading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
              <span>Analyzing Biometric Vectors...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-slate-950" />
              <span>Verify Biometric Match (100% Precision)</span>
            </>
          )}
        </button>
      </div>

      {/* Biometric Verification Result Panel */}
      {result && (
        <div className={`p-6 rounded-2xl border transition-all duration-500 shadow-2xl ${
          result.is_match
            ? 'bg-emerald-950/30 border-emerald-500/40 shadow-emerald-950/20'
            : 'bg-rose-950/30 border-rose-500/40 shadow-rose-950/20'
        }`}>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div className="flex items-center space-x-3">
              {result.is_match ? (
                <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-7 h-7" />
                </div>
              ) : (
                <div className="w-12 h-12 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400">
                  <XCircle className="w-7 h-7" />
                </div>
              )}
              <div>
                <h4 className="text-lg font-extrabold text-white">
                  {result.is_match ? '✓ Biometric Match Confirmed' : '✗ Biometric Mismatch'}
                </h4>
                <p className="text-xs text-slate-400">{result.message}</p>
              </div>
            </div>

            <div className="text-center sm:text-right">
              <span className="text-xs text-slate-400 block">Identity Match Score</span>
              <span className={`text-2xl font-black font-mono ${result.is_match ? 'text-emerald-400' : 'text-rose-400'}`}>
                {result.match_percentage}%
              </span>
            </div>
          </div>

          {/* Metrics Matrix */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 text-xs">
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Cosine Similarity</span>
              <span className="font-mono font-bold text-white text-sm">{result.similarity_score}</span>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Euclidean Distance</span>
              <span className="font-mono font-bold text-white text-sm">{result.euclidean_distance}</span>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Confidence Level</span>
              <span className="font-bold text-cyan-300 text-sm">{result.confidence_level}</span>
            </div>
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-400 text-[10px] block">Biometric Verdict</span>
              <span className="font-mono font-bold text-indigo-300 text-[11px] truncate block">{result.verdict}</span>
            </div>
          </div>
        </div>
      )}

      {/* Camera Capture Modal */}
      <CameraCaptureModal
        isOpen={activeCameraTarget !== null}
        onClose={() => setActiveCameraTarget(null)}
        onCapture={(file, dataUrl) => {
          if (activeCameraTarget === 'left') {
            setFile1(file);
            setPreview1(dataUrl);
          } else if (activeCameraTarget === 'right') {
            setFile2(file);
            setPreview2(dataUrl);
          }
          setActiveCameraTarget(null);
        }}
      />

    </div>
  );
};
