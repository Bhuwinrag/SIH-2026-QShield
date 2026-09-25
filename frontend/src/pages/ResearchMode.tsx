import { useState } from 'react';
import { Beaker, Search, RefreshCw } from 'lucide-react';
import { getExperimentResult, getLatestExperiment } from '../lib/api';

export const ResearchMode = () => {
  const [experimentId, setExperimentId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchExperiment = async () => {
    if (!experimentId) return;
    setIsLoading(true);
    setError('');
    try {
      const data = await getExperimentResult(experimentId);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to fetch experiment.");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLatest = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await getLatestExperiment();
      setExperimentId(data.experiment.id);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "No recent experiments found.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-4xl font-light tracking-widest text-white mb-2 flex items-center gap-4">
            <Beaker className="w-8 h-8 text-q-accent" />
            RESEARCH MODE
          </h2>
          <p className="text-q-text-secondary">Inspect Quantum Measurement Fingerprints (QMF) and statistical hypothesis tests.</p>
        </div>
      </div>

      <div className="glass-panel p-6 rounded-xl flex gap-4 items-center">
        <input 
          type="text" 
          placeholder="ENTER EXPERIMENT ID" 
          value={experimentId}
          onChange={(e) => setExperimentId(e.target.value)}
          className="flex-1 bg-q-bg border border-q-border rounded-lg px-4 py-3 text-white font-mono text-sm focus:outline-none focus:border-q-accent"
        />
        <button 
          onClick={fetchExperiment}
          disabled={isLoading || !experimentId}
          className="pill-control active py-3 px-8 font-bold text-sm flex items-center gap-2"
        >
          {isLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          LOAD BY ID
        </button>
        <button 
          onClick={fetchLatest}
          disabled={isLoading}
          className="pill-control py-3 px-8 font-bold text-sm flex items-center gap-2 border-q-accent text-q-accent"
        >
          LOAD LATEST
        </button>
      </div>

      {error && (
        <div className="p-4 border border-red-500/50 bg-red-500/10 text-red-400 font-mono text-sm rounded-lg">
          {error}
        </div>
      )}

      {result && result.quantum_run && (
        <div className="flex flex-col gap-8 animate-in fade-in duration-500">
          
          {/* Artifact Context Panel */}
          {result.session && result.session.artifact_name && (
            <div className="glass-panel p-6 rounded-xl border border-q-border">
              <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4 mb-6">
                SECURITY ARTIFACT CONTEXT
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 font-mono text-sm">
                <div className="flex flex-col gap-1">
                  <span className="text-q-text-secondary text-xs">ARTIFACT</span>
                  <span className="text-white truncate">{result.session.artifact_name}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-q-text-secondary text-xs">SHA-256 DIGEST</span>
                  <span className="text-q-accent truncate" title={result.session.message_digest}>{result.session.message_digest.substring(0, 16)}...</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-q-text-secondary text-xs">SIGNER</span>
                  <span className="text-white">{result.session.signer_id}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-q-text-secondary text-xs">VERIFIER</span>
                  <span className="text-white">{result.session.verifier_id}</span>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* STAGE 1: H0 Evaluation */}
            <div className="glass-panel p-6 rounded-xl border border-q-border">
              <h3 className="font-mono text-sm tracking-widest text-q-accent border-b border-q-border pb-4 mb-6">
                STAGE 1: LEGITIMATE BASELINE DEVIATION (H0)
              </h3>
              
              <div className="grid grid-cols-3 gap-4 font-mono text-xs text-q-text-secondary mb-4">
                <div>BASIS</div>
                <div>TV DISTANCE</div>
                <div>SIGNIFICANT?</div>
              </div>

              {['X', 'Y', 'Z'].map(basis => {
                const basisData = result.quantum_run.qmf_observed.basis[basis];
                return (
                  <div key={basis} className="grid grid-cols-3 gap-4 font-mono text-sm text-white py-3 border-b border-q-border/50">
                    <div className="text-q-accent">{basis}</div>
                    <div>{basisData?.tv_distance?.toFixed(4) || "0.0000"}</div>
                    <div className={basisData?.significant ? "text-red-400" : "text-white"}>
                      {basisData?.significant ? "YES (> BOUND)" : "NO"}
                    </div>
                  </div>
                );
              })}
              
              <div className="mt-6 p-4 bg-q-bg rounded-lg">
                <div className="text-xs text-q-text-secondary font-mono mb-2">HOEFFDING RADIUS ENVELOPE</div>
                <div className="text-white font-mono">
                  ε = {result.quantum_run.qmf_observed.basis['X']?.confidence_radius?.toFixed(5) || "0.0000"} 
                  <span className="text-q-text-secondary ml-2">(Bonferroni Corrected)</span>
                </div>
              </div>
            </div>

            {/* STAGE 2: Threat Attribution */}
            <div className="glass-panel p-6 rounded-xl border border-q-border">
              <h3 className="font-mono text-sm tracking-widest text-q-accent border-b border-q-border pb-4 mb-6">
                STAGE 2: ATTACK HYPOTHESIS
              </h3>
              
              <div className="mb-6">
                <div className="text-xs text-q-text-secondary font-mono mb-1">DECISION</div>
                <div className={`text-2xl font-mono ${result.threat_event.decision === 'ACCEPT' ? 'text-q-accent' : 'text-red-400'}`}>
                  {result.threat_event.threat_type === 'ANOMALY_UNATTRIBUTED' ? 'ANOMALY DETECTED ATTRIBUTION UNCERTAIN' : result.threat_event.threat_type}
                </div>
              </div>

              <div className="p-4 border border-q-border rounded-lg bg-q-bg mb-6">
                <div className="text-xs text-q-text-secondary font-mono mb-2">REASONING</div>
                <div className="text-white font-mono text-sm">{result.threat_event.reason}</div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-q-text-secondary font-mono mb-1">STATE FIDELITY</div>
                  <div className="text-white font-mono text-lg">{((result.quantum_run.qmf_observed?.fidelity || 1.0) * 100).toFixed(2)}%</div>
                </div>
                <div>
                  <div className="text-xs text-q-text-secondary font-mono mb-1">BELL CORRELATION (C_ZZ)</div>
                  <div className="text-white font-mono text-lg">{result.quantum_run.qmf_observed.bell?.C_ZZ?.toFixed(4) || "1.0000"}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Full QMF Dump */}
          <div className="glass-panel p-6 rounded-xl border border-q-border">
            <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4 mb-6">
              RAW QUANTUM MEASUREMENT FINGERPRINT (QMF)
            </h3>
            <pre className="text-xs font-mono text-q-accent bg-[#0A0D0B] p-4 rounded-lg overflow-x-auto">
              {JSON.stringify(result.quantum_run.qmf_observed, null, 2)}
            </pre>
          </div>

        </div>
      )}
    </div>
  );
};
