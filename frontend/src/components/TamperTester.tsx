import React, { useState } from 'react';
import { ShieldAlert, ShieldCheck, RefreshCw, Sparkles, AlertTriangle, Code, ArrowRight } from 'lucide-react';
import { CanonicalEvidence, VerificationResult } from '../types';
import { verifyEvidence } from '../services/api';

interface TamperTesterProps {
  initialEvidence?: CanonicalEvidence | null;
  initialRecordId?: number | null;
}

export const TamperTester: React.FC<TamperTesterProps> = ({
  initialEvidence,
  initialRecordId = 1,
}) => {
  const [recordId, setRecordId] = useState<number>(initialRecordId || 1);
  const [evidence, setEvidence] = useState<CanonicalEvidence>(
    initialEvidence || {
      source_image_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      reverse_search_provider: "SerpApi (google_lens)",
      matched_url: "https://www.instagram.com/p/C_DemoPhotoRecord2026",
      platform: "Instagram",
      search_timestamp: "2026-09-05T12:00:00Z",
      match_metadata: {
        title: "Verified Social Record",
        domain: "instagram.com"
      }
    }
  );

  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [tamperApplied, setTamperApplied] = useState(false);

  const handleTamperUrl = () => {
    setEvidence((prev) => ({
      ...prev,
      matched_url: prev.matched_url.includes('_tampered')
        ? prev.matched_url.replace('_tampered', '')
        : `${prev.matched_url}_tampered_fake_account`,
    }));
    setTamperApplied(true);
    setVerificationResult(null);
  };

  const handleTamperHash = () => {
    setEvidence((prev) => ({
      ...prev,
      source_image_sha256: prev.source_image_sha256.endsWith('00')
        ? prev.source_image_sha256.slice(0, -2) + 'ff'
        : prev.source_image_sha256.slice(0, -2) + '00',
    }));
    setTamperApplied(true);
    setVerificationResult(null);
  };

  const handleRestore = () => {
    if (initialEvidence) {
      setEvidence(initialEvidence);
    } else {
      setEvidence({
        source_image_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        reverse_search_provider: "SerpApi (google_lens)",
        matched_url: "https://www.instagram.com/p/C_DemoPhotoRecord2026",
        platform: "Instagram",
        search_timestamp: "2026-09-05T12:00:00Z",
        match_metadata: {
          title: "Verified Social Record",
          domain: "instagram.com"
        }
      });
    }
    setTamperApplied(false);
    setVerificationResult(null);
  };

  const runVerificationCheck = async () => {
    try {
      setIsVerifying(true);
      const res = await verifyEvidence(recordId, evidence);
      setVerificationResult(res);
    } catch (err: any) {
      alert(`Verification check failed: ${err.message}`);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-2xl relative overflow-hidden space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2.5">
            <ShieldAlert className="w-6 h-6 text-purple-400" />
            <span>Interactive Tamper-Evident Lab</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Test the immutability of the blockchain registry by modifying evidence fields and observing hash divergence.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleTamperUrl}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 transition"
          >
            ⚡ Tamper URL
          </button>
          <button
            onClick={handleTamperHash}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 transition"
          >
            ⚡ Alter Image Hash
          </button>
          <button
            onClick={handleRestore}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
          >
            Reset
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Evidence JSON Editor */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
              <Code className="w-3.5 h-3.5 text-cyan-400" />
              <span>Canonical Evidence Object</span>
            </span>
            <div className="flex items-center space-x-2">
              <label className="text-xs text-slate-400">Target Record ID:</label>
              <input
                type="number"
                value={recordId}
                onChange={(e) => setRecordId(parseInt(e.target.value) || 1)}
                className="w-16 px-2 py-0.5 rounded bg-black/60 border border-slate-700 text-cyan-300 text-xs font-mono text-center focus:outline-none focus:border-cyan-400"
              />
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Matched Social URL:</label>
              <input
                type="text"
                value={evidence.matched_url}
                onChange={(e) => {
                  setEvidence({ ...evidence, matched_url: e.target.value });
                  setTamperApplied(true);
                  setVerificationResult(null);
                }}
                className="w-full px-3 py-2 rounded-lg bg-black/60 border border-slate-700 text-slate-200 font-mono text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Source Image SHA-256:</label>
              <input
                type="text"
                value={evidence.source_image_sha256}
                onChange={(e) => {
                  setEvidence({ ...evidence, source_image_sha256: e.target.value });
                  setTamperApplied(true);
                  setVerificationResult(null);
                }}
                className="w-full px-3 py-2 rounded-lg bg-black/60 border border-slate-700 text-slate-200 font-mono text-xs focus:outline-none focus:border-cyan-400"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Platform:</label>
                <input
                  type="text"
                  value={evidence.platform}
                  onChange={(e) => {
                    setEvidence({ ...evidence, platform: e.target.value });
                    setTamperApplied(true);
                    setVerificationResult(null);
                  }}
                  className="w-full px-3 py-2 rounded-lg bg-black/60 border border-slate-700 text-slate-200 font-mono text-xs focus:outline-none focus:border-cyan-400"
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Search Timestamp:</label>
                <input
                  type="text"
                  value={evidence.search_timestamp}
                  onChange={(e) => {
                    setEvidence({ ...evidence, search_timestamp: e.target.value });
                    setTamperApplied(true);
                    setVerificationResult(null);
                  }}
                  className="w-full px-3 py-2 rounded-lg bg-black/60 border border-slate-700 text-slate-200 font-mono text-xs focus:outline-none focus:border-cyan-400"
                />
              </div>
            </div>
          </div>

          <div className="pt-3">
            <button
              onClick={runVerificationCheck}
              disabled={isVerifying}
              className="w-full py-2.5 rounded-xl font-semibold text-xs text-white bg-gradient-to-r from-purple-600 via-indigo-600 to-cyan-600 hover:opacity-90 active:scale-95 transition flex items-center justify-center space-x-2 shadow-lg shadow-purple-500/20"
            >
              {isVerifying ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Verifying Against Blockchain Record #{recordId}...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Verify Evidence Hash with On-Chain Record</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Live Result View */}
        <div className="lg:col-span-5 flex flex-col justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              On-Chain Verification Outcome
            </h4>

            {verificationResult ? (
              <div
                className={`p-4 rounded-xl border space-y-3 ${
                  verificationResult.is_verified
                    ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                    : 'bg-rose-950/40 border-rose-500/50 text-rose-200'
                }`}
              >
                <div className="flex items-center space-x-2">
                  {verificationResult.is_verified ? (
                    <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
                  ) : (
                    <ShieldAlert className="w-6 h-6 text-rose-400 shrink-0" />
                  )}
                  <div>
                    <h5 className="text-sm font-bold">
                      {verificationResult.is_verified
                        ? '✓ HASH MATCH CONFIRMED'
                        : '✕ RECORD MISMATCH (TAMPERED)'}
                    </h5>
                    <p className="text-[11px] opacity-80 leading-tight">
                      {verificationResult.verification_message}
                    </p>
                  </div>
                </div>

                <div className="pt-2 border-t border-white/10 space-y-1.5 font-mono text-[10px]">
                  <div>
                    <span className="opacity-60 block">Calculated Hash:</span>
                    <span className="break-all font-semibold select-all">
                      {verificationResult.calculated_hash}
                    </span>
                  </div>
                  <div>
                    <span className="opacity-60 block">Blockchain On-Chain Hash:</span>
                    <span className="break-all font-semibold select-all">
                      {verificationResult.blockchain_hash}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-6 rounded-xl border border-dashed border-slate-800 text-center text-slate-500 space-y-2">
                <AlertTriangle className="w-6 h-6 mx-auto text-slate-600" />
                <p className="text-xs">Click "Verify Evidence Hash" to compare against blockchain state</p>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 leading-relaxed">
            💡 <strong>How it works:</strong> Any modification to the evidence object creates a completely different SHA-256 hash. The smart contract verifies integrity without ever exposing user biometrics.
          </div>
        </div>
      </div>
    </div>
  );
};
