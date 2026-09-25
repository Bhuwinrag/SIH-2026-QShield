import React, { useCallback, useRef } from 'react';
import { Upload, FileText } from 'lucide-react';

interface ArtifactMetadata {
  artifact_name: string;
  artifact_size: number;
  artifact_type: string;
  message_digest: string;
}

interface ArtifactUploaderProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
  metadata: ArtifactMetadata | null;
  signer: string;
  setSigner: (val: string) => void;
  verifier: string;
  setVerifier: (val: string) => void;
}

export const ArtifactUploader: React.FC<ArtifactUploaderProps> = ({
  onUpload,
  isUploading,
  metadata,
  signer,
  setSigner,
  verifier,
  setVerifier
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onUpload(e.dataTransfer.files[0]);
    }
  }, [onUpload]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(e.target.files[0]);
      e.target.value = '';
    }
  }, [onUpload]);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const [processingStep, setProcessingStep] = React.useState(0);

  React.useEffect(() => {
    if (isUploading) {
      setProcessingStep(0);
      const interval = setInterval(() => {
        setProcessingStep(prev => (prev < 3 ? prev + 1 : prev));
      }, 2500);
      return () => clearInterval(interval);
    }
  }, [isUploading]);

  const steps = [
    "EXTRACTING ARTIFACT METADATA...",
    "CALCULATING EXACT BYTE DIGEST...",
    "VERIFYING LOCAL INTEGRITY...",
    "SECURING ARTIFACT HASH..."
  ];

  return (
    <div className="glass-panel p-6 rounded-xl flex flex-col gap-6 w-full">
      <h3 className="font-mono text-sm tracking-widest text-q-text-secondary border-b border-q-border pb-4">SECURITY ARTIFACT</h3>
      
      <div 
        className="border-2 border-dashed border-q-border hover:border-q-accent transition-colors rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer relative min-h-[200px]"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          className="hidden" 
          onChange={handleChange}
          onClick={(e) => e.stopPropagation()}
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center gap-4 text-q-text-secondary font-mono">
            <Upload className="w-8 h-8 animate-bounce text-q-accent" /> 
            <div className="animate-pulse tracking-widest text-sm">{steps[processingStep]}</div>
          </div>
        ) : metadata ? (
          <div className="flex flex-col items-center text-center gap-2 w-full">
            <FileText className="w-8 h-8 text-q-accent mb-2" />
            <div className="text-white font-mono font-bold truncate max-w-full">{metadata.artifact_name}</div>
            <div className="text-q-text-secondary text-xs font-mono">{(metadata.artifact_size / 1024).toFixed(2)} KB • {metadata.artifact_type}</div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-4 text-q-text-secondary hover:text-white transition-colors">
            <Upload className="w-8 h-8" />
            <span className="font-mono text-sm">Drop Artifact PDF Here or Click to Browse</span>
          </div>
        )}
      </div>

      {metadata && (
        <div className="flex flex-col gap-4 bg-q-bg p-4 rounded border border-q-border font-mono text-xs animate-in fade-in">
          <div className="flex flex-col gap-1">
            <span className="text-q-text-secondary">SHA-256 DIGEST</span>
            <span className="text-q-accent break-all">{metadata.message_digest}</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
            <div className="flex flex-col gap-1">
              <label className="text-q-text-secondary">SIGNER</label>
              <input 
                type="text" 
                value={signer}
                onChange={(e) => setSigner(e.target.value)}
                className="bg-transparent border border-q-border rounded p-2 text-white focus:border-q-accent outline-none"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-q-text-secondary">VERIFIER</label>
              <input 
                type="text" 
                value={verifier}
                onChange={(e) => setVerifier(e.target.value)}
                className="bg-transparent border border-q-border rounded p-2 text-white focus:border-q-accent outline-none"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
