import { motion } from 'framer-motion';
import {
  FileText,
  DollarSign,
  Shield,
  Award,
  Clock,
  AlertTriangle,
  TrendingUp,
} from 'lucide-react';
import type { DashboardResponse } from '../services/api';

interface Props {
  dashboard: DashboardResponse;
}

export default function OverviewPanel({ dashboard }: Props) {
  const stats = dashboard.quick_stats;
  const proposals = dashboard.proposals;

  const formatCurrency = (val: number | null | undefined) => {
    if (val == null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const statCards = [
    {
      label: dashboard.proposal_count === 1 ? 'Health Score' : 'Proposals Analyzed',
      value: dashboard.proposal_count === 1 
        ? (stats?.health_score ? `${stats.health_score}/10` : 'N/A')
        : (stats?.total_proposals ?? proposals.length),
      icon: FileText,
      color: 'var(--accent-start)',
    },
    {
      label: dashboard.proposal_count === 1 ? 'Total Cost' : 'Price Range',
      value: dashboard.proposal_count === 1
        ? (proposals[0]?.extracted_data?.pricing?.total_cost ? formatCurrency(proposals[0].extracted_data.pricing.total_cost) : 'N/A')
        : (stats?.price_range_min != null && stats?.price_range_max != null
          ? `${formatCurrency(stats.price_range_min)} - ${formatCurrency(stats.price_range_max)}`
          : 'N/A'),
      icon: DollarSign,
      color: 'var(--status-success)',
    },
    {
      label: 'Total Risks',
      value: stats?.total_risks ?? 0,
      sub: stats?.critical_risks
        ? `${stats.critical_risks} critical`
        : undefined,
      icon: Shield,
      color:
        (stats?.critical_risks ?? 0) > 0
          ? 'var(--severity-critical)'
          : 'var(--severity-low)',
    },
    {
      label: dashboard.proposal_count === 1 ? 'Proposal Status' : 'Recommended',
      value: dashboard.proposal_count === 1 
        ? (dashboard.recommendation?.proposal_readiness ?? 'Pending') 
        : (stats?.recommended_agency ?? 'Pending'),
      sub: stats?.confidence_level
        ? `Confidence: ${stats.confidence_level}`
        : undefined,
      icon: Award,
      color: 'var(--accent-mid)',
    },
  ];

  return (
    <div>
      {/* Stat Cards Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '16px',
          marginBottom: '32px',
        }}
      >
        {statCards.map((card, i) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="stat-card"
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <p className="stat-label">{card.label}</p>
                <p
                  className="stat-value"
                  style={{
                    fontSize: typeof card.value === 'string' && card.value.length > 10 ? '1.2rem' : undefined,
                  }}
                >
                  {card.value}
                </p>
                {card.sub && <p className="stat-sub">{card.sub}</p>}
              </div>
              <card.icon size={28} color={card.color} style={{ opacity: 0.7 }} />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Proposal Cards */}
      <h2
        style={{
          fontSize: '1.1rem',
          fontWeight: 700,
          marginBottom: '16px',
          color: 'var(--text-primary)',
        }}
      >
        Proposals
      </h2>
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '16px',
        }}
      >
        {proposals.map((proposal, i) => {
          const data = proposal.extracted_data;
          return (
            <motion.div
              key={proposal.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              className="glass-card"
              style={{ padding: '24px', borderRadius: 'var(--radius-lg)' }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '16px',
                }}
              >
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                  {data?.agency_name ?? proposal.original_name}
                </h3>
                {stats?.recommended_agency === data?.agency_name && (
                  <span className="badge badge-info">
                    <Award size={12} /> Recommended
                  </span>
                )}
              </div>

              {data?.executive_summary && (
                <p
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    marginBottom: '16px',
                    lineHeight: 1.6,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {data.executive_summary}
                </p>
              )}

              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '12px',
                  fontSize: '0.8rem',
                }}
              >
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Total Cost</span>
                  <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {formatCurrency(data?.pricing?.total_cost)}
                  </p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Timeline</span>
                  <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {data?.timeline?.duration ?? 'N/A'}
                  </p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Deliverables</span>
                  <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {data?.deliverables?.length ?? 0} items
                  </p>
                </div>
                <div>
                  <span style={{ color: 'var(--text-muted)' }}>Team Size</span>
                  <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                    {data?.team?.total_members ?? data?.team?.members?.length ?? 'N/A'}
                  </p>
                </div>
              </div>

              {/* USPs */}
              {data?.unique_selling_points && data.unique_selling_points.length > 0 && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {data.unique_selling_points.slice(0, 3).map((usp, j) => (
                      <span
                        key={j}
                        style={{
                          fontSize: '0.7rem',
                          padding: '3px 8px',
                          borderRadius: '9999px',
                          background: 'rgba(99, 102, 241, 0.1)',
                          color: 'var(--text-accent)',
                          border: '1px solid rgba(99, 102, 241, 0.2)',
                        }}
                      >
                        {usp.length > 30 ? usp.slice(0, 30) + '...' : usp}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Comparison Summary */}
      {dashboard.comparison?.overall_summary && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="glass-card"
          style={{ marginTop: '24px', padding: '24px' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <TrendingUp size={20} color="var(--accent-start)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>AI Summary</h3>
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
            {dashboard.comparison.overall_summary}
          </p>
        </motion.div>
      )}
    </div>
  );
}
