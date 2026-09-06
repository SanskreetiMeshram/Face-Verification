import React, { useState } from 'react';
import { Database, ExternalLink, Copy, Check, Blocks, Clock, ShieldCheck, User } from 'lucide-react';
import { BlockchainRegisterResponse } from '../types';

interface BlockchainCardProps {
  blockchainData: BlockchainRegisterResponse | null;
}

export const BlockchainCard: React.FC<BlockchainCardProps> = ({ blockchainData }) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = (text: string, fieldName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    setTimeout(() => setCopiedField(null), 2000);
  };

  if (!blockchainData) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col items-center justify-center min-h-[300px] text-center text-slate-500">
        <Database className="w-12 h-12 text-slate-700 mb-3 animate-pulse" />
        <p className="text-sm font-semibold text-slate-400">Blockchain Registration Pending</p>
        <p className="text-xs text-slate-600 mt-1">Registers SHA-256 evidence fingerprint to Polygon Amoy smart contract</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
      {/* Subtle background glow */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Card Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Blockchain Registry Record</h3>
            <p className="text-xs text-slate-400">
              {blockchainData.chain_name} (Chain ID: {blockchainData.chain_id})
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {blockchainData.is_simulated ? (
            <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
              Testnet In-Memory Node
            </span>
          ) : (
            <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Live Polygon Amoy
            </span>
          )}
          <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-purple-500/10 text-purple-300 border border-purple-500/30">
            Record #{blockchainData.record_id}
          </span>
        </div>
      </div>

      {/* Main Blockchain Fields Grid */}
      <div className="space-y-3.5">
        {/* Evidence Hash */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-slate-400">
              Canonical Evidence Hash (bytes32)
            </span>
            <button
              onClick={() => copyToClipboard(blockchainData.evidence_hash, 'evidence_hash')}
              className="text-slate-400 hover:text-white text-xs flex items-center space-x-1"
            >
              {copiedField === 'evidence_hash' ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
              <span className="text-[10px]">{copiedField === 'evidence_hash' ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
          <div className="font-mono text-xs text-cyan-300 break-all select-all bg-black/40 p-2 rounded-lg border border-slate-800/80">
            {blockchainData.evidence_hash}
          </div>
        </div>

        {/* Transaction Hash */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-slate-400">
              Transaction Hash
            </span>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => copyToClipboard(blockchainData.transaction_hash, 'tx_hash')}
                className="text-slate-400 hover:text-white text-xs flex items-center space-x-1"
              >
                {copiedField === 'tx_hash' ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
                <span className="text-[10px]">{copiedField === 'tx_hash' ? 'Copied' : 'Copy'}</span>
              </button>

              <a
                href={blockchainData.explorer_tx_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-cyan-400 hover:underline flex items-center space-x-1 font-semibold"
              >
                <span>View on Explorer</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
          <div className="font-mono text-xs text-slate-300 break-all select-all bg-black/40 p-2 rounded-lg border border-slate-800/80">
            {blockchainData.transaction_hash}
          </div>
        </div>

        {/* Meta Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center space-x-2.5">
            <Blocks className="w-4 h-4 text-indigo-400 shrink-0" />
            <div className="min-w-0">
              <span className="text-[10px] uppercase font-bold text-slate-500 block">Block Height</span>
              <span className="text-xs font-mono font-semibold text-slate-200">
                #{blockchainData.block_number.toLocaleString()}
              </span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center space-x-2.5">
            <Clock className="w-4 h-4 text-emerald-400 shrink-0" />
            <div className="min-w-0">
              <span className="text-[10px] uppercase font-bold text-slate-500 block">Confirmed At</span>
              <span className="text-xs font-mono font-semibold text-slate-200 truncate block">
                {new Date(blockchainData.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center space-x-2.5">
            <User className="w-4 h-4 text-purple-400 shrink-0" />
            <div className="min-w-0">
              <span className="text-[10px] uppercase font-bold text-slate-500 block">Signer Wallet</span>
              <span className="text-xs font-mono font-semibold text-slate-200 truncate block">
                {blockchainData.submitter.slice(0, 6)}...{blockchainData.submitter.slice(-4)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
