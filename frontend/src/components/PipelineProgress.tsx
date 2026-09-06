import React from 'react';
import { CheckCircle2, Circle, Loader2, XCircle, ChevronRight } from 'lucide-react';
import { PipelineStepStatus } from '../types';

interface PipelineProgressProps {
  steps: PipelineStepStatus[];
  isLoading: boolean;
}

const DEFAULT_STEPS = [
  { step_number: 1, name: "IMAGE UPLOAD", default_msg: "Upload received & validated" },
  { step_number: 2, name: "FACE AI", default_msg: "Face detected + safe embedding generated" },
  { step_number: 3, name: "REVERSE SEARCH", default_msg: "Searching genuine image sources" },
  { step_number: 4, name: "SOCIAL MATCH", default_msg: "Social-media domain classified" },
  { step_number: 5, name: "EVIDENCE HASH", default_msg: "Canonical JSON SHA-256 fingerprint" },
  { step_number: 6, name: "BLOCKCHAIN", default_msg: "Polygon Amoy registry transaction" },
  { step_number: 7, name: "VERIFICATION", default_msg: "On-chain evidence verified" },
];

export const PipelineProgress: React.FC<PipelineProgressProps> = ({ steps, isLoading }) => {
  const getStepStatus = (stepNum: number) => {
    const found = steps.find((s) => s.step_number === stepNum);
    if (found) return found;
    return {
      step_number: stepNum,
      name: DEFAULT_STEPS[stepNum - 1].name,
      status: 'pending' as const,
      message: DEFAULT_STEPS[stepNum - 1].default_msg,
    };
  };

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Pipeline Execution Flow
          </h3>
          <p className="text-xs text-slate-500">
            End-to-End Cryptographic & On-Chain Lifecycle
          </p>
        </div>

        {isLoading && (
          <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>Processing Pipeline...</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-7 gap-3">
        {DEFAULT_STEPS.map((defStep, idx) => {
          const stepData = getStepStatus(defStep.step_number);
          const isPending = stepData.status === 'pending';
          const isProcessing = stepData.status === 'processing';
          const isSuccess = stepData.status === 'success';
          const isFailed = stepData.status === 'failed';

          return (
            <div
              key={defStep.step_number}
              className={`relative p-3.5 rounded-xl border transition-all duration-300 flex flex-col justify-between ${
                isSuccess
                  ? 'bg-emerald-950/20 border-emerald-500/40 shadow-sm shadow-emerald-500/10'
                  : isProcessing
                  ? 'bg-cyan-950/30 border-cyan-400 shadow-md shadow-cyan-500/20 animate-pulse-slow'
                  : isFailed
                  ? 'bg-rose-950/30 border-rose-500/50 shadow-sm shadow-rose-500/10'
                  : 'bg-slate-900/40 border-slate-800/80 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-mono font-bold text-slate-400">
                  0{defStep.step_number}
                </span>

                {isSuccess && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                {isProcessing && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
                {isFailed && <XCircle className="w-4 h-4 text-rose-400" />}
                {isPending && <Circle className="w-4 h-4 text-slate-600" />}
              </div>

              <div>
                <h4
                  className={`text-xs font-bold tracking-tight mb-1 truncate ${
                    isSuccess
                      ? 'text-emerald-300'
                      : isProcessing
                      ? 'text-cyan-300'
                      : isFailed
                      ? 'text-rose-300'
                      : 'text-slate-400'
                  }`}
                >
                  {defStep.name}
                </h4>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                  {stepData.message || defStep.default_msg}
                </p>
              </div>

              {/* Step indicator bottom bar */}
              <div className="mt-3 h-1 w-full rounded-full bg-slate-800 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    isSuccess
                      ? 'bg-emerald-400 w-full'
                      : isProcessing
                      ? 'bg-cyan-400 w-3/4 animate-pulse'
                      : isFailed
                      ? 'bg-rose-400 w-full'
                      : 'w-0'
                  }`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
