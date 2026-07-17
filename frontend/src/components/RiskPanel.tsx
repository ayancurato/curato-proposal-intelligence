import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  Filter,
} from 'lucide-react';
import type { DashboardResponse, Risk } from '../services/api';

interface Props {
  dashboard: DashboardResponse;
}

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };
const SEVERITY_CONFIG: Record<
  string,
  { icon: typeof AlertCircle; color: string; badge: string }
> = {
  critical: { icon: AlertCircle, color: 'var(--severity-critical)', badge: 'badge-critical' },
  high: { icon: AlertTriangle, color: 'var(--severity-high)', badge: 'badge-high' },
  medium: { icon: Info, color: 'var(--severity-medium)', badge: 'badge-medium' },
  low: { icon: CheckCircle, color: 'var(--severity-low)', badge: 'badge-low' },
};

export default function RiskPanel({ dashboard }: Props) {
  const riskAnalysis = dashboard.risk_analysis;
  const [expandedRisk, setExpandedRisk] = useState<string | null>(null);
  const [filterAgency, setFilterAgency] = useState<string | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string | null>(null);

  if (!riskAnalysis || riskAnalysis.analyses.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center' }}>
        <ShieldAlert size={48} color="var(--text-muted)" style={{ margin: '0 auto 16px', display: 'block' }} />
        <p style={{ color: 'var(--text-muted)' }}>No risk analysis available yet.</p>
      </div>
    );
  }

  // Flatten and sort risks
  type EnrichedRisk = Risk & { agency_name: string; proposal_id: string };
  const allRisks: EnrichedRisk[] = riskAnalysis.analyses
    .flatMap((a) =>
      a.risks.map((r) => ({
        ...r,
        agency_name: a.agency_name,
        proposal_id: a.proposal_id,
      }))
    )
    .filter((r) => !filterAgency || r.agency_name === filterAgency)
    .filter((r) => !filterSeverity || r.severity === filterSeverity)
    .sort(
      (a, b) =>
        (SEVERITY_ORDER[a.severity as keyof typeof SEVERITY_ORDER] ?? 4) -
        (SEVERITY_ORDER[b.severity as keyof typeof SEVERITY_ORDER] ?? 4)
    );


  return (
    <div>
      {/* Risk Summary Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        {riskAnalysis.analyses.map((analysis, i) => (
          <motion.div
            key={analysis.proposal_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="stat-card"
            style={{
              cursor: 'pointer',
              border: filterAgency === analysis.agency_name
                ? '1px solid var(--accent-start)'
                : undefined,
            }}
            onClick={() =>
              setFilterAgency(
                filterAgency === analysis.agency_name ? null : analysis.agency_name
              )
            }
          >
            <p className="stat-label">{analysis.agency_name}</p>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
              <p
                className="stat-value"
                style={{
                  color:
                    analysis.risk_score > 60
                      ? 'var(--severity-critical)'
                      : analysis.risk_score > 40
                        ? 'var(--severity-high)'
                        : analysis.risk_score > 20
                          ? 'var(--severity-medium)'
                          : 'var(--severity-low)',
                }}
              >
                {analysis.risk_score}
              </p>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>/ 100 risk score</span>
            </div>
            <p className="stat-sub">{analysis.risks.length} risk(s) identified</p>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          marginBottom: '16px',
          flexWrap: 'wrap',
        }}
      >
        <Filter size={16} color="var(--text-muted)" />
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: '8px' }}>
          Filter:
        </span>
        {['critical', 'high', 'medium', 'low'].map((sev) => {
          const config = SEVERITY_CONFIG[sev];
          const count = allRisks.filter((r) => r.severity === sev).length;
          return (
            <button
              key={sev}
              className={`badge ${config.badge}`}
              onClick={() => setFilterSeverity(filterSeverity === sev ? null : sev)}
              style={{
                cursor: 'pointer',
                opacity: filterSeverity && filterSeverity !== sev ? 0.4 : 1,
              }}
            >
              {sev} ({count})
            </button>
          );
        })}
        {(filterAgency || filterSeverity) && (
          <button
            onClick={() => {
              setFilterAgency(null);
              setFilterSeverity(null);
            }}
            style={{
              fontSize: '0.75rem',
              color: 'var(--text-accent)',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              textDecoration: 'underline',
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {/* Risk Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <AnimatePresence>
          {allRisks.map((risk, i) => {
            const config = SEVERITY_CONFIG[risk.severity] || SEVERITY_CONFIG.low;
            const SeverityIcon = config.icon;
            const key = `${risk.proposal_id}-${risk.title}-${i}`;
            const isExpanded = expandedRisk === key;

            return (
              <motion.div
                key={key}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ delay: i * 0.03 }}
                className="glass-card"
                style={{
                  padding: '16px 20px',
                  cursor: 'pointer',
                  borderRadius: 'var(--radius-md)',
                  borderLeft: `3px solid ${config.color}`,
                }}
                onClick={() => setExpandedRisk(isExpanded ? null : key)}
              >
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '12px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                    <SeverityIcon size={18} color={config.color} />
                    <div>
                      <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '2px' }}>
                        {risk.title}
                      </p>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <span className={`badge ${config.badge}`} style={{ fontSize: '0.6rem' }}>
                          {risk.severity}
                        </span>
                        <span
                          style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}
                        >
                          {risk.agency_name}
                        </span>
                        {risk.affected_section && (
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            &middot; {risk.affected_section}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  {isExpanded ? (
                    <ChevronUp size={16} color="var(--text-muted)" />
                  ) : (
                    <ChevronDown size={16} color="var(--text-muted)" />
                  )}
                </div>

                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    style={{
                      marginTop: '16px',
                      paddingTop: '16px',
                      borderTop: '1px solid var(--glass-border)',
                    }}
                  >
                    <div style={{ marginBottom: '12px' }}>
                      <p
                        style={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          color: 'var(--text-muted)',
                          marginBottom: '4px',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        Explanation
                      </p>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                        {risk.explanation}
                      </p>
                    </div>

                    {risk.business_impact && (
                      <div style={{ marginBottom: '12px' }}>
                        <p
                          style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: 'var(--text-muted)',
                            marginBottom: '4px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                          }}
                        >
                          Business Impact
                        </p>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                          {risk.business_impact}
                        </p>
                      </div>
                    )}

                    {risk.why_it_matters && (
                      <div style={{ marginBottom: '16px' }}>
                        <p
                          style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: 'var(--text-muted)',
                            marginBottom: '4px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                          }}
                        >
                          Why It Matters
                        </p>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                          {risk.why_it_matters}
                        </p>
                      </div>
                    )}
                    <div
                      style={{
                        padding: '12px 16px',
                        borderRadius: 'var(--radius-sm)',
                        background: 'rgba(99, 102, 241, 0.08)',
                        border: '1px solid rgba(99, 102, 241, 0.15)',
                      }}
                    >
                      <p
                        style={{
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          color: 'var(--text-accent)',
                          marginBottom: '4px',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        Suggested Action
                      </p>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                        {risk.suggested_action}
                      </p>
                    </div>
                  </motion.div>
                )}
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Comparative Insights */}
      {riskAnalysis.comparative_insights && riskAnalysis.comparative_insights.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="glass-card"
          style={{ marginTop: '24px', padding: '24px' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>
            Comparative Risk Insights
          </h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {riskAnalysis.comparative_insights.map((insight, i) => (
              <li
                key={i}
                style={{
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                  padding: '8px 0 8px 12px',
                  borderLeft: '2px solid var(--accent-start)',
                  marginBottom: '8px',
                  lineHeight: 1.6,
                }}
              >
                {insight}
              </li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
}
