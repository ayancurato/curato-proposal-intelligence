import { motion } from 'framer-motion';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts';
import { GitCompareArrows, ChevronDown, ChevronUp, DollarSign } from 'lucide-react';
import { useState } from 'react';
import type { DashboardResponse } from '../services/api';

interface Props {
  dashboard: DashboardResponse;
}

// Color palette for agencies
const AGENCY_COLORS = ['#061535', '#06b6d4', '#f59e0b', '#ef4444', '#10b981'];

export default function ComparisonTable({ dashboard }: Props) {
  const comparison = dashboard.comparison;
  const [expandedDim, setExpandedDim] = useState<string | null>(null);

  if (!comparison) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center' }}>
        <p style={{ color: 'var(--text-muted)' }}>
          Comparison data is not available. Upload at least 2 proposals.
        </p>
      </div>
    );
  }

  // Prepare radar chart data
  const radarData = comparison.dimensions.map((dim) => {
    const entry: Record<string, string | number> = { dimension: dim.dimension };
    comparison.agency_names.forEach((name) => {
      entry[name] = dim.scores[name] ?? 0;
    });
    return entry;
  });

  const formatCurrency = (val: number | null | undefined) => {
    if (val == null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  return (
    <div>
      {/* Radar Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
        style={{ padding: '24px', marginBottom: '24px' }}
      >
        <h3
          style={{
            fontSize: '1rem',
            fontWeight: 700,
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <GitCompareArrows size={18} color="var(--accent-start)" />
          {dashboard.proposal_count === 1 ? 'Multi-Dimension Analysis' : 'Multi-Dimension Comparison'}
        </h3>
        <div style={{ width: '100%', height: '400px' }}>
          <ResponsiveContainer>
            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="var(--glass-border)" />
              <PolarAngleAxis
                dataKey="dimension"
                tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 10]}
                tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
              />
              {comparison.agency_names.map((name, i) => (
                <Radar
                  key={name}
                  name={name}
                  dataKey={name}
                  stroke={AGENCY_COLORS[i % AGENCY_COLORS.length]}
                  fill={AGENCY_COLORS[i % AGENCY_COLORS.length]}
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
              ))}
              <Legend
                wrapperStyle={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Pricing Comparison */}
      {comparison.pricing_comparison && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card"
          style={{ padding: '24px', marginBottom: '24px' }}
        >
          <h3
            style={{
              fontSize: '1rem',
              fontWeight: 700,
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <DollarSign size={18} color="var(--status-success)" />
            Pricing Breakdown
          </h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px',
              marginBottom: '16px',
            }}
          >
            {Object.entries(comparison.pricing_comparison.pricing_breakdown || {}).map(
              ([agency, cost], i) => {
                const maxCost = Math.max(
                  ...Object.values(comparison.pricing_comparison.pricing_breakdown || {})
                );
                const pct = maxCost > 0 ? (cost / maxCost) * 100 : 0;

                return (
                  <div key={agency}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginBottom: '6px',
                      }}
                    >
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 500 }}>
                        {agency}
                      </span>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>
                        {formatCurrency(cost)}
                      </span>
                    </div>
                    <div className="score-bar">
                      <motion.div
                        className="score-bar-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ delay: 0.3 + i * 0.1, duration: 0.6 }}
                        style={{
                          background: `${AGENCY_COLORS[i % AGENCY_COLORS.length]}`,
                        }}
                      />
                    </div>
                  </div>
                );
              }
            )}
          </div>
          {comparison.pricing_comparison.value_reasoning && (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {comparison.pricing_comparison.value_reasoning}
            </p>
          )}
        </motion.div>
      )}

      {/* Dimension-by-Dimension */}
      <h3
        style={{
          fontSize: '1rem',
          fontWeight: 700,
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        Dimension Analysis
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {comparison.dimensions.map((dim, i) => (
          <motion.div
            key={dim.dimension}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 + i * 0.05 }}
            className="glass-card"
            style={{
              padding: '16px 20px',
              cursor: 'pointer',
              borderRadius: 'var(--radius-md)',
            }}
            onClick={() => setExpandedDim(expandedDim === dim.dimension ? null : dim.dimension)}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '8px',
                  }}
                >
                  <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{dim.dimension}</span>
                  {dim.leader && (
                    <span className="badge badge-info" style={{ fontSize: '0.65rem' }}>
                      Leader: {dim.leader}
                    </span>
                  )}
                </div>
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                  {Object.entries(dim.scores).map(([agency, score], j) => (
                    <div key={agency} style={{ minWidth: '120px' }}>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          fontSize: '0.75rem',
                          marginBottom: '4px',
                        }}
                      >
                        <span style={{ color: 'var(--text-muted)' }}>{agency}</span>
                        <span style={{ fontWeight: 600 }}>
                          {score != null ? `${score}/10` : 'Not Mentioned'}
                        </span>
                      </div>
                      <div className="score-bar" style={{ height: '6px' }}>
                        <motion.div
                          className="score-bar-fill"
                          initial={{ width: 0 }}
                          animate={{ width: score != null ? `${(score / 10) * 100}%` : '0%' }}
                          transition={{ delay: 0.3 }}
                          style={{
                            background: score != null ? AGENCY_COLORS[j % AGENCY_COLORS.length] : 'var(--glass-border)',
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ marginLeft: '12px' }}>
                {expandedDim === dim.dimension ? (
                  <ChevronUp size={18} color="var(--text-muted)" />
                ) : (
                  <ChevronDown size={18} color="var(--text-muted)" />
                )}
              </div>
            </div>

            {/* Expanded Analysis */}
            {expandedDim === dim.dimension && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                style={{
                  marginTop: '16px',
                  paddingTop: '16px',
                  borderTop: '1px solid var(--glass-border)',
                }}
              >
                <p
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.7,
                    marginBottom: '12px',
                  }}
                >
                  {dim.analysis}
                </p>
                {dim.key_differences.length > 0 && (
                  <div>
                    <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                      KEY DIFFERENCES
                    </p>
                    <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                      {dim.key_differences.map((diff, k) => (
                        <li
                          key={k}
                          style={{
                            fontSize: '0.8rem',
                            color: 'var(--text-secondary)',
                            padding: '4px 0',
                            paddingLeft: '12px',
                            borderLeft: '2px solid var(--accent-start)',
                            marginBottom: '4px',
                          }}
                        >
                          {diff}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Head-to-Head Insights */}
      {comparison.head_to_head && comparison.head_to_head.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="glass-card"
          style={{ marginTop: '24px', padding: '24px' }}
        >
          <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px' }}>
            {dashboard.proposal_count === 1 ? 'Proposal Highlights' : 'Head-to-Head Insights'}
          </h3>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {comparison.head_to_head.map((insight, i) => (
              <li
                key={i}
                style={{
                  fontSize: '0.85rem',
                  color: 'var(--text-secondary)',
                  padding: '8px 0',
                  borderBottom:
                    i < comparison.head_to_head.length - 1
                      ? '1px solid var(--glass-border)'
                      : 'none',
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
