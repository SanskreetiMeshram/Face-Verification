import React, { useState } from 'react';
import { Globe, ExternalLink, Sparkles, AlertTriangle, ShieldCheck, Check, Database } from 'lucide-react';
import { ReverseSearchResponse, SearchResultItem } from '../types';

interface ReverseSearchCardProps {
  searchData: ReverseSearchResponse | null;
  onRegisterOnChain?: (item: SearchResultItem) => void;
  isRegistering?: boolean;
}

const getPlatformBadge = (platform?: string) => {
  const p = platform?.toLowerCase() || '';
  if (p.includes('instagram')) {
    return {
      name: 'Instagram',
      color: 'bg-gradient-to-r from-pink-500 via-rose-500 to-amber-500 text-white',
      border: 'border-pink-500/30'
    };
  }
  if (p.includes('x') || p.includes('twitter')) {
    return {
      name: 'X (Twitter)',
      color: 'bg-slate-800 text-cyan-300',
      border: 'border-cyan-500/30'
    };
  }
  if (p.includes('tiktok')) {
    return {
      name: 'TikTok',
      color: 'bg-black text-rose-400 border-rose-500',
      border: 'border-rose-500/40'
    };
  }
  if (p.includes('youtube')) {
    return {
      name: 'YouTube',
      color: 'bg-red-600 text-white',
      border: 'border-red-500/40'
    };
  }
  if (p.includes('reddit')) {
    return {
      name: 'Reddit',
      color: 'bg-orange-600 text-white',
      border: 'border-orange-500/40'
    };
  }
  if (p.includes('linkedin')) {
    return {
      name: 'LinkedIn',
      color: 'bg-blue-600 text-white',
      border: 'border-blue-500/40'
    };
  }
  if (p.includes('facebook')) {
    return {
      name: 'Facebook',
      color: 'bg-blue-700 text-white',
      border: 'border-blue-500/40'
    };
  }
  return {
    name: platform || 'Web Match',
    color: 'bg-slate-800 text-slate-300',
    border: 'border-slate-700'
  };
};

export const ReverseSearchCard: React.FC<ReverseSearchCardProps> = ({
  searchData,
  onRegisterOnChain,
  isRegistering = false,
}) => {
  const [confirmItem, setConfirmItem] = useState<SearchResultItem | null>(null);

  if (!searchData) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col items-center justify-center min-h-[300px] text-center text-slate-500">
        <Globe className="w-12 h-12 text-slate-700 mb-3 animate-pulse" />
        <p className="text-sm font-semibold text-slate-400">Reverse Image Search Pending</p>
        <p className="text-xs text-slate-600 mt-1">Queries configured search provider for visually matching public content</p>
      </div>
    );
  }

  const match = searchData.primary_match;
  const badge = getPlatformBadge(match?.platform);

  return (
    <div className="glass-panel p-6 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
      {/* Background glow decoration */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Card Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800/80">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <Globe className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Reverse Image Search</h3>
            <p className="text-xs text-slate-400">Provider: {searchData.provider}</p>
          </div>
        </div>

        {searchData.is_demo_mode && (
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Demo Data • Not Live Search
          </span>
        )}
      </div>

      {searchData.demo_badge_message && (
        <div className="mb-4 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
          <span>{searchData.demo_badge_message}</span>
        </div>
      )}

      {/* Main Matched Result Card */}
      {match ? (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              {match.thumbnail && (
                <div className="w-20 h-20 shrink-0 rounded-lg overflow-hidden border border-slate-700 bg-black">
                  <img
                    src={match.thumbnail}
                    alt={match.title || "Matched reverse search thumbnail"}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              <div className="flex-1 min-w-0 space-y-1.5">
                <div className="flex items-center space-x-2">
                  <span className={`px-2.5 py-0.5 text-xs font-bold rounded-md shadow-sm border ${badge.color} ${badge.border}`}>
                    {badge.name}
                  </span>
                  {match.similarity ? (
                    <span className="text-[11px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                      {match.similarity}
                    </span>
                  ) : (
                    <span className="text-[10px] text-slate-500 font-mono">
                      Provider did not supply a numerical confidence score
                    </span>
                  )}
                </div>

                <h4 className="text-sm font-bold text-white truncate">
                  {match.title || 'Potential Matching Public Content Discovered'}
                </h4>

                <p className="text-xs text-slate-400 font-mono truncate">
                  Domain: {match.domain}
                </p>
              </div>

              <div className="shrink-0 w-full sm:w-auto flex flex-col gap-2">
                <a
                  href={match.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full sm:w-auto inline-flex items-center justify-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 hover:border-cyan-400 transition"
                >
                  <span>Open Source</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>

                {onRegisterOnChain && (
                  <button
                    onClick={() => setConfirmItem(match)}
                    disabled={isRegistering}
                    className="w-full sm:w-auto inline-flex items-center justify-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-semibold bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 transition disabled:opacity-50"
                  >
                    <Database className="w-3.5 h-3.5" />
                    <span>Use for Blockchain Record</span>
                  </button>
                )}
              </div>
            </div>

            {/* Matched URL full display */}
            <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center space-x-2">
              <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                Discovered URL:
              </span>
              <span className="text-xs font-mono text-slate-300 truncate select-all">
                {match.url}
              </span>
            </div>
          </div>

          {/* Transparent Match Disclaimer */}
          <p className="text-[11px] text-slate-500 italic leading-relaxed">
            * Note: Potential matching public content discovered. This does not prove person identity or account ownership. The blockchain record stores a cryptographic fingerprint of discovered metadata, not personal identity.
          </p>
        </div>
      ) : (
        <div className="p-6 rounded-xl bg-slate-900/40 border border-slate-800 text-center space-y-2">
          <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
          <h4 className="text-sm font-semibold text-slate-300">No Matching Public Result Found</h4>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            The reverse-search query returned no suitable public web or social content. The system does not fabricate artificial results.
          </p>
        </div>
      )}

      {/* Confirmation Dialog Modal */}
      {confirmItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="glass-panel max-w-md w-full p-6 rounded-2xl border border-slate-700 shadow-2xl space-y-4">
            <div className="flex items-center space-x-2 text-emerald-400">
              <ShieldCheck className="w-6 h-6" />
              <h3 className="text-base font-bold text-white">Blockchain Registration Confirmation</h3>
            </div>
            
            <p className="text-xs text-slate-300 leading-relaxed">
              Register this discovered content fingerprint on the blockchain?
            </p>

            <div className="p-3 rounded-lg bg-black/50 border border-slate-800 space-y-1 text-[11px] font-mono text-slate-400">
              <div className="truncate"><span className="text-slate-500">Title:</span> {confirmItem.title}</div>
              <div className="truncate"><span className="text-slate-500">URL:</span> {confirmItem.url}</div>
              <div><span className="text-slate-500">Domain:</span> {confirmItem.domain}</div>
            </div>

            <p className="text-[11px] text-slate-500 italic">
              Only a SHA-256 cryptographic metadata fingerprint will be recorded on-chain. No raw biometric face data is stored.
            </p>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setConfirmItem(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (onRegisterOnChain) {
                    onRegisterOnChain(confirmItem);
                  }
                  setConfirmItem(null);
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 transition"
              >
                Register on Blockchain
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
