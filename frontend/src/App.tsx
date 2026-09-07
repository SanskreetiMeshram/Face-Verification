import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MobileNav } from './components/MobileNav';
import { Dashboard } from './pages/Dashboard';
import { HistoryPage } from './pages/HistoryPage';
import { ComparePage } from './pages/ComparePage';
import { TamperTester } from './components/TamperTester';
import { CreatorDashboard } from './pages/CreatorDashboard';
import { SettingsPage } from './pages/SettingsPage';
import { LimitationsModal } from './components/LimitationsModal';
import { SystemStatusResponse, CanonicalEvidence } from './types';
import { getSystemStatus } from './services/api';
import { ShieldCheck, ExternalLink } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'compare' | 'history' | 'tamper' | 'settings' | 'creator'>('dashboard');
  const [status, setStatus] = useState<SystemStatusResponse | null>(null);
  const [isLimitationsOpen, setIsLimitationsOpen] = useState(false);
  
  // State passed to Tamper Lab when navigated from Dashboard
  const [tamperEvidence, setTamperEvidence] = useState<CanonicalEvidence | null>(null);
  const [tamperRecordId, setTamperRecordId] = useState<number | null>(null);

  useEffect(() => {
    loadSystemStatus();
  }, []);

  const loadSystemStatus = async () => {
    try {
      const res = await getSystemStatus();
      setStatus(res);
    } catch (err) {
      console.warn("Could not load system status:", err);
    }
  };

  const handleNavigateToTamper = (evidence: CanonicalEvidence, recordId: number) => {
    setTamperEvidence(evidence);
    setTamperRecordId(recordId);
    setActiveTab('tamper');
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#070B14] text-slate-100 selection:bg-cyan-500 selection:text-black pb-16 lg:pb-0">
      {/* Top Header */}
      <Header
        status={status}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenLimitations={() => setIsLimitationsOpen(true)}
      />

      {/* Main Page Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8">
        {activeTab === 'dashboard' && (
          <Dashboard
            status={status}
            onNavigateToTamper={handleNavigateToTamper}
          />
        )}

        {activeTab === 'compare' && (
          <ComparePage />
        )}

        {activeTab === 'history' && (
          <HistoryPage />
        )}

        {activeTab === 'tamper' && (
          <div className="max-w-5xl mx-auto space-y-6 pb-16">
            <TamperTester
              initialEvidence={tamperEvidence}
              initialRecordId={tamperRecordId}
            />
          </div>
        )}

        {activeTab === 'creator' && (
          <CreatorDashboard />
        )}

        {activeTab === 'settings' && (
          <SettingsPage
            status={status}
            onRefresh={loadSystemStatus}
          />
        )}
      </main>

      {/* Known Limitations & Privacy Modal */}
      <LimitationsModal
        isOpen={isLimitationsOpen}
        onClose={() => setIsLimitationsOpen(false)}
      />

      {/* Mobile Bottom Navigation Bar */}
      <MobileNav
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#070B14] py-8 text-xs text-slate-500 hidden sm:block">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span className="font-bold text-slate-300">FaceChain Verify Protocol</span>
            <span>•</span>
            <span>Deterministic SHA-256 On-Chain Evidence</span>
          </div>

          <div className="flex items-center space-x-6 text-slate-400">
            <button
              onClick={() => setIsLimitationsOpen(true)}
              className="hover:text-cyan-400 transition"
            >
              Limitations & Privacy
            </button>
            <a
              href="https://amoy.polygonscan.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-cyan-400 transition flex items-center space-x-1"
            >
              <span>Polygonscan</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
