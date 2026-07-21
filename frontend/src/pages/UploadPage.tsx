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
  FolderOpen,
  Scale,
  ShieldCheck,
  BarChart2,
  FileCheck
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
    <div style={{ position: 'relative', width: '100%', minHeight: 'calc(100vh - 65px)', overflowX: 'hidden' }}>
      {/* Background decorations for Upload Page */}
      <div style={{
        position: 'absolute', top: '10%', left: '5%', width: '300px', height: '300px',
        backgroundImage: 'radial-gradient(#cbd5e1 2px, transparent 2px)',
        backgroundSize: '24px 24px', opacity: 0.4, zIndex: 0
      }} />
      <div style={{
        position: 'absolute', top: '-10%', right: '-5%', width: '800px', height: '800px',
        borderRadius: '50%', border: '1px solid rgba(15, 181, 168, 0.1)', zIndex: 0
      }} />
      <div style={{
        position: 'absolute', top: '-5%', right: '0%', width: '600px', height: '600px',
        borderRadius: '50%', border: '1px solid rgba(15, 181, 168, 0.15)', zIndex: 0
      }} />
      
      <div
        style={{
          position: 'relative',
          zIndex: 1,
          maxWidth: '1080px',
          margin: '0 auto',
          padding: '48px 24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ textAlign: 'center', marginBottom: '40px', width: '100%' }}
        >
          <h1
            className="font-serif"
            style={{
              fontSize: '3.5rem',
              fontWeight: 600,
              letterSpacing: '-0.02em',
              lineHeight: 1.2,
              marginBottom: '16px',
              color: '#061535',
            }}
          >
            Compare Agency Proposals
          </h1>
          <div style={{ width: '48px', height: '3px', background: '#0fb5a8', margin: '0 auto 24px', borderRadius: '2px' }} />
          <p style={{ color: '#475569', fontWeight: 400, fontSize: '1.1rem', fontFamily: 'Inter, sans-serif' }}>
            Upload your proposal to get in-depth analysis and feedback
          </p>
        </motion.div>

        {/* Drop Zone Container */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{ width: '100%', maxWidth: '780px' }}
        >
          <div
            className={`drop-zone ${dragActive ? 'active' : ''}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            style={{
              background: '#ffffff',
              border: `1.5px dashed ${dragActive ? '#0fb5a8' : '#94a3b8'}`,
              borderRadius: '20px',
              padding: '48px',
              textAlign: 'center',
              boxShadow: '0 20px 40px -12px rgba(14, 42, 92, 0.05)',
              transition: 'all 0.2s ease',
            }}
          >
            <motion.div
              animate={dragActive ? { scale: 1.02 } : { scale: 1 }}
              transition={{ type: 'spring', stiffness: 300 }}
              style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}
            >
              <div style={{
                width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(15, 181, 168, 0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px'
              }}>
                <Upload size={28} color="#0fb5a8" />
              </div>
              <p style={{ fontSize: '1.2rem', fontWeight: 600, color: '#061535', marginBottom: '8px' }}>
                {dragActive ? 'Drop your proposals here' : 'Drag & drop proposal PDFs'}
              </p>
              <p style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '24px' }}>
                or click to browse · PDF only · max {MAX_FILE_SIZE_MB}MB · up to {MAX_FILES} files
              </p>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
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
                style={{
                  background: '#061535',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '12px 28px',
                  fontSize: '0.95rem',
                  fontWeight: 500,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  cursor: 'pointer',
                  boxShadow: '0 4px 12px rgba(6, 21, 53, 0.2)',
                  transition: 'background 0.2s'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = '#0e2a5c'}
                onMouseOut={(e) => e.currentTarget.style.background = '#061535'}
              >
                <FolderOpen size={18} />
                Browse Files
              </button>
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
              style={{ width: '100%', maxWidth: '780px' }}
            >
              <div style={{
                marginTop: '16px',
                padding: '12px 16px',
                borderRadius: '8px',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#ef4444',
                fontSize: '0.875rem',
              }}>
                <AlertCircle size={16} />
                {error}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* File List */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{ width: '100%', maxWidth: '780px', marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '8px' }}
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
                    borderRadius: '12px',
                    background: '#ffffff',
                    boxShadow: '0 2px 8px rgba(14, 42, 92, 0.04)',
                    border: '1px solid rgba(0,0,0,0.05)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <FileText size={20} color="#0fb5a8" />
                    <div>
                      <p style={{ fontSize: '0.9rem', fontWeight: 500, color: '#061535' }}>
                        {file.name}
                      </p>
                      <p style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
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
                    <X size={16} color="#94a3b8" />
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

        {/* Feature Cards Grid (Visible only when no files uploaded to match design purity) */}
        {files.length === 0 && !error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '24px',
              width: '100%',
              marginTop: '48px'
            }}
          >
            {[
              { title: 'Smart Comparison', desc: 'AI compares pricing, scope, timelines, and more side by side.', icon: Scale },
              { title: 'Risk Detection', desc: 'We identify potential risks and red flags in each proposal.', icon: ShieldCheck },
              { title: 'Data-Backed Insights', desc: 'Get a clear breakdown of strengths, gaps, and key differentiators.', icon: BarChart2 },
              { title: 'Executive Recommendation', desc: 'Receive a final recommendation to help you decide with confidence.', icon: FileCheck },
            ].map((feature, idx) => (
              <div key={idx} style={{
                background: '#ffffff',
                borderRadius: '16px',
                padding: '24px',
                boxShadow: '0 4px 24px -10px rgba(14, 42, 92, 0.1)',
                border: '1px solid rgba(0,0,0,0.02)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '16px',
                transition: 'transform 0.2s',
              }}
              onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <div style={{
                  background: 'rgba(15, 181, 168, 0.1)',
                  borderRadius: '50%',
                  width: '48px',
                  height: '48px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <feature.icon size={22} color="#0fb5a8" />
                </div>
                <div style={{ width: '1px', background: '#e2e8f0', alignSelf: 'stretch', margin: '0' }} />
                <div>
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: '#061535', marginBottom: '6px' }}>{feature.title}</h3>
                  <p style={{ fontSize: '0.8rem', color: '#64748b', lineHeight: 1.5 }}>{feature.desc}</p>
                </div>
              </div>
            ))}
          </motion.div>
        )}

        {/* Bottom Banner */}
        {files.length === 0 && !error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            style={{
              width: '100%',
              marginTop: '32px',
              background: 'linear-gradient(90deg, #f0f7ff 0%, #ffffff 100%)',
              borderRadius: '16px',
              padding: '24px 32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              boxShadow: '0 4px 24px -10px rgba(14, 42, 92, 0.1)',
              border: '1px solid rgba(15, 181, 168, 0.1)',
              position: 'relative',
              overflow: 'hidden'
            }}
          >
            {/* Background graphic */}
            <svg style={{ position: 'absolute', bottom: 0, right: '0%', height: '100%', width: '100%', opacity: 0.3, pointerEvents: 'none' }} viewBox="0 0 1000 100" preserveAspectRatio="none">
              <path d="M0,100 C200,80 400,20 1000,50 L1000,100 Z" fill="rgba(15, 181, 168, 0.1)" />
              <path d="M0,100 C300,60 500,40 1000,80 L1000,100 Z" fill="rgba(14, 42, 92, 0.05)" />
            </svg>

            <div style={{ display: 'flex', alignItems: 'center', gap: '24px', zIndex: 1 }}>
              <div style={{
                background: '#061535',
                width: '64px',
                height: '64px',
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                boxShadow: '0 8px 16px rgba(6, 21, 53, 0.2)'
              }}>
                <Sparkles size={28} color="#ffffff" />
              </div>
              <div>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#061535', marginBottom: '4px' }}>
                  AI that understands proposals. Insights that drive better decisions.
                </h2>
                <p style={{ fontSize: '0.9rem', color: '#475569' }}>
                  Curato AI analyzes complex proposals so you can focus on what matters most.
                </p>
              </div>
            </div>
            
            <div style={{ zIndex: 1, alignItems: 'center', paddingRight: '40px' }} className="hidden md:flex">
              <div style={{ position: 'relative' }}>
                <FileText size={56} color="#cbd5e1" strokeWidth={1} />
                <div style={{ position: 'absolute', bottom: '-4px', right: '-8px', background: '#f0f7ff', borderRadius: '50%', padding: '2px' }}>
                  <CheckCircle2 size={24} color="#0fb5a8" fill="white" />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
