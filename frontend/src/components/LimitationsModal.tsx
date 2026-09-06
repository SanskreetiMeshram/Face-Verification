import React from 'react';
import { X, AlertTriangle, ShieldCheck, Lock, Globe, Scale, Cpu, Database } from 'lucide-react';

interface LimitationsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LimitationsModal: React.FC<LimitationsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="glass-panel w-full max-w-3xl rounded-2xl border border-slate-700/80 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/60">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">
                Known Limitations & Privacy Guarantees
              </h3>
              <p className="text-xs text-slate-400">
                Ethical AI, cryptographic verification bounds, and responsible disclosure
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content Scrollable */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm text-slate-300 leading-relaxed">
          
          {/* Privacy Model */}
          <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/20 space-y-2">
            <div className="flex items-center space-x-2 text-indigo-300 font-bold">
              <ShieldCheck className="w-5 h-5 text-indigo-400" />
              <span>1. Zero Biometric Storage on Public Blockchain</span>
            </div>
            <p className="text-xs text-indigo-200/80">
              Raw photos and facial embedding vectors are processed in ephemeral memory and are <strong>never stored on the public blockchain</strong>. Only deterministic SHA-256 evidence fingerprints and verified search metadata are registered on-chain.
            </p>
          </div>

          {/* Probabilistic Nature */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center space-x-2">
              <Scale className="w-4 h-4 text-cyan-400" />
              <span>2. Visual Similarity vs. Real-World Identity</span>
            </h4>
            <p className="text-xs text-slate-400">
              Facial embeddings and reverse-image search results are <strong>probabilistic</strong>. Visual similarity returned by an image search engine indicates that a visually matching photo was indexed on the web. It does <strong>not</strong> prove that the subject in the photo owns or controls the target social media profile.
            </p>
          </div>

          {/* Blockchain Verification Scope */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center space-x-2">
              <Database className="w-4 h-4 text-emerald-400" />
              <span>3. Blockchain Immutability Scope</span>
            </h4>
            <p className="text-xs text-slate-400">
              A blockchain record provides a cryptographically tamper-evident proof that a specific piece of evidence (the SHA-256 hash) was observed and registered at a specific block timestamp. It does not independently verify the authenticity or copyright of the underlying photo itself.
            </p>
          </div>

          {/* Search Indexing & Platform Restrictions */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center space-x-2">
              <Globe className="w-4 h-4 text-purple-400" />
              <span>4. Web Indexing & Social Media Restrictions</span>
            </h4>
            <p className="text-xs text-slate-400">
              Reverse-image search coverage depends on third-party provider indexing (e.g. Google Lens, Bing Visual Search). Private profiles, protected tweets, and platforms with strict robots.txt or anti-scraping policies may not return indexed results.
            </p>
          </div>

          {/* Rate Limits */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center space-x-2">
              <Lock className="w-4 h-4 text-amber-400" />
              <span>5. API Rate Limits & Provider Configuration</span>
            </h4>
            <p className="text-xs text-slate-400">
              Live queries require valid provider API credentials (e.g. SerpApi or Azure Bing Visual Search). When credentials are not supplied or rate limits are reached, the system will transparently inform the user and will never invent fake search matches.
            </p>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-black transition"
          >
            I Understand & Agree
          </button>
        </div>

      </div>
    </div>
  );
};
