import { useState } from 'react';
import { Overview } from './pages/Overview';
import { QDSLab } from './pages/QDSLab';
import { Observatory } from './pages/Observatory';
import { AttackLab } from './pages/AttackLab';
import { ResearchMode } from './pages/ResearchMode';
import { DemoMode } from './pages/DemoMode';
import { Shield } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen text-q-text-primary flex flex-col relative overflow-hidden">
      {/* Top Navigation */}
      <header className="glass-panel sticky top-0 z-50 flex items-center justify-between px-8 py-4 border-b border-q-border">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
          <Shield className="w-6 h-6 text-q-accent" />
          <h1 className="text-xl font-bold tracking-widest text-white">Q-SHIELD</h1>
        </div>
        
        <nav className="flex gap-4">
          <button 
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'overview' ? 'text-q-accent' : 'text-q-text-secondary hover:text-white'}`}
          >
            OVERVIEW
          </button>
          <button 
            onClick={() => setActiveTab('qdslab')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'qdslab' ? 'text-q-accent' : 'text-q-text-secondary hover:text-white'}`}
          >
            QDS LAB
          </button>
          <button 
            onClick={() => setActiveTab('attacklab')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'attacklab' ? 'text-q-accent' : 'text-q-text-secondary hover:text-white'}`}
          >
            ATTACK LAB
          </button>
          <button 
            onClick={() => setActiveTab('research')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'research' ? 'text-q-accent' : 'text-q-text-secondary hover:text-white'}`}
          >
            RESEARCH MODE
          </button>
          <button 
            onClick={() => setActiveTab('observatory')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'observatory' ? 'text-q-accent' : 'text-q-text-secondary hover:text-white'}`}
          >
            OBSERVATORY
          </button>
          <button 
            onClick={() => setActiveTab('demo')}
            className={`px-4 py-2 text-sm font-medium transition-colors border border-q-border rounded-full ${activeTab === 'demo' ? 'text-q-accent border-q-accent' : 'text-q-accent hover:bg-q-accent hover:text-black'}`}
          >
            LIVE DEMO
          </button>
        </nav>
        
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-q-accent animate-pulse shadow-[0_0_8px_#DFFFBC]"></div>
          <span className="text-xs font-mono text-q-text-secondary tracking-wider">SYSTEM ONLINE</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto">
        {activeTab === 'overview' && <Overview navigate={setActiveTab} />}
        {activeTab === 'qdslab' && <QDSLab />}
        {activeTab === 'attacklab' && <AttackLab />}
        {activeTab === 'research' && <ResearchMode />}
        {activeTab === 'observatory' && <Observatory />}
        {activeTab === 'demo' && <DemoMode />}
      </main>
    </div>
  );
}

export default App;
