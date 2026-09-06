import React, { useState, useEffect } from 'react';
import { History, Search, ExternalLink, ShieldCheck, ChevronRight, Filter, Globe, Database } from 'lucide-react';
import { getHistory } from '../services/api';
import { RecordDetail } from './RecordDetail';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<any | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [platformFilter, setPlatformFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setIsLoading(true);
      const res = await getHistory();
      setHistory(res.history || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  if (selectedRecord) {
    return (
      <RecordDetail
        record={selectedRecord}
        onBack={() => setSelectedRecord(null)}
      />
    );
  }

  const filtered = history.filter((item) => {
    const matchesSearch =
      searchTerm === '' ||
      item.record_id.toString().includes(searchTerm) ||
      item.platform?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.evidence_hash?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.result_url?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesPlatform =
      platformFilter === 'ALL' ||
      item.platform?.toUpperCase() === platformFilter.toUpperCase();

    return matchesSearch && matchesPlatform;
  });

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center space-x-2.5">
            <History className="w-6 h-6 text-cyan-400" />
            <span>Verification Registry History</span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Immutable face match records written to the blockchain
          </p>
        </div>

        <button
          onClick={loadHistory}
          className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
        >
          Refresh Records
        </button>
      </div>

      {/* Filters & Search Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Record #, hash, platform, or URL..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-slate-200 placeholder-slate-500 text-xs focus:outline-none focus:border-cyan-400"
          />
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-slate-200 text-xs focus:outline-none focus:border-cyan-400"
          >
            <option value="ALL">All Platforms</option>
            <option value="INSTAGRAM">Instagram</option>
            <option value="X (TWITTER)">X (Twitter)</option>
            <option value="TIKTOK">TikTok</option>
            <option value="YOUTUBE">YouTube</option>
            <option value="REDDIT">Reddit</option>
            <option value="LINKEDIN">LinkedIn</option>
          </select>
        </div>
      </div>

      {/* History Records Table / Cards */}
      {isLoading ? (
        <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center text-slate-500 text-xs">
          Loading blockchain records...
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-panel p-12 rounded-2xl border border-slate-800 text-center space-y-3">
          <Database className="w-12 h-12 text-slate-700 mx-auto animate-pulse" />
          <h4 className="text-sm font-bold text-slate-300">No Verification Records Found</h4>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {history.length === 0
              ? 'Run your first image verification in the Pipeline Dashboard to register evidence on-chain.'
              : 'No records matched your search query.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div
              key={item.record_id}
              onClick={() => setSelectedRecord(item)}
              className="glass-panel p-4 sm:p-5 rounded-2xl border border-slate-800 hover:border-cyan-500/40 cursor-pointer transition-all duration-200 hover:shadow-lg hover:shadow-cyan-500/5 group flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
            >
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-300 flex items-center justify-center font-mono font-bold text-sm shrink-0">
                  #{item.record_id}
                </div>

                <div className="space-y-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 text-xs font-bold rounded bg-slate-800 text-white border border-slate-700">
                      {item.platform || 'Instagram'}
                    </span>
                    <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 flex items-center space-x-1">
                      <ShieldCheck className="w-3 h-3" />
                      <span>Verified On-Chain</span>
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 truncate max-w-md font-mono">
                    {item.result_url || 'https://instagram.com/p/...'}
                  </p>

                  <div className="flex items-center space-x-3 text-[11px] text-slate-500 font-mono">
                    <span>Hash: {item.evidence_hash ? `${item.evidence_hash.slice(0, 10)}...${item.evidence_hash.slice(-6)}` : '0x...'}</span>
                    <span>•</span>
                    <span>{item.chain_name || 'Polygon Amoy'}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-3 self-end sm:self-center shrink-0">
                <span className="text-xs text-slate-400 group-hover:text-cyan-400 font-semibold flex items-center space-x-1">
                  <span>View Details</span>
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
