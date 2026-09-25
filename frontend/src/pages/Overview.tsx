import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getHealth } from '../lib/api';
import { Activity, ShieldCheck, Zap, Server, Database, GitMerge } from 'lucide-react';

export const Overview = ({ navigate }: { navigate: (page: string) => void }) => {
  const [health, setHealth] = useState<any>({
    api: { status: "CHECKING" },
    database: { status: "CHECKING" },
    quantum: { status: "CHECKING" },
    redis: { status: "CHECKING" },
    worker: { status: "CHECKING" }
  });

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {
      // Handled by api.ts fallbacks mostly, but just in case
    });
  }, []);

  const pipelineSteps = [
    "QUANTUM STATE",
    "BELL ENTANGLEMENT",
    "TELEPORTATION",
    "PAULI CORRECTION",
    "PROJECTIVE MEASUREMENT",
    "QMF",
    "STATISTICAL EVIDENCE",
    "THREAT ATTRIBUTION"
  ];

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-12">
      {/* Hero Section */}
      <section className="flex flex-col items-start gap-6 py-12">
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.9] text-transparent bg-clip-text bg-gradient-to-br from-white to-q-text-secondary"
        >
          Don't Just Verify.<br />
          <span className="text-q-accent">Explain the Attack.</span>
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-xl text-q-text-secondary max-w-2xl font-light"
        >
          Quantum Signature Security Observatory. From fundamental quantum state verification to deterministic attack attribution using advanced measurement statistics.
        </motion.p>
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="flex gap-4 mt-4"
        >
          <button 
            onClick={() => navigate("attacklab")}
            className="pill-control active px-8 py-4 font-bold tracking-wide text-sm flex items-center gap-2"
          >
            <ShieldCheck className="w-4 h-4" /> ATTACK LAB
          </button>
          <button 
            onClick={() => navigate("demo")}
            className="pill-control px-8 py-4 font-bold tracking-wide text-sm flex items-center gap-2 border-q-accent text-q-accent"
          >
            <Zap className="w-4 h-4" /> RUN LIVE DEMO
          </button>
        </motion.div>
      </section>

      {/* Status Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatusCard title="FASTAPI CORE" status={health.api?.status || "OFFLINE"} icon={<Activity />} />
        <StatusCard title="QUANTUM SIM" status={health.quantum?.status || "OFFLINE"} icon={<Zap />} />
        <StatusCard title="WORKER" status={health.worker?.status === "OFFLINE" ? "ASYNC UNAVAILABLE" : (health.worker?.status || "OFFLINE")} isOptional icon={<GitMerge />} />
        <StatusCard title="POSTGRESQL" status={health.database?.status || "OFFLINE"} icon={<Database />} />
        <StatusCard title="REDIS" status={health.redis?.status === "OFFLINE" ? "OPTIONAL" : (health.redis?.status || "OFFLINE")} isOptional icon={<Server />} />
      </section>

      {/* Visual Pipeline */}
      <section className="glass-panel p-8 rounded-xl border border-q-border/50">
        <h3 className="font-mono text-sm tracking-widest text-q-text-secondary mb-8 border-b border-q-border pb-4">
          Q-SHIELD ATTRIBUTION PIPELINE
        </h3>
        <div className="flex flex-wrap items-center justify-center gap-2 md:gap-4 font-mono text-xs text-white">
          {pipelineSteps.map((step, idx) => (
            <React.Fragment key={step}>
              <div className="px-4 py-2 border border-q-accent/50 bg-q-accent/10 rounded-lg whitespace-nowrap text-q-accent shadow-[0_0_10px_rgba(223,255,188,0.1)]">
                {step}
              </div>
              {idx < pipelineSteps.length - 1 && (
                <div className="text-q-text-secondary animate-pulse">→</div>
              )}
            </React.Fragment>
          ))}
        </div>
      </section>
      
      <div className="h-20"></div>
    </div>
  );
};

const StatusCard = ({ title, status, icon }: { title: string, status: string, icon: React.ReactNode, isOptional?: boolean }) => {
  const isOnline = status === "ONLINE" || status === "READY" || status === "ACTIVE";
  const isWarning = status === "OPTIONAL" || status === "ASYNC UNAVAILABLE";
  
  return (
    <div className="glass-panel p-6 flex flex-col gap-4 rounded-xl border border-q-border/30 hover:border-q-accent/30 transition-colors">
      <div className="flex justify-between items-center text-q-text-secondary">
        <span className="text-sm font-mono tracking-widest">{title}</span>
        {icon}
      </div>
      <div className="flex items-center gap-3">
        <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-q-accent shadow-[0_0_8px_#DFFFBC]' : (isWarning ? 'bg-yellow-500' : 'bg-red-500')}`}></div>
        <span className={`font-mono text-xs md:text-sm ${isOnline ? 'text-white' : (isWarning ? 'text-yellow-400' : 'text-red-400')}`}>{status}</span>
      </div>
    </div>
  );
}
