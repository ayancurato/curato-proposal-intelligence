import { motion } from 'framer-motion';
import {
  Award,
  Star,
  ThumbsUp,
  ThumbsDown,
  HelpCircle,
  ArrowRightLeft,
  Trophy,
  Target,
  MessageSquareQuote,
} from 'lucide-react';
import type { DashboardResponse } from '../services/api';

interface Props {
  dashboard: DashboardResponse;
}

export default function RecommendationPanel({ dashboard }: Props) {
  const rec = dashboard.recommendation;

  if (!rec) {
    return (
      <div className="glass-card" style={{ padding: '48px', textAlign: 'center' }}>
        <Award size={48} color="var(--text-muted)" style={{ margin: '0 auto 16px', display: 'block' }} />
        <p style={{ color: 'var(--text-muted)' }}>
          Recommendation is not available. Upload at least 2 proposals.
        </p>
      </div>
    );
  }

  const confidenceColor =
    rec.confidence_level === 'high'
      ? 'var(--status-success)'
      : rec.confidence_level === 'medium'
        ? 'var(--status-warning)'
        : 'var(--status-error)';

  return (
    <div>
      {/* Hero Recommendation Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card"
        style={{
          padding: '40px 32px',
          marginBottom: '24px',
          textAlign: 'center',
          background: 'var(--text-primary)',
          boxShadow: '0 20px 40px -20px rgba(6, 21, 53, 0.5)',
        }}
      >
        <Trophy size={56} color="var(--accent-end)" style={{ margin: '0 auto 20px', display: 'block' }} />
        <p
          style={{
            fontSize: '0.85rem',
            color: 'rgba(255, 255, 255, 0.6)',
            textTransform: 'uppercase',
            letterSpacing: '0.15em',
            marginBottom: '12px',
            fontWeight: 600,
          }}
        >
          {dashboard.proposal_count === 1 ? 'Final Verdict' : 'AI Recommendation'}
        </p>
        <h2
          style={{
            fontSize: '2.5rem',
            fontWeight: 800,
            letterSpacing: '-0.02em',
            marginBottom: '16px',
            color: '#ffffff',
          }}
        >
          {rec.best_fit_agency}
        </h2>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 20px',
            borderRadius: '9999px',
            background: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            marginBottom: '24px',
          }}
        >
          <Target size={16} color={confidenceColor} />
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: confidenceColor }}>
            {rec.confidence_level.charAt(0).toUpperCase() + rec.confidence_level.slice(1)} Confidence
          </span>
        </div>
        <p
          style={{
            fontSize: '1.1rem',
            color: 'rgba(255, 255, 255, 0.85)',
            lineHeight: 1.7,
            maxWidth: '640px',
            margin: '0 auto',
            fontWeight: 400,
          }}
        >
          {rec.primary_reasoning}
        </p>
      </motion.div>

      {/* Executive Summary */}
      {rec.executive_summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card"
          style={{ padding: '24px', marginBottom: '24px' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <MessageSquareQuote size={18} color="var(--accent-start)" />
            <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>Executive Summary</h3>
          </div>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
            {rec.executive_summary}
          </p>
        </motion.div>
      )}

      {/* Detailed Reasoning */}
      {rec.detailed_reasoning && rec.detailed_reasoning.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="glass-card"
          style={{ padding: '24px', marginBottom: '24px' }}
        >
          <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '16px' }}>
            Reasoning Chain
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {rec.detailed_reasoning.map((reason, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  gap: '12px',
                  alignItems: 'flex-start',
                }}
              >
                <div
                  style={{
                    minWidth: '28px',
                    height: '28px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, var(--accent-start), var(--accent-mid))',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: 'white',
                  }}
                >
                  {i + 1}
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6, paddingTop: '4px' }}>
                  {reason}
                </p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Agency Assessments */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '16px',
          marginBottom: '24px',
        }}
      >
        {rec.assessments.map((assessment, i) => (
          <motion.div
            key={assessment.agency_name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className="glass-card"
            style={{
              padding: '24px',
              border:
                assessment.agency_name === rec.best_fit_agency
                  ? '1px solid var(--accent-start)'
                  : undefined,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>{assessment.agency_name}</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Star size={16} color="var(--accent-mid)" fill="var(--accent-mid)" />
                <span style={{ fontWeight: 700, fontSize: '1.1rem' }}>
                  {assessment.overall_score}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/10</span>
              </div>
            </div>

            {assessment.best_for && (
              <p
                style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-accent)',
                  marginBottom: '16px',
                  fontStyle: 'italic',
                }}
              >
                Best for: {assessment.best_for}
              </p>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                  <ThumbsUp size={14} color="var(--status-success)" />
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--text-muted)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    Strengths
                  </span>
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {assessment.strengths.map((s, j) => (
                    <li
                      key={j}
                      style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-secondary)',
                        padding: '3px 0',
                        lineHeight: 1.5,
                      }}
                    >
                      + {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
                  <ThumbsDown size={14} color="var(--severity-high)" />
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      color: 'var(--text-muted)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    Weaknesses
                  </span>
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                  {assessment.weaknesses.map((w, j) => (
                    <li
                      key={j}
                      style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-secondary)',
                        padding: '3px 0',
                        lineHeight: 1.5,
                      }}
                    >
                      - {w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Trade-offs */}
      {dashboard.proposal_count > 1 && rec.trade_offs && rec.trade_offs.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card"
          style={{ padding: '24px', marginBottom: '24px' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <ArrowRightLeft size={18} color="var(--accent-start)" />
            <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>Trade-offs</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {rec.trade_offs.map((tradeoff, i) => (
              <div
                key={i}
                style={{
                  padding: '16px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--glass-border)',
                }}
              >
                <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '4px' }}>
                  {tradeoff.description}
                </p>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  {tradeoff.agency_a} vs {tradeoff.agency_b}
                </p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  {tradeoff.consideration}
                </p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Single Proposal Extras */}
      {dashboard.proposal_count === 1 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          {rec.things_to_clarify && rec.things_to_clarify.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="glass-card"
              style={{ padding: '24px' }}
            >
              <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '16px', color: 'var(--status-warning)' }}>
                Things to Clarify
              </h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {rec.things_to_clarify.map((item, i) => (
                  <li key={i} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '6px 0', borderBottom: i < rec.things_to_clarify!.length - 1 ? '1px solid var(--glass-border)' : 'none' }}>
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          )}

          {rec.negotiation_suggestions && rec.negotiation_suggestions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.45 }}
              className="glass-card"
              style={{ padding: '24px' }}
            >
              <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '16px', color: 'var(--status-success)' }}>
                Negotiation Suggestions
              </h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {rec.negotiation_suggestions.map((item, i) => (
                  <li key={i} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '6px 0', borderBottom: i < rec.negotiation_suggestions!.length - 1 ? '1px solid var(--glass-border)' : 'none' }}>
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>
      )}

      {/* Decision Guide */}
      {(rec.choose_agency_a_if || rec.choose_agency_b_if) && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.45 }}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            marginBottom: '24px',
          }}
        >
          {rec.choose_agency_a_if && (
            <div
              className="glass-card"
              style={{ padding: '20px', borderLeft: '3px solid var(--status-success)' }}
            >
              <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-success)', marginBottom: '8px', textTransform: 'uppercase' }}>
                Choose {rec.best_fit_agency} if...
              </p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {rec.choose_agency_a_if}
              </p>
            </div>
          )}
          {rec.choose_agency_b_if && (
            <div
              className="glass-card"
              style={{ padding: '20px', borderLeft: '3px solid var(--status-info)' }}
            >
              <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--status-info)', marginBottom: '8px', textTransform: 'uppercase' }}>
                Choose runner-up if...
              </p>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {rec.choose_agency_b_if}
              </p>
            </div>
          )}
        </motion.div>
      )}

      {/* Questions to Ask */}
      {rec.questions_to_ask && rec.questions_to_ask.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card"
          style={{ padding: '24px' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <HelpCircle size={18} color="var(--accent-end)" />
            <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>Questions to Ask Before Signing</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {rec.questions_to_ask.map((q, i) => (
              <div
                key={i}
                style={{
                  padding: '14px 18px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--glass-border)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <p style={{ fontWeight: 600, fontSize: '0.9rem', flex: 1 }}>{q.question}</p>
                  <span
                    style={{
                      fontSize: '0.7rem',
                      padding: '2px 8px',
                      borderRadius: '9999px',
                      background: 'rgba(99, 102, 241, 0.1)',
                      color: 'var(--text-accent)',
                      whiteSpace: 'nowrap',
                      alignSelf: 'flex-start',
                    }}
                  >
                    {q.agency_name}
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                  Why it matters: {q.why_it_matters}
                </p>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
