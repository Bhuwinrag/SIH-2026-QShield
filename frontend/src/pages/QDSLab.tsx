import { useState } from 'react';
import { Play, RotateCcw } from 'lucide-react';
import { createSession, createExperiment, runExperiment, getExperimentResult, processArtifact } from '../lib/api';
import { BellStateVisualizer } from '../components/quantum/BellStateVisualizer';
import { ArtifactUploader } from '../components/ArtifactUploader';

export const QDSLab = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  
  const [shots, setShots] = useState(1000);
  const [noiseEnabled, setNoiseEnabled] = useState(true);

  // Artifact State
  const [isUploading, setIsUploading] = useState(false);
  const [artifactMetadata, setArtifactMetadata] = useState<any>(null);
  const [signer, setSigner] = useState("ACME-INDUSTRIAL-ROOT");
  const [verifier, setVerifier] = useState("EDGE-GATEWAY-07");

  const [error, setError] = useState<string | null>(null);

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

  const handleRun = async () => {
    if (!artifactMetadata) {
      alert("Please upload a security artifact first.");
      return;
    }
    
    setIsRunning(true);
    setResult(null);
    try {
      // 1. Create Session
      const session = await createSession(
        signer, 
        verifier, 
        artifactMetadata.message_digest,
        artifactMetadata.artifact_name,
        artifactMetadata.artifact_size,
        artifactMetadata.artifact_type
      );
      
      // 2. Create Experiment (Normal mode only for QDS Lab)
      const exp = await createExperiment(session.id, shots, noiseEnabled, "NORMAL", 0.5);
      
      // 3. Run Experiment
      await runExperiment(exp.id);
      
      // 4. Poll for result
      const pollInterval = setInterval(async () => {
        try {
          const finalResult = await getExperimentResult(exp.id);
          // Check if the simulation worker has finished (threat_event is generated last)
          if (finalResult && finalResult.threat_event) {
            clearInterval(pollInterval);
            setResult(finalResult);
            setIsRunning(false);
          }
        } catch (e) {
          console.error("Polling error", e);
        }
      }, 1000);
      
      // Safety timeout after 30 seconds
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsRunning(false);
      }, 30000);
      
    } catch (e) {
      console.error(e);
      setIsRunning(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col gap-8">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-4xl font-light tracking-widest text-white mb-2">QDS LAB</h2>
          <p className="text-q-text-secondary">Interactive Quantum Digital Signature Protocol Simulation.</p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={handleRun}
            disabled={isRunning || !artifactMetadata}
            className={`pill-control px-6 py-3 font-bold text-sm flex items-center gap-2 ${isRunning || !artifactMetadata ? 'opacity-50 cursor-not-allowed' : 'active'}`}
          >
            {isRunning ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {isRunning ? 'SIMULATING...' : 'VERIFY ARTIFACT'}
          </button>
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
        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 font-mono text-sm rounded-lg animate-in fade-in">
            {error}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Controls */}
        <div className="glass-panel p-6 rounded-xl flex flex-col gap-6 h-fit">
          <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4">PARAMETERS</h3>

          <div className="flex flex-col gap-2">
            <label className="text-xs font-mono text-q-text-secondary">SHOTS</label>
            <input 
              type="number" 
              value={shots}
              onChange={(e) => setShots(parseInt(e.target.value))}
              className="bg-transparent border border-q-border rounded-lg p-2 text-white font-mono focus:border-q-accent outline-none"
            />
          </div>

          <div className="flex items-center justify-between mt-2">
            <label className="text-xs font-mono text-q-text-secondary">ENVIRONMENT NOISE</label>
            <button 
              onClick={() => setNoiseEnabled(!noiseEnabled)}
              className={`w-12 h-6 rounded-full p-1 transition-colors ${noiseEnabled ? 'bg-q-accent' : 'bg-q-border'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-q-bg transition-transform ${noiseEnabled ? 'translate-x-6' : 'translate-x-0'}`}></div>
            </button>
          </div>
        </div>

        {/* Visualization & Results */}
        <div className="lg:col-span-2 flex flex-col gap-8">
          <div className="glass-panel p-6 rounded-xl min-h-[350px]">
            <h3 className="font-mono text-sm tracking-widest text-q-text-secondary mb-4">QUANTUM STATE</h3>
            <BellStateVisualizer correlation={result?.quantum_run?.bell_correlation ?? 1.0} />
          </div>

          {result && (
            <div className="glass-panel p-6 rounded-xl animate-in fade-in slide-in-from-bottom-4 duration-500">
              <h3 className="font-mono text-sm tracking-widest text-q-text-secondary mb-6 border-b border-q-border pb-4">MEASUREMENT RESULTS</h3>
              
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <div className="text-xs text-q-text-secondary mb-1">FIDELITY</div>
                  <div className="text-2xl font-mono text-white">{((result.quantum_run.qmf_observed?.fidelity || 1.0) * 100).toFixed(2)}%</div>
                </div>
                <div>
                  <div className="text-xs text-q-text-secondary mb-1">BELL CORRELATION</div>
                  <div className="text-2xl font-mono text-white">{((result.quantum_run.qmf_observed?.bell?.C_ZZ || 1.0) * 100).toFixed(2)}%</div>
                </div>
                <div>
                  <div className="text-xs text-q-text-secondary mb-1">VERIFICATION</div>
                  <div className={`text-2xl font-mono ${result.threat_event?.decision === 'ACCEPT' ? 'text-q-accent' : 'text-red-400'}`}>
                    {result.threat_event?.decision}
                  </div>
                </div>
              </div>

              {result.threat_event?.decision === 'REJECT' && (
                <div className="mt-6 p-4 rounded bg-red-500/10 border border-red-500/30">
                  <div className="text-red-400 font-mono text-sm mb-2">DETECTED ATTRIBUTION: {result.threat_event.threat_type === 'ANOMALY_UNATTRIBUTED' ? 'ANOMALY DETECTED ATTRIBUTION UNCERTAIN' : result.threat_event.threat_type}</div>
                  <div className="text-q-text-secondary text-sm">{result.threat_event.reason}</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
