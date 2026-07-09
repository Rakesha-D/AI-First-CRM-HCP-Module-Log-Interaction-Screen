import React from 'react'
import { useLocation } from 'react-router-dom'

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/log-interaction': 'Log Interaction',
  '/interactions': 'Interactions',
  '/hcps': 'Healthcare Professionals',
}

function Header() {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'AI-First CRM'

  return (
    <header className="header">
      <h1 className="header-title">{title}</h1>
      <div className="header-actions">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: 'var(--primary)',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.875rem',
              fontWeight: 600,
            }}
          >
            JR
          </div>
          <span className="text-sm font-medium">John Rep</span>
        </div>
      </div>
    </header>
  )
}

export default Header
