import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  X,
  AlertCircle,
  Loader2,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Zap,
} from 'lucide-react';
import { useUpload } from '../hooks/useUpload';

const MAX_FILE_SIZE_MB = 25;
const MAX_FILES = 5;

export default function UploadPage() {
  const navigate = useNavigate();
  const { uploadAsync, startAnalysisAsync, isUploading, isStartingAnalysis } = useUpload();
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(0);

  const processingSteps = [
    { label: 'Uploading proposals...', icon: Upload },
    { label: 'Starting AI analysis...', icon: Sparkles },
    { label: 'Redirecting to dashboard...', icon: Zap },
  ];

  const validateFile = useCallback((file: File): string | null => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return `${file.name}: Only PDF files are accepted.`;
    }
    if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
      return `${file.name}: File exceeds ${MAX_FILE_SIZE_MB}MB limit.`;
    }
    return null;
  }, []);

  const addFiles = useCallback(
    (newFiles: FileList | File[]) => {
      setError(null);
      const incoming = Array.from(newFiles);

      // Validate
      for (const f of incoming) {
        const err = validateFile(f);
        if (err) {
          setError(err);
          return;
        }
      }

      // Check total count
      const combined = [...files, ...incoming];
      if (combined.length > MAX_FILES) {
        setError(`Maximum ${MAX_FILES} files allowed.`);
        return;
      }

      // Deduplicate by name
      const names = new Set(files.map((f) => f.name));
      const unique = incoming.filter((f) => !names.has(f.name));
      setFiles((prev) => [...prev, ...unique]);
    },
    [files, validateFile]
  );

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
    setError(null);
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      if (e.dataTransfer.files.length > 0) {
        addFiles(e.dataTransfer.files);
      }
    },
    [addFiles]
  );

  const handleAnalyze = async () => {
    if (files.length < 1) {
      setError('Please upload at least 1 proposal to analyze.');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      // Step 1: Upload
      setProcessingStep(0);
      const session = await uploadAsync(files);

      // Step 2: Start analysis
      setProcessingStep(1);
      await startAnalysisAsync(session.id);

      // Step 3: Redirect
      setProcessingStep(2);
      await new Promise((r) => setTimeout(r, 500));
      navigate(`/analysis/${session.id}`);
    } catch (err) {
      setIsProcessing(false);
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // ── Processing Overlay ────────────────────────────────────────────
  if (isProcessing) {
    return (
      <div
        style={{
          minHeight: 'calc(100vh - 69px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '32px',
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-card"
          style={{ padding: '48px 64px', textAlign: 'center', maxWidth: '480px' }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
            style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--accent-start), var(--accent-end))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 24px',
            }}
          >
            <Sparkles size={28} color="white" />
          </motion.div>

          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '32px' }}>
            Analyzing Your Proposals
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {processingSteps.map((step, i) => (
              <motion.div
                key={step.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.3 }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-sm)',
                  background:
                    i === processingStep
                      ? 'rgba(99, 102, 241, 0.1)'
                      : i < processingStep
                        ? 'rgba(16, 185, 129, 0.1)'
                        : 'transparent',
                }}
              >
                {i < processingStep ? (
                  <CheckCircle2 size={20} color="var(--status-success)" />
                ) : i === processingStep ? (
                  <Loader2 size={20} color="var(--accent-start)" className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
                ) : (
                  <div
                    style={{
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      border: '2px solid var(--text-muted)',
                    }}
                  />
                )}
                <span
                  style={{
                    fontSize: '0.9rem',
                    color:
                      i <= processingStep ? 'var(--text-primary)' : 'var(--text-muted)',
                    fontWeight: i === processingStep ? 600 : 400,
                  }}
                >
                  {step.label}
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    );
  }

  // ── Upload UI ─────────────────────────────────────────────────────
  return (
    <div
      style={{
        minHeight: 'calc(100vh - 69px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '32px',
      }}
    >
      <div style={{ maxWidth: '680px', width: '100%' }}>
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ textAlign: 'center', marginBottom: '40px' }}
        >
          <h1
            className="font-serif"
            style={{
              fontSize: '3rem',
              fontWeight: 600,
              letterSpacing: '-0.02em',
              lineHeight: 1.2,
              marginBottom: '16px',
              color: 'var(--text-primary)',
            }}
          >
            Compare Agency Proposals
            <br />
            <span style={{ color: 'var(--text-secondary)', fontWeight: 400, fontSize: '1.25rem', fontFamily: 'Inter, sans-serif' }}>
              Upload your proposals and let AI guide your decision
            </span>
          </h1>
        </motion.div>

        {/* Drop Zone */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            onClick={() => {
              const input = document.createElement('input');
              input.type = 'file';
              input.multiple = true;
              input.accept = '.pdf';
              input.onchange = (e) => {
                const target = e.target as HTMLInputElement;
                if (target.files) addFiles(target.files);
              };
              input.click();
            }}
          >
            <motion.div
              animate={dragActive ? { scale: 1.05 } : { scale: 1 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <Upload
                size={48}
                color={dragActive ? 'var(--accent-mid)' : 'var(--text-muted)'}
                style={{ margin: '0 auto 16px', display: 'block' }}
              />
              <p style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                {dragActive ? 'Drop your proposals here' : 'Drag & drop proposal PDFs'}
              </p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                or click to browse · PDF only · max {MAX_FILE_SIZE_MB}MB · up to {MAX_FILES} files
              </p>
            </motion.div>
          </div>
        </motion.div>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              style={{
                marginTop: '16px',
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: 'var(--severity-critical)',
                fontSize: '0.875rem',
              }}
            >
              <AlertCircle size={16} />
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* File List */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '8px' }}
            >
              {files.map((file, i) => (
                <motion.div
                  key={file.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: i * 0.05 }}
                  className="glass-card"
                  style={{
                    padding: '14px 18px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <FileText size={20} color="var(--accent-start)" />
                    <div>
                      <p style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                        {file.name}
                      </p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {formatFileSize(file.size)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(i);
                    }}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '4px',
                      borderRadius: '4px',
                      display: 'flex',
                    }}
                  >
                    <X size={16} color="var(--text-muted)" />
                  </button>
                </motion.div>
              ))}

              {/* Analyze Button */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                style={{ marginTop: '16px', textAlign: 'center' }}
              >
                <button
                  className="btn-accent"
                  onClick={handleAnalyze}
                  disabled={files.length < 1 || isUploading || isStartingAnalysis}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '10px',
                    fontSize: '1rem',
                    padding: '14px 36px',
                  }}
                >
                  <Sparkles size={18} />
                  Analyze {files.length} Proposal{files.length !== 1 ? 's' : ''}
                  <ArrowRight size={18} />
                </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
