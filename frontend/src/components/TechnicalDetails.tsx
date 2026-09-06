import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Cpu, Server, Shield, Layers, FileCode, Terminal } from 'lucide-react';
import { PipelineRunResponse, SystemStatusResponse } from '../types';

interface TechnicalDetailsProps {
  pipelineData: PipelineRunResponse | null;
  status: SystemStatusResponse | null;
}

export const TechnicalDetails: React.FC<TechnicalDetailsProps> = ({ pipelineData, status }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="glass-panel rounded-2xl border border-slate-800 shadow-xl overflow-hidden transition-all">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 sm:p-5 flex items-center justify-between hover:bg-slate-900/50 transition text-left"
      >
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <span>Technical Specification & Architecture Details</span>
              <span className="px-2 py-0.5 text-[10px] font-mono text-cyan-400 bg-cyan-500/10 rounded-full border border-cyan-500/20">
                For Evaluators
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Inspect model specs, deterministic hashing parameters, contract interfaces, and Web3 RPC metrics
            </p>
          </div>
        </div>

        <div className="p-1 rounded-lg bg-slate-800 text-slate-400">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="p-5 border-t border-slate-800/80 bg-slate-950/40 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 text-xs">
            
            {/* 1. Face AI */}
            <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400 flex items-center space-x-1.5">
                <Cpu className="w-3.5 h-3.5 text-cyan-400" />
                <span>Face AI Engine</span>
              </span>
              <p className="font-semibold text-white">
                {pipelineData?.face_analysis?.detector_model || status?.face_detector_model || 'OpenCV Deep Neural Cascade Engine'}
              </p>
              <p className="text-[11px] text-slate-400">
                128-D spatial frequency moments & lighting-invariant histogram equalization.
              </p>
            </div>

            {/* 2. Reverse Search */}
            <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400 flex items-center space-x-1.5">
                <Server className="w-3.5 h-3.5 text-purple-400" />
                <span>Reverse Image Provider</span>
              </span>
              <p className="font-semibold text-white">
                {pipelineData?.reverse_search?.provider || status?.reverse_image_provider || 'SerpApi (google_lens)'}
              </p>
              <p className="text-[11px] text-slate-400">
                Domain-level regex matching across Instagram, X, TikTok, YouTube, Reddit, LinkedIn.
              </p>
            </div>

            {/* 3. Blockchain & Smart Contract */}
            <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400 flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-emerald-400" />
                <span>Smart Contract Registry</span>
              </span>
              <p className="font-semibold text-white">
                {status?.blockchain_network || 'Polygon Amoy Testnet'} (Chain ID: {status?.blockchain_chain_id || 80002})
              </p>
              <p className="text-[11px] font-mono text-slate-400 truncate">
                Contract: {status?.smart_contract_address || '0x98Fc85d03C891C808E5F495493019808381D4bA5'}
              </p>
            </div>

            {/* 4. Evidence Hashing */}
            <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400 flex items-center space-x-1.5">
                <FileCode className="w-3.5 h-3.5 text-amber-400" />
                <span>Evidence Hash Algorithm</span>
              </span>
              <p className="font-semibold text-white">
                Deterministic RFC 8785 JSON + SHA-256
              </p>
              <p className="text-[11px] text-slate-400">
                EVM-compatible bytes32 representation passed to registerRecord().
              </p>
            </div>

            {/* 5. Zero Biometric Storage */}
            <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400 flex items-center space-x-1.5">
                <Shield className="w-3.5 h-3.5 text-indigo-400" />
                <span>Privacy & Biometrics</span>
              </span>
              <p className="font-semibold text-white">
                Zero Biometrics On-Chain
              </p>
              <p className="text-[11px] text-slate-400">
                Raw photos & embeddings remain on the ephemeral client/worker and are never registered on-chain.
              </p>
            </div>

            {/* 6. Solidity ABI Interface */}
            <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
              <span className="text-[11px] font-bold uppercase text-slate-400 flex items-center space-x-1.5">
                <Terminal className="w-3.5 h-3.5 text-rose-400" />
                <span>Solidity Method</span>
              </span>
              <p className="font-mono text-slate-200 text-[11px] truncate">
                registerRecord(bytes32,string,string)
              </p>
              <p className="text-[11px] text-slate-400">
                Emits RecordRegistered(uint256,bytes32,string,string,uint256,address)
              </p>
            </div>

          </div>

          {/* Canonical JSON representation if available */}
          {pipelineData?.evidence_hash && (
            <div className="p-3.5 rounded-xl bg-black/60 border border-slate-800 space-y-1.5">
              <span className="text-[10px] font-mono uppercase text-slate-400 block font-bold">
                Live Canonical JSON Payload:
              </span>
              <pre className="font-mono text-[11px] text-cyan-300 break-all whitespace-pre-wrap select-all">
                {pipelineData.evidence_hash.canonical_json}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
