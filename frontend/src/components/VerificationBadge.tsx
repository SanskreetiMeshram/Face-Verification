import React from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertOctagon, ArrowRight } from 'lucide-react';
import { VerificationResult } from '../types';

interface VerificationBadgeProps {
  verification: VerificationResult | null;
}

export const VerificationBadge: React.FC<VerificationBadgeProps> = ({ verification }) => {
  if (!verification) return null;

  const isVerified = verification.is_verified;

  return (
    <div
      className={`p-6 rounded-2xl border transition-all duration-300 shadow-2xl relative overflow-hidden ${
        isVerified
          ? 'bg-emerald-950/30 border-emerald-500/50 shadow-emerald-500/10'
          : 'bg-rose-950/30 border-rose-500/50 shadow-rose-500/10'
      }`}
    >
      {/* Glow pulse */}
      <div
        className={`absolute top-0 right-0 w-80 h-80 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20 ${
          isVerified ? 'bg-emerald-500/10' : 'bg-rose-500/10'
        }`}
      />

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start space-x-3.5">
          <div
            className={`p-3 rounded-2xl border shrink-0 ${
              isVerified
                ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400 glow-green'
                : 'bg-rose-500/20 border-rose-500/40 text-rose-400 glow-red'
            }`}
          >
            {isVerified ? (
              <ShieldCheck className="w-8 h-8" />
            ) : (
              <ShieldAlert className="w-8 h-8" />
            )}
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h3
                className={`text-xl font-extrabold tracking-tight ${
                  isVerified ? 'text-emerald-300' : 'text-rose-300'
                }`}
              >
                {isVerified ? '✓ VERIFIED ON-CHAIN' : '✕ VERIFICATION FAILED'}
              </h3>
              <span
                className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded ${
                  isVerified
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : 'bg-rose-500/20 text-rose-300'
                }`}
              >
                Record #{verification.record_id}
              </span>
            </div>

            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              {verification.verification_message}
            </p>
          </div>
        </div>

        {/* Status Chip */}
        <div className="shrink-0">
          <div
            className={`px-4 py-2 rounded-xl border text-xs font-mono font-bold flex items-center space-x-2 ${
              isVerified
                ? 'bg-emerald-900/40 text-emerald-300 border-emerald-500/40'
                : 'bg-rose-900/40 text-rose-300 border-rose-500/40'
            }`}
          >
            {isVerified ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>SHA-256 HASH MATCH CONFIRMED</span>
              </>
            ) : (
              <>
                <AlertOctagon className="w-4 h-4 text-rose-400" />
                <span>TAMPER DETECTED / MISMATCH</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Hash comparison details */}
      <div className="mt-5 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
        <div className="p-3 rounded-xl bg-black/40 border border-slate-800">
          <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
            Calculated Local Hash:
          </span>
          <span className="text-slate-200 break-all select-all font-mono">
            {verification.calculated_hash}
          </span>
        </div>

        <div className="p-3 rounded-xl bg-black/40 border border-slate-800">
          <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
            Immutable Blockchain Record Hash:
          </span>
          <span className="text-cyan-300 break-all select-all font-mono">
            {verification.blockchain_hash}
          </span>
        </div>
      </div>
    </div>
  );
};
