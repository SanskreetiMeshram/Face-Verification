import React, { useState, useEffect } from 'react';
import { Activity, ShieldCheck, ShieldAlert, Smartphone, Laptop, Download, RefreshCw, Database, Globe, Share2, Copy, Check, Users, FileSpreadsheet, FileCode } from 'lucide-react';

export const CreatorDashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [copiedShareLink, setCopiedShareLink] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setIsLoading(true);
      const res = await fetch('/api/admin/activity');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to load admin stats:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const copyShareLink = () => {
    const url = window.location.origin;
    navigator.clipboard.writeText(url);
    setCopiedShareLink(true);
    setTimeout(() => setCopiedShareLink(false), 2500);
  };

  const handleExport = (format: 'json' | 'csv') => {
    window.open(`/api/admin/export?format=${format}`, '_blank');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-semibold mb-1.5">
            <Users className="w-3.5 h-3.5 text-purple-400" />
            <span>Creator Master Control Room</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Live Activity & Backend Audit Trail
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time tracking of all uploads, scans, device types, and blockchain verifications across all users.
          </p>
        </div>

        <div className="flex items-center space-x-2.5">
          <button
            onClick={copyShareLink}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center space-x-1.5 transition"
          >
            {copiedShareLink ? <Check className="w-4 h-4 text-emerald-400" /> : <Share2 className="w-4 h-4" />}
            <span>{copiedShareLink ? 'Link Copied!' : 'Share App Link'}</span>
          </button>

          <button
            onClick={loadStats}
            disabled={isLoading}
            className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center space-x-1.5 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Total Pipeline Scans
          </span>
          <p className="text-2xl sm:text-3xl font-black text-cyan-400">
            {stats?.total_scans ?? 0}
          </p>
          <span className="text-[10px] text-slate-500 mt-1 block">Full verification cycles executed</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            On-Chain Registrations
          </span>
          <p className="text-2xl sm:text-3xl font-black text-emerald-400">
            {stats?.total_blockchain_records ?? 0}
          </p>
          <span className="text-[10px] text-slate-500 mt-1 block">Persistent Polygon Amoy records</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Tampering Interceptions
          </span>
          <p className="text-2xl sm:text-3xl font-black text-rose-400">
            {stats?.tamper_incidents_caught ?? 0}
          </p>
          <span className="text-[10px] text-slate-500 mt-1 block">Tampered evidence mismatches caught</span>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800 relative overflow-hidden">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
            Total Logged Events
          </span>
          <p className="text-2xl sm:text-3xl font-black text-purple-400">
            {stats?.total_events ?? 0}
          </p>
          <span className="text-[10px] text-slate-500 mt-1 block">Persistent SQLite audit entries</span>
        </div>

      </div>

      {/* Device & Platform Breakdown Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Device Types */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Smartphone className="w-4 h-4 text-cyan-400" />
            <span>User Devices Connected</span>
          </h3>

          <div className="space-y-2.5">
            {stats?.device_breakdown && Object.keys(stats.device_breakdown).length > 0 ? (
              Object.entries(stats.device_breakdown).map(([device, count]: [string, any]) => (
                <div key={device} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                  <span className="text-slate-300 font-semibold">{device}</span>
                  <span className="font-mono text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded border border-cyan-500/20">
                    {count} events
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 italic">No device telemetry recorded yet.</p>
            )}
          </div>
        </div>

        {/* Export Data Box */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between space-y-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Download className="w-4 h-4 text-emerald-400" />
              <span>Download & Export Audit Records</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Download the entire persistent database containing all evidence hashes, timestamps, submitter wallets, and search outcomes for offline evaluation.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <button
              onClick={() => handleExport('json')}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-500/30 flex items-center justify-center space-x-2 transition"
            >
              <FileCode className="w-4 h-4" />
              <span>Export as JSON</span>
            </button>
            <button
              onClick={() => handleExport('csv')}
              className="px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-emerald-300 border border-emerald-500/30 flex items-center justify-center space-x-2 transition"
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>Export as CSV</span>
            </button>
          </div>
        </div>

      </div>

      {/* Real-time Activity Stream Table */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-purple-400" />
            <h3 className="text-sm font-bold text-white">Live Activity Stream</h3>
          </div>
          <span className="text-[10px] font-mono text-slate-400">
            Latest 50 Persistent Events
          </span>
        </div>

        {stats?.recent_logs && stats.recent_logs.length > 0 ? (
          <div className="space-y-2.5 overflow-x-auto">
            {stats.recent_logs.map((log: any) => (
              <div
                key={log.id}
                className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 text-[10px] font-mono font-bold rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      {log.event_type}
                    </span>
                    <span
                      className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                        log.status === 'SUCCESS' || log.status === 'VERIFIED'
                          ? 'bg-emerald-500/20 text-emerald-300'
                          : 'bg-rose-500/20 text-rose-300'
                      }`}
                    >
                      {log.status}
                    </span>
                    {log.platform && (
                      <span className="px-2 py-0.5 text-[10px] font-semibold rounded bg-slate-800 text-slate-300">
                        {log.platform}
                      </span>
                    )}
                  </div>
                  <p className="text-slate-300 font-medium truncate max-w-lg">
                    {log.message || log.matched_url || 'Activity event recorded'}
                  </p>
                  <div className="flex items-center space-x-3 text-[10px] font-mono text-slate-500">
                    <span>Device: {log.device_type}</span>
                    <span>•</span>
                    <span>IP: {log.client_ip || '127.0.0.1'}</span>
                    {log.record_id && (
                      <>
                        <span>•</span>
                        <span>Record #{log.record_id}</span>
                      </>
                    )}
                  </div>
                </div>

                <span className="text-[10px] font-mono text-slate-400 shrink-0 self-end sm:self-center">
                  {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 italic text-center py-6">
            No activity events recorded yet. Run a verification to populate the log.
          </p>
        )}
      </div>

    </div>
  );
};
