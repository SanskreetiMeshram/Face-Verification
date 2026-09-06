import React from 'react';
import { Settings, Cpu, Globe, Database, Shield, CheckCircle2, AlertCircle, ExternalLink, Lock } from 'lucide-react';
import { SystemStatusResponse } from '../types';

interface SettingsPageProps {
  status: SystemStatusResponse | null;
  onRefresh: () => void;
}

export const SettingsPage: React.FC<SettingsPageProps> = ({ status, onRefresh }) => {
  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-16">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center space-x-2.5">
            <Settings className="w-6 h-6 text-cyan-400" />
            <span>System Status & Configuration</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Live pipeline health, connected RPC endpoints, and cryptographic parameters
          </p>
        </div>

        <button
          onClick={onRefresh}
          className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 transition"
        >
          Refresh Status
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* 1. Face AI Status Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Face AI Engine</h3>
                <p className="text-[11px] text-slate-400">Detection & Local Encoding</p>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Ready</span>
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Detector Model:</span>
              <span className="font-semibold text-slate-200">
                {status?.face_detector_model || 'OpenCV Deep Neural Cascade'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Embedding Extraction:</span>
              <span className="font-semibold text-slate-200">128-D Normalized Vector</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Biometric Privacy:</span>
              <span className="font-semibold text-emerald-400">Zero On-Chain Storage</span>
            </div>
          </div>
        </div>

        {/* 2. Reverse Search Provider */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2.5 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Reverse Image Search</h3>
                <p className="text-[11px] text-slate-400">Provider Abstraction Layer</p>
              </div>
            </div>

            {status?.reverse_image_api_configured ? (
              <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Live API</span>
              </span>
            ) : (
              <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center space-x-1">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Demo Fallback</span>
              </span>
            )}
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Configured Provider:</span>
              <span className="font-semibold text-slate-200 uppercase">
                {status?.reverse_image_provider || 'SerpApi'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Social Media Filter:</span>
              <span className="font-semibold text-purple-300">Instagram, X, TikTok, YouTube, Reddit</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">API Key Status:</span>
              <span className="font-mono text-slate-300">
                {status?.reverse_image_api_configured ? 'Configured in backend/.env' : 'Unset (Running in Demo Mode)'}
              </span>
            </div>
          </div>
        </div>

        {/* 3. Blockchain RPC */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Blockchain Network</h3>
                <p className="text-[11px] text-slate-400">Web3 RPC Integration</p>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Connected</span>
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Network:</span>
              <span className="font-semibold text-slate-200">
                {status?.blockchain_network || 'Polygon Amoy Testnet'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Chain ID:</span>
              <span className="font-mono font-semibold text-cyan-300">
                {status?.blockchain_chain_id || 80002}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Signing Mode:</span>
              <span className="font-semibold text-slate-200">Backend Signer Wallet (web3.py)</span>
            </div>
          </div>
        </div>

        {/* 4. Smart Contract Registry */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white">Smart Contract Registry</h3>
                <p className="text-[11px] text-slate-400">FaceMatchRegistry.sol</p>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center space-x-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Active</span>
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Contract Name:</span>
              <span className="font-mono font-semibold text-slate-200">FaceMatchRegistry</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Address:</span>
              <span className="font-mono text-cyan-300 text-[11px] truncate max-w-[200px]">
                {status?.smart_contract_address || '0x98Fc85d03C891C808E5F495493019808381D4bA5'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Compiler Version:</span>
              <span className="font-mono text-slate-200">Solidity 0.8.20</span>
            </div>
          </div>
        </div>

      </div>

      {/* Security & Secrets Notice */}
      <div className="p-4 rounded-2xl bg-indigo-950/20 border border-indigo-500/20 flex items-center space-x-3 text-xs text-indigo-200/90">
        <Lock className="w-5 h-5 text-indigo-400 shrink-0" />
        <div>
          <strong className="font-semibold block text-indigo-200">Security Architecture Notice:</strong>
          <span>Wallet private keys and reverse-search API secrets are managed strictly on the backend. No secrets are ever exposed to the client-side bundle.</span>
        </div>
      </div>
    </div>
  );
};
