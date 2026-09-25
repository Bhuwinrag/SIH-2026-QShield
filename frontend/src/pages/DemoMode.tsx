import { useState } from 'react';
import { Play, ShieldAlert, CheckCircle, RefreshCw } from 'lucide-react';
import { createSession, createExperiment, runExperiment, getExperimentResult, processArtifact } from '../lib/api';
import { ArtifactUploader } from '../components/ArtifactUploader';

const DEMO_STAGES = [
  { id: "NORMAL", name: "LEGITIMATE + NOISE", type: "NORMAL", strength: 0.05, noise: true },
  { id: "FORGERY", name: "FORGERY ATTACK", type: "FORGERY", strength: 0.8, noise: true },
  { id: "REPLAY", name: "REPLAY ATTACK", type: "REPLAY", strength: 1.0, noise: true },
  { id: "CHANNEL_MANIPULATION", name: "CHANNEL MANIPULATION", type: "CHANNEL_MANIPULATION", strength: 0.9, noise: true },
];

export const DemoMode = () => {
  const [activeStageIndex, setActiveStageIndex] = useState(-1);
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Artifact State
  const [isUploading, setIsUploading] = useState(false);
  const [artifactMetadata, setArtifactMetadata] = useState<any>(null);
  const [signer, setSigner] = useState("SIGNER_ALICE");
  const [verifier, setVerifier] = useState("VERIFIER_BOB");

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

  const runDemoSequence = async () => {
    if (!artifactMetadata) {
      setError("Please upload a legitimate security artifact to begin the demo sequence.");
      return;
    }

    setIsRunning(true);
    setResults([]);
    setError(null);
    setActiveStageIndex(0);

    for (let i = 0; i < DEMO_STAGES.length; i++) {
      setActiveStageIndex(i);
      const stage = DEMO_STAGES[i];
      try {
        const session = await createSession(
          signer, 
          verifier, 
          artifactMetadata.message_digest,
          artifactMetadata.artifact_name,
          artifactMetadata.artifact_size,
          artifactMetadata.artifact_type
        );
        const exp = await createExperiment(session.id, 2000, stage.noise, stage.type, stage.strength);
        await runExperiment(exp.id);
        
        // Wait for worker to finish (demo mode delay)
        await new Promise(resolve => setTimeout(resolve, 2500));
        
        const res = await getExperimentResult(exp.id);
        setResults(prev => [...prev, { ...stage, result: res }]);
        
      } catch (err: any) {
        let msg = err.message || 'Backend unreachable';
        if (err.response && err.response.data && err.response.data.detail) {
            msg = err.response.data.detail;
        }
        setError(`SIMULATION ERROR: ${msg}`);
        setIsRunning(false);
        return;
      }
      
      // Pause between stages for effect
      await new Promise(resolve => setTimeout(resolve, 1500));
    }
    
    setIsRunning(false);
    setActiveStageIndex(DEMO_STAGES.length); // Complete
  };

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-4xl font-light tracking-widest text-white mb-2">Q-SHIELD LIVE DEMONSTRATION</h2>
          <p className="text-q-text-secondary">Deterministic demonstration of Q-SHIELD threat attribution.</p>
        </div>
        <button 
          onClick={runDemoSequence}
          disabled={isRunning || !artifactMetadata}
          className={`pill-control px-8 py-3 font-bold text-sm flex items-center gap-2 ${isRunning || !artifactMetadata ? 'opacity-50 cursor-not-allowed' : 'active border-q-accent text-q-accent'}`}
        >
          {isRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {isRunning ? 'EXECUTING SEQUENCE...' : 'RUN LIVE DEMO'}
        </button>
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
        {error && (
          <div className="glass-panel p-6 border-red-500 bg-red-500/10 text-red-400 font-mono flex items-center gap-4">
            <ShieldAlert /> {error}
          </div>
        )}
      </div>

      <div className="flex flex-col gap-6 mt-8">
        {DEMO_STAGES.map((stage, idx) => {
          const isActive = idx === activeStageIndex;
          const isComplete = idx < activeStageIndex || results.length > idx;
          const resultData = results.find(r => r.id === stage.id)?.result;

          return (
            <div 
              key={stage.id} 
              className={`glass-panel p-6 rounded-xl border transition-all duration-500 ${isActive ? 'border-q-accent shadow-[0_0_15px_rgba(223,255,188,0.2)]' : isComplete ? 'border-q-border' : 'border-transparent opacity-40'}`}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-mono tracking-widest text-white text-lg flex items-center gap-3">
                  <span className="text-q-accent text-sm">0{idx + 1}</span> {stage.name}
                </h3>
                {isActive && <div className="text-q-accent font-mono text-sm flex items-center gap-2"><RefreshCw className="w-4 h-4 animate-spin" /> SIMULATING</div>}
                {isComplete && resultData && <div className="text-q-text-secondary font-mono text-sm flex items-center gap-2"><CheckCircle className="w-4 h-4" /> COMPLETED</div>}
              </div>

              {resultData && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6 animate-in fade-in duration-500">
                  <div className="p-4 bg-q-bg rounded-lg border border-q-border text-center">
                    <div className="text-xs text-q-text-secondary font-mono mb-2">EXPECTED TV DEVIATION</div>
                    <div className="text-white font-mono">{resultData.security_evidence?.bound_threshold?.toFixed(4) || "0.0000"}</div>
                  </div>
                  <div className="p-4 bg-q-bg rounded-lg border border-q-border text-center">
                    <div className="text-xs text-q-text-secondary font-mono mb-2">OBSERVED MAX DEVIATION</div>
                    <div className={`font-mono ${resultData.security_evidence?.statistical_significance > resultData.security_evidence?.bound_threshold ? 'text-red-400' : 'text-q-accent'}`}>
                      {resultData.security_evidence?.statistical_significance?.toFixed(4) || "0.0000"}
                    </div>
                  </div>
                  <div className="p-4 bg-q-bg rounded-lg border border-q-border text-center">
                    <div className="text-xs text-q-text-secondary font-mono mb-2">ATTRIBUTED THREAT</div>
                    <div className={`font-mono ${resultData.threat_event?.threat_type === 'NORMAL' ? 'text-q-accent' : 'text-red-400'}`}>
                      {resultData.threat_event?.threat_type === 'ANOMALY_UNATTRIBUTED' ? 'ANOMALY DETECTED ATTRIBUTION UNCERTAIN' : resultData.threat_event?.threat_type}
                    </div>
                  </div>
                  <div className="p-4 bg-q-bg rounded-lg border border-q-border text-center">
                    <div className="text-xs text-q-text-secondary font-mono mb-2">DECISION</div>
                    <div className={`font-mono ${resultData.threat_event?.decision === 'ACCEPT' ? 'text-q-accent' : 'text-red-400'}`}>
                      {resultData.threat_event?.decision}
                    </div>
                  </div>
                  <div className="md:col-span-4 p-4 bg-q-bg rounded-lg border border-q-border">
                    <div className="text-xs text-q-text-secondary font-mono mb-2">EVIDENCE REASONING</div>
                    <div className="text-white font-mono text-sm">{resultData.threat_event?.reason}</div>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {activeStageIndex === DEMO_STAGES.length && (
          <div className="mt-8 text-center text-q-accent font-mono tracking-widest text-xl animate-pulse">
            DEMONSTRATION COMPLETE
          </div>
        )}
      </div>
    </div>
  );
};
