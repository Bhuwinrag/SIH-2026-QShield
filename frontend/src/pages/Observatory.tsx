import { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { getLatestExperiment } from '../lib/api';

export const Observatory = () => {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTelemetry = async () => {
      try {
        const latest = await getLatestExperiment();
        setData(latest);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'No live session available');
      }
    };
    
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 3000);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <div className="flex items-end justify-between mb-4">
        <div>
          <h2 className="text-4xl font-light tracking-widest text-white mb-2">OBSERVATORY</h2>
          <p className="text-q-text-secondary">Global Quantum Channel & Threat Monitoring.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Telemetry panel */}
        <div className="glass-panel p-6 rounded-xl flex flex-col gap-6">
          <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4 flex justify-between items-center">
            CHANNEL STATUS <Activity className="w-4 h-4 text-q-accent" />
          </h3>
          
          {data?.session?.artifact_name && (
            <div className="flex flex-col gap-2 p-3 bg-q-bg border border-q-border rounded-lg mb-2">
              <div className="text-xs font-mono text-q-text-secondary">ARTIFACT</div>
              <div className="text-sm font-mono text-white truncate" title={data.session.artifact_name}>{data.session.artifact_name}</div>
              <div className="text-xs font-mono text-q-accent truncate mt-1">SHA: {data.session.message_digest.substring(0, 16)}...</div>
            </div>
          )}
          
          {error ? (
            <div className="flex-1 flex items-center justify-center text-q-text-secondary font-mono tracking-widest text-sm h-full py-12">
              WAITING FOR LIVE SESSION
            </div>
          ) : data?.quantum_run ? (
            <>
              <div className="flex flex-col gap-4">
                 <div>
                    <div className="flex justify-between text-xs font-mono text-q-text-secondary mb-1">
                      <span>BELL CORRELATION (C_ZZ)</span>
                      <span>{(data.quantum_run.qmf_observed.bell?.C_ZZ * 100 || 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-1 w-full bg-q-bg rounded overflow-hidden">
                      <div className="h-full bg-q-accent transition-all duration-500" style={{ width: `${Math.max(0, (data.quantum_run.qmf_observed.bell?.C_ZZ || 1) * 100)}%` }}></div>
                    </div>
                 </div>
                 <div>
                    <div className="flex justify-between text-xs font-mono text-q-text-secondary mb-1">
                      <span>FIDELITY</span>
                      <span>{((data.quantum_run.qmf_observed?.fidelity || 1.0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-1 w-full bg-q-bg rounded overflow-hidden">
                      <div className="h-full bg-q-accent transition-all duration-500" style={{ width: `${(data.quantum_run.qmf_observed?.fidelity || 1.0) * 100}%` }}></div>
                    </div>
                 </div>
                 <div>
                    <div className="flex justify-between text-xs font-mono text-q-text-secondary mb-1">
                      <span>DISTURBANCE (MAX TV)</span>
                      <span className={data.threat_event?.decision === 'REJECT' ? 'text-red-400' : 'text-q-accent'}>
                        {(data.security_evidence?.basis_deviation * 100 || 0).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-1 w-full bg-q-bg rounded overflow-hidden">
                      <div className="h-full bg-red-400 transition-all duration-500" style={{ width: `${Math.min(100, (data.security_evidence?.basis_deviation || 0) * 100)}%` }}></div>
                    </div>
                 </div>
              </div>
              
              <div className="mt-4 p-4 bg-q-bg border border-q-border rounded-lg flex items-center justify-between">
                <span className="text-xs font-mono tracking-widest text-q-text-secondary">GLOBAL STATUS</span>
                <span className={`text-sm font-mono tracking-widest ${data.threat_event?.decision === 'REJECT' ? 'text-red-400 animate-pulse' : 'text-q-accent'}`}>
                  {data.threat_event?.decision === 'REJECT' ? 'THREAT DETECTED' : 'STABLE'}
                </span>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-q-text-secondary font-mono tracking-widest text-sm h-full py-12">
              AWAITING EXPERIMENT DATA
            </div>
          )}
        </div>

        {/* QMF Visualizer */}
        <div className="lg:col-span-3 flex flex-col gap-8">
          <div className="glass-panel p-6 rounded-xl min-h-[500px]">
             <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4 mb-8">QUANTUM MEASUREMENT FINGERPRINT</h3>
             
             {!data || error ? (
                <div className="col-span-2 md:col-span-3 text-center py-12 text-q-text-secondary font-mono tracking-widest">
                  WAITING FOR LIVE SESSION
                </div>
             ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
                  <DistributionChart basis="X" errorRate={(data.quantum_run.qmf_observed.basis?.X?.tv_distance || 0) * 100} distribution={data.quantum_run.qmf_observed.basis?.X?.distribution} />
                  <DistributionChart basis="Y" errorRate={(data.quantum_run.qmf_observed.basis?.Y?.tv_distance || 0) * 100} distribution={data.quantum_run.qmf_observed.basis?.Y?.distribution} />
                  <DistributionChart basis="Z" errorRate={(data.quantum_run.qmf_observed.basis?.Z?.tv_distance || 0) * 100} distribution={data.quantum_run.qmf_observed.basis?.Z?.distribution} />
                </div>
             )}
             
             <div className="mt-12 p-6 border border-q-border/50 rounded-xl bg-q-bg/50">
               <h4 className="text-xs font-mono tracking-widest text-q-text-secondary mb-4">BASELINE VS OBSERVED</h4>
               <div className="flex flex-col gap-4">
                 <div className="flex items-center gap-4 text-xs font-mono">
                   <div className="w-3 h-3 rounded-sm bg-q-accent/30 border border-q-accent"></div>
                   <span className="text-q-text-secondary">Expected Legitimate Envelope</span>
                 </div>
                 <div className="flex items-center gap-4 text-xs font-mono">
                   <div className="w-3 h-3 rounded-sm bg-white"></div>
                   <span className="text-white">Current Session Trajectory</span>
                 </div>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const DistributionChart = ({ basis, errorRate, distribution }: { basis: string, errorRate: number, distribution?: Record<string, number> }) => {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <span className="font-mono text-lg text-white">{basis} BASIS</span>
        <span className="font-mono text-xs text-q-text-secondary">TV: {errorRate.toFixed(2)}%</span>
      </div>
      <div className="h-32 flex items-end gap-1">
        {distribution ? (
          Object.entries(distribution).map(([state, prob]) => (
            <div key={state} className="flex-1 flex flex-col justify-end items-center group relative">
              <div className="w-full bg-q-accent/20 border-t border-q-accent/50 rounded-t-sm transition-all duration-300" style={{ height: `${Math.max(2, prob * 100)}%` }}></div>
              <span className="absolute -bottom-5 text-[8px] text-q-text-secondary font-mono opacity-0 group-hover:opacity-100">{state}</span>
            </div>
          ))
        ) : (
          Array.from({ length: 16 }).map((_, i) => (
            <div key={i} className="flex-1 bg-q-border/20 border-t border-q-border/50 rounded-t-sm" style={{ height: '5%' }}></div>
          ))
        )}
      </div>
    </div>
  )
}
