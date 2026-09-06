import React from 'react';
import { Home, History, ShieldAlert, Users, Settings } from 'lucide-react';

interface MobileNavProps {
  activeTab: 'dashboard' | 'history' | 'tamper' | 'settings' | 'creator';
  setActiveTab: (tab: 'dashboard' | 'history' | 'tamper' | 'settings' | 'creator') => void;
}

export const MobileNav: React.FC<MobileNavProps> = ({ activeTab, setActiveTab }) => {
  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-[#070B14]/95 backdrop-blur-xl border-t border-slate-800/80 px-2 py-2 safe-area-pb">
      <div className="grid grid-cols-5 gap-1 max-w-md mx-auto text-[10px] font-semibold text-center">
        
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`flex flex-col items-center py-1.5 rounded-xl transition ${
            activeTab === 'dashboard' ? 'text-cyan-400 bg-cyan-500/10' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Home className="w-4 h-4 mb-0.5" />
          <span>Pipeline</span>
        </button>

        <button
          onClick={() => setActiveTab('history')}
          className={`flex flex-col items-center py-1.5 rounded-xl transition ${
            activeTab === 'history' ? 'text-cyan-400 bg-cyan-500/10' : 'text-slate-400 hover:text-white'
          }`}
        >
          <History className="w-4 h-4 mb-0.5" />
          <span>History</span>
        </button>

        <button
          onClick={() => setActiveTab('tamper')}
          className={`flex flex-col items-center py-1.5 rounded-xl transition ${
            activeTab === 'tamper' ? 'text-purple-400 bg-purple-500/10' : 'text-slate-400 hover:text-white'
          }`}
        >
          <ShieldAlert className="w-4 h-4 mb-0.5" />
          <span>Tamper</span>
        </button>

        <button
          onClick={() => setActiveTab('creator')}
          className={`flex flex-col items-center py-1.5 rounded-xl transition ${
            activeTab === 'creator' ? 'text-pink-400 bg-pink-500/10' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Users className="w-4 h-4 mb-0.5" />
          <span>Creator</span>
        </button>

        <button
          onClick={() => setActiveTab('settings')}
          className={`flex flex-col items-center py-1.5 rounded-xl transition ${
            activeTab === 'settings' ? 'text-cyan-400 bg-cyan-500/10' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Settings className="w-4 h-4 mb-0.5" />
          <span>Status</span>
        </button>

      </div>
    </div>
  );
};
