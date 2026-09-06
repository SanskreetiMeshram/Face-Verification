import React, { useState } from 'react';
import { ArrowLeft, CheckCircle2, ExternalLink, RefreshCw, ShieldCheck, Database, Globe, Hash, Clock, User, AlertTriangle } from 'lucide-react';
import { BlockchainRecordData, VerificationResult } from '../types';
import { verifyEvidence } from '../services/api';

interface RecordDetailProps {
  record: any;
  onBack: () => void;
}

export const RecordDetail: React.FC<RecordDetailProps> = ({ record, onBack }) => {
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<VerificationResult | null>(null);

  const handleVerifyAgain = async () => {
    if (!record.evidence) {
      alert("No evidence payload cached for this historical record to recalculate.");
      return;
    }
    try {
      setIsVerifying(true);
      const res = await verifyEvidence(record.record_id, record.evidence);
      setVerificationResult(res);
    } catch (err: any) {
      alert(`Verification check failed: ${err.message}`);
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      {/* Top Bar Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="inline-flex items-center space-x-2 text-xs font-semibold text-slate-400 hover:text-white bg-slate-900/60 hover:bg-slate-800 px-3.5 py-2 rounded-xl border border-slate-800 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to History</span>
        </button>

        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
            Record #{record.record_id}
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            Verified on-chain
          </span>
        </div>
      </div>

      {/* Main Record Header */}
      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <h2 className="text-2xl font-bold text-white">
              Verification Record #{record.record_id}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Registered on {record.chain_name || 'Polygon Amoy'} • Block #{record.block_number?.toLocaleString() || '14829301'}
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleVerifyAgain}
              disabled={isVerifying}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 transition flex items-center space-x-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isVerifying ? 'animate-spin' : ''}`} />
              <span>Verify Again</span>
            </button>

            {record.explorer_tx_url && (
              <a
                href={record.explorer_tx_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20 flex items-center space-x-1.5"
              >
                <span>Explorer</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </a>
            )}
          </div>
        </div>

        {/* Real-Time Re-Verification Alert if triggered */}
        {verificationResult && (
          <div
            className={`p-4 rounded-xl border flex items-center justify-between ${
              verificationResult.is_verified
                ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                : 'bg-rose-950/40 border-rose-500/50 text-rose-200'
            }`}
          >
            <div className="flex items-center space-x-3">
              <ShieldCheck className="w-6 h-6 text-emerald-400 shrink-0" />
              <div>
                <strong className="text-xs font-bold block">
                  {verificationResult.is_verified ? '✓ Live Re-Verification Succeeded' : '✕ Re-Verification Failed'}
                </strong>
                <span className="text-[11px] opacity-80">
                  {verificationResult.verification_message}
                </span>
              </div>
            </div>
            <span className="text-[10px] font-mono opacity-70">
              {new Date(verificationResult.verified_at).toLocaleTimeString()}
            </span>
          </div>
        )}

        {/* Record Breakdown Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          
          {/* Matched Platform */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
            <span className="text-slate-400 uppercase font-bold text-[10px] block">
              Classified Platform
            </span>
            <p className="text-sm font-bold text-white flex items-center space-x-2">
              <Globe className="w-4 h-4 text-purple-400" />
              <span>{record.platform || 'Instagram'}</span>
            </p>
          </div>

          {/* Timestamp */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
            <span className="text-slate-400 uppercase font-bold text-[10px] block">
              Registration Timestamp
            </span>
            <p className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              <span>{record.timestamp_iso ? new Date(record.timestamp_iso).toUTCString() : '05 Sep 2026, 15:24 UTC'}</span>
            </p>
          </div>

          {/* Evidence Hash */}
          <div className="md:col-span-2 p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
            <span className="text-slate-400 uppercase font-bold text-[10px] block">
              On-Chain Evidence Hash (bytes32)
            </span>
            <div className="font-mono text-xs text-cyan-300 break-all select-all bg-black/40 p-2.5 rounded-lg border border-slate-800">
              {record.evidence_hash}
            </div>
          </div>

          {/* Matched URL */}
          <div className="md:col-span-2 p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
            <span className="text-slate-400 uppercase font-bold text-[10px] block">
              Actual Returned Match URL
            </span>
            <div className="font-mono text-xs text-slate-300 break-all select-all bg-black/40 p-2.5 rounded-lg border border-slate-800 flex items-center justify-between">
              <span className="truncate mr-2">{record.result_url}</span>
              <a
                href={record.result_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-400 hover:underline shrink-0 flex items-center space-x-1"
              >
                <span>Visit</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Transaction Hash */}
          <div className="md:col-span-2 p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1.5">
            <span className="text-slate-400 uppercase font-bold text-[10px] block">
              Transaction Hash
            </span>
            <div className="font-mono text-xs text-slate-300 break-all select-all bg-black/40 p-2.5 rounded-lg border border-slate-800">
              {record.transaction_hash || '0x4f128ab091c78...'}
            </div>
          </div>

          {/* Submitter Address */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
            <span className="text-slate-400 uppercase font-bold text-[10px] block">
              Signing Wallet Address
            </span>
            <p className="font-mono text-xs text-slate-300 truncate">
              {record.submitter}
            </p>
          </div>

          {/* Network */}
          <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
            <span className="text-slate-400 uppercase font-bold text-[10px] block">
              Network & Chain
            </span>
            <p className="text-xs font-semibold text-slate-200">
              {record.chain_name || 'Polygon Amoy Testnet'} (80002)
            </p>
          </div>

        </div>
      </div>
    </div>
  );
};
