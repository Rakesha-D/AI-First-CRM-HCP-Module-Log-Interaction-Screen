import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import LogInteraction from './pages/LogInteraction'
import Dashboard from './pages/Dashboard'
import HCPList from './pages/HCPList'
import InteractionList from './pages/InteractionList'

function AppLayout() {
  const location = useLocation()
  const isFocusedLogView = location.pathname === '/log-interaction'

  return (
    <div className={isFocusedLogView ? 'app app-focused' : 'app'}>
      {!isFocusedLogView && <Sidebar />}
      <div className="main-content">
        {!isFocusedLogView && <Header />}
        <div className={isFocusedLogView ? 'content content-focused' : 'content'}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/log-interaction" element={<LogInteraction />} />
            <Route path="/hcps" element={<HCPList />} />
            <Route path="/interactions" element={<InteractionList />} />
          </Routes>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  )
}

export default App
