import { Outlet } from 'react-router';
import { Sparkles } from 'lucide-react';

export default function MainLayout() {
  return (
    <div style={{ minHeight: '100vh', position: 'relative', overflow: 'hidden' }}>
      {/* Background orbs */}
      <div className="bg-orb bg-orb-1" />
      <div className="bg-orb bg-orb-2" />
      <div className="bg-orb bg-orb-3" />

      {/* Navigation */}
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 50,
          background: 'rgba(244, 247, 252, 0.8)',
          backdropFilter: 'blur(16px)',
          borderBottom: '1px solid var(--glass-border)',
          padding: '16px 32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <img
            src="/curato-logo-full.jpg"
            alt="Curato Logo"
            style={{ height: '76px', width: 'auto', objectFit: 'contain', marginRight: '-16px', mixBlendMode: 'multiply' }}
          />
          <div style={{ height: '24px', width: '2px', background: 'var(--glass-border)', marginRight: '12px', position: 'relative', zIndex: 1 }} />
          <span style={{
            fontSize: '1.15rem',
            fontWeight: 600,
            color: 'var(--text-secondary)',
            letterSpacing: '0.01em',
          }}>
            Proposal Intelligence
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span className="badge badge-info">
            <Sparkles size={12} />
            AI-Powered
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ position: 'relative', zIndex: 1 }}>
        <Outlet />
      </main>
    </div>
  );
}
