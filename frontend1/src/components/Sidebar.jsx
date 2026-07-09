import React from 'react'
import { Link, useLocation } from 'react-router-dom'

function Sidebar() {
  const location = useLocation()

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/log-interaction', label: 'Log Interaction', icon: '📝' },
    { path: '/interactions', label: 'Interactions', icon: '📋' },
    { path: '/hcps', label: 'HCPs', icon: '👨‍⚕️' },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
        </svg>
        <span>AI CRM</span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`sidebar-nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--gray-700)' }}>
        <div className="text-xs text-gray" style={{ color: 'var(--gray-400)' }}>
          <p>AI-First CRM HCP Module</p>
          <p style={{ marginTop: '0.25rem' }}>v1.0.0</p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
