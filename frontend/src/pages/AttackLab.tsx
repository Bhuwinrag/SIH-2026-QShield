import { useState } from 'react';
import { ShieldCheck, Crosshair, RefreshCw, ZapOff } from 'lucide-react';
import { createSession, createExperiment, runExperiment, getExperimentResult, processArtifact } from '../lib/api';
import { ArtifactUploader } from '../components/ArtifactUploader';

export const AttackLab = () => {
  const [activeAttack, setActiveAttack] = useState('FORGERY');
  const [strength, setStrength] = useState(0.5);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Artifact State
  const [isUploading, setIsUploading] = useState(false);
  const [artifactMetadata, setArtifactMetadata] = useState<any>(null);
  const [signer, setSigner] = useState("SIGNER_EVE");
  const [verifier, setVerifier] = useState("VERIFIER_BOB");

  const attacks = [
    { id: 'FORGERY', name: 'FORGERY', icon: <ShieldCheck className="w-4 h-4" /> },
    { id: 'IMPERSONATION', name: 'IMPERSONATION', icon: <Crosshair className="w-4 h-4" /> },
    { id: 'REPLAY', name: 'REPLAY', icon: <RefreshCw className="w-4 h-4" /> },
    { id: 'CHANNEL_MANIPULATION', name: 'CHANNEL MANIPULATION', icon: <ZapOff className="w-4 h-4" /> },
    { id: 'NOISE_ONLY', name: 'NOISE ONLY', icon: <div className="w-4 h-4 border border-current rounded-full opacity-50" /> },
  ];

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    setError(null);
    try {
      const data = await processArtifact(file);
      setArtifactMetadata(data);
    } catch (e: any) {
      console.error("Upload failed", e);
      setError("Artifact upload failed: Backend endpoint not found. Please restart .\\run_backend.bat to apply the new endpoint.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSimulate = async () => {
    if (!artifactMetadata) {
      setError("Please upload a security artifact first.");
      return;
    }

    setIsRunning(true);
    setResult(null);
    setError(null);
    try {
      const session = await createSession(
        signer, 
        verifier, 
        artifactMetadata.message_digest,
        artifactMetadata.artifact_name,
        artifactMetadata.artifact_size,
        artifactMetadata.artifact_type
      );
      const exp = await createExperiment(session.id, 1000, true, activeAttack, strength);
      await runExperiment(exp.id);
      
      setTimeout(async () => {
        try {
            const finalResult = await getExperimentResult(exp.id);
            setResult(finalResult);
        } catch (pollErr: any) {
            setError(pollErr.message || "Failed to fetch simulation results.");
        } finally {
            setIsRunning(false);
        }
      }, 2500);
      
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Simulation failed to start.");
      setIsRunning(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-4xl font-light tracking-widest text-white mb-2">ATTACK LAB</h2>
          <p className="text-q-text-secondary">Simulate controlled threats against the QDS protocol.</p>
        </div>
      </div>

      <div className="w-full flex flex-col gap-2">
        <ArtifactUploader 
          onUpload={handleFileUpload} 
          isUploading={isUploading} 
          metadata={artifactMetadata} 
          signer={signer}
          setSigner={setSigner}
          verifier={verifier}
          setVerifier={setVerifier}
        />
        {error && error.includes("upload failed") && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 font-mono text-sm rounded-lg animate-in fade-in">
            {error}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Attack Selector */}
        <div className="glass-panel p-6 rounded-xl flex flex-col gap-4">
          <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4">THREAT VECTORS</h3>
          
          {attacks.map(atk => (
            <button
              key={atk.id}
              onClick={() => setActiveAttack(atk.id)}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-colors ${
                activeAttack === atk.id 
                  ? 'border-q-accent bg-q-accent/10 text-white' 
                  : 'border-q-border/30 text-q-text-secondary hover:border-q-border'
              }`}
            >
              {atk.icon}
              <span className="font-mono text-xs">{atk.name}</span>
            </button>
          ))}
          
          <div className="mt-4 border-t border-q-border pt-4 flex flex-col gap-2">
            <div className="flex justify-between items-center text-xs font-mono text-q-text-secondary">
              <span>ATTACK STRENGTH</span>
              <span>{strength.toFixed(2)}</span>
            </div>
            <input 
              type="range" 
              min="0.1" 
              max="1.0" 
              step="0.1"
              value={strength}
              onChange={(e) => setStrength(parseFloat(e.target.value))}
              className="w-full accent-q-accent"
            />
          </div>

          <button 
            onClick={handleSimulate}
            disabled={isRunning || !artifactMetadata}
            className={`mt-4 pill-control py-3 font-bold text-sm flex items-center justify-center gap-2 ${isRunning || !artifactMetadata ? 'opacity-50' : 'active'}`}
          >
            {isRunning ? 'SIMULATING ATTACK...' : 'LAUNCH ATTACK'}
          </button>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-3 flex flex-col gap-8">
          <div className="glass-panel p-6 rounded-xl min-h-[500px] flex flex-col">
            <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4 mb-6">SECURITY EVIDENCE VECTOR</h3>
            
            {isRunning ? (
              <div className="flex-1 flex flex-col items-center justify-center gap-4 text-q-text-secondary">
                <div className="w-12 h-12 rounded-full border-t-2 border-l-2 border-q-accent animate-spin"></div>
                <div className="font-mono text-sm tracking-widest">EXECUTING THREAT SIMULATION...</div>
              </div>
            ) : error ? (
              <div className="flex-1 flex items-center justify-center text-red-400 font-mono text-sm">
                SIMULATION ERROR: {error}
              </div>
            ) : result ? (
              <div className="flex flex-col gap-6 animate-in fade-in duration-500">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 border border-q-border rounded-lg">
                    <div className="text-xs text-q-text-secondary font-mono mb-1">DECISION</div>
                    <div className={`text-xl font-mono ${result.threat_event?.decision === 'ACCEPT' ? 'text-q-accent' : 'text-red-400'}`}>
                      {result.threat_event?.decision}
                    </div>
                  </div>
                  <div className="p-4 border border-q-border rounded-lg">
                    <div className="text-xs text-q-text-secondary font-mono mb-1">ATTRIBUTED THREAT</div>
                    <div className={`text-xl font-mono ${result.threat_event?.decision === 'ACCEPT' ? 'text-white' : 'text-red-400'}`}>
                      {result.threat_event?.threat_type === 'ANOMALY_UNATTRIBUTED' ? 'ANOMALY DETECTED ATTRIBUTION UNCERTAIN' : result.threat_event?.threat_type}
                    </div>
                  </div>
                </div>

                <div className="p-4 border border-q-border rounded-lg bg-q-bg">
                  <div className="text-xs text-q-text-secondary font-mono mb-2">PRIMARY EVIDENCE</div>
                  <div className="text-white font-mono text-sm">{result.threat_event?.reason}</div>
                </div>
                
                {result.security_evidence && (
                  <div className="mt-4 border-t border-q-border pt-4">
                    <h4 className="text-xs text-q-text-secondary font-mono mb-4">STATISTICAL ENGINE METRICS</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
                      <div>
                        <div className="text-q-text-secondary mb-1">Max Deviation</div>
                        <div className="text-white">{result.security_evidence.basis_deviation.toFixed(4)}</div>
                      </div>
                      <div>
                        <div className="text-q-text-secondary mb-1">Hoeffding Bound</div>
                        <div className="text-white">{result.security_evidence.bound_threshold.toFixed(4)}</div>
                      </div>
                      <div>
                        <div className="text-q-text-secondary mb-1">Significance</div>
                        <div className="text-red-400">{result.security_evidence.statistical_significance.toFixed(4)}</div>
                      </div>
                      <div>
                        <div className="text-q-text-secondary mb-1">Freshness</div>
                        <div className={result.security_evidence.freshness_status ? "text-q-accent" : "text-red-400"}>
                          {result.security_evidence.freshness_status ? "PASS" : "FAIL"}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-q-text-secondary font-mono text-sm">
                AWAITING SIMULATION
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
