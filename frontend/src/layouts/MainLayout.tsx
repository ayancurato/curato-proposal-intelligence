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
          background: 'rgba(255, 255, 255, 0.9)',
          backdropFilter: 'blur(16px)',
          borderBottom: '1px solid rgba(0,0,0,0.05)',
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
            style={{ height: '32px', width: 'auto', objectFit: 'contain', marginRight: '16px', mixBlendMode: 'multiply' }}
          />
          <div style={{ height: '20px', width: '1px', background: '#cbd5e1', marginRight: '16px' }} />
          <span style={{
            fontSize: '1rem',
            fontWeight: 500,
            color: '#475569',
            fontFamily: 'Inter, sans-serif'
          }}>
            Proposal Intelligence
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '6px 14px',
            background: 'rgba(15, 181, 168, 0.1)',
            color: '#0fb5a8',
            borderRadius: '9999px',
            fontSize: '0.75rem',
            fontWeight: 600,
            letterSpacing: '0.05em'
          }}>
            <Sparkles size={14} />
            AI-POWERED
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ position: 'relative', zIndex: 1 }}>
        <Outlet />
      </main>
    </div>
  );
}
