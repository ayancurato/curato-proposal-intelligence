import { useState } from 'react';
import { useParams } from 'react-router';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  GitCompareArrows,
  ShieldAlert,
  Award,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { useAnalysis } from '../hooks/useAnalysis';
import OverviewPanel from '../components/OverviewPanel';
import ComparisonTable from '../components/ComparisonTable';
import RiskPanel from '../components/RiskPanel';
import RecommendationPanel from '../components/RecommendationPanel';

const TABS = [
  { key: 'overview', label: 'Overview', icon: LayoutDashboard },
  { key: 'comparison', label: 'Comparison', icon: GitCompareArrows },
  { key: 'risks', label: 'Risks', icon: ShieldAlert },
  { key: 'recommendation', label: 'Recommendation', icon: Award },
] as const;

type TabKey = (typeof TABS)[number]['key'];

export default function DashboardPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { dashboard, status, statusMessage, isComplete, isFailed, isProcessing } =
    useAnalysis(sessionId);
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  // ── Loading / Processing State ─────────────────────────────────
  if (!isComplete || !dashboard) {
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
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="glass-card"
          style={{ padding: '48px 64px', textAlign: 'center', maxWidth: '500px' }}
        >
          {isFailed ? (
            <>
              <AlertCircle
                size={48}
                color="var(--severity-critical)"
                style={{ margin: '0 auto 16px', display: 'block' }}
              />
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '8px' }}>
                Analysis Failed
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                {statusMessage || 'Something went wrong during analysis.'}
              </p>
            </>
          ) : (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                style={{
                  width: '64px',
                  height: '64px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 20px',
                }}
              >
                <img
                  src="/curato-logo.jpg"
                  alt="Loading"
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                />
              </motion.div>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '4px' }}>
                Curato AI
              </h2>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '12px' }}>
                {statusMessage || 'Processing...'}
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Status: <span style={{ color: 'var(--text-accent)' }}>{status}</span>
              </p>
              <div
                style={{
                  marginTop: '24px',
                  height: '4px',
                  background: 'var(--bg-secondary)',
                  borderRadius: '2px',
                  overflow: 'hidden',
                }}
              >
                <motion.div
                  style={{
                    height: '100%',
                    background: 'linear-gradient(90deg, var(--accent-start), var(--accent-end))',
                    borderRadius: '2px',
                  }}
                  initial={{ width: '5%' }}
                  animate={{ width: '90%' }}
                  transition={{ duration: 60, ease: 'linear' }}
                />
              </div>
            </>
          )}
        </motion.div>
      </div>
    );
  }

  // ── Dashboard ──────────────────────────────────────────────────
  return (
    <div style={{ padding: '24px 32px', maxWidth: '1400px', margin: '0 auto' }}>
      {/* Tab Bar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: '24px' }}
      >
        <div className="tab-bar">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              className={`tab-item ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              <tab.icon size={16} />
              {tab.key === 'comparison' && dashboard.proposal_count === 1
                ? 'Proposal Analysis'
                : tab.key === 'recommendation' && dashboard.proposal_count === 1
                ? 'Final Verdict'
                : tab.label}
              {tab.key === 'risks' && dashboard.quick_stats && dashboard.quick_stats.total_risks > 0 && (
                <span
                  style={{
                    fontSize: '0.7rem',
                    padding: '1px 6px',
                    borderRadius: '9999px',
                    background: dashboard.quick_stats.critical_risks > 0
                      ? 'rgba(239, 68, 68, 0.2)'
                      : 'rgba(234, 179, 8, 0.2)',
                    color: dashboard.quick_stats.critical_risks > 0
                      ? 'var(--severity-critical)'
                      : 'var(--severity-medium)',
                  }}
                >
                  {dashboard.quick_stats.total_risks}
                </span>
              )}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {activeTab === 'overview' && <OverviewPanel dashboard={dashboard} />}
        {activeTab === 'comparison' && <ComparisonTable dashboard={dashboard} />}
        {activeTab === 'risks' && <RiskPanel dashboard={dashboard} />}
        {activeTab === 'recommendation' && <RecommendationPanel dashboard={dashboard} />}
      </motion.div>
    </div>
  );
}
