import React from 'react'

function Dashboard() {
  const stats = [
    { label: 'Total Interactions', value: '156', change: '+12%', color: 'var(--primary)' },
    { label: 'HCPs Contacted', value: '48', change: '+5%', color: 'var(--success)' },
    { label: 'Open Opportunities', value: '23', change: '+8%', color: 'var(--warning)' },
    { label: 'Follow-ups Due', value: '7', change: '-2%', color: 'var(--danger)' },
  ]

  const recentInteractions = [
    { id: 1, hcp: 'Dr. Sarah Johnson', type: 'Visit', date: '2024-01-15', status: 'Approved' },
    { id: 2, hcp: 'Dr. Michael Chen', type: 'Call', date: '2024-01-14', status: 'Submitted' },
    { id: 3, hcp: 'Dr. Emily Williams', type: 'Meeting', date: '2024-01-14', status: 'Draft' },
    { id: 4, hcp: 'Dr. Robert Brown', type: 'Email', date: '2024-01-13', status: 'Approved' },
    { id: 5, hcp: 'Dr. Lisa Davis', type: 'Virtual', date: '2024-01-12', status: 'Approved' },
  ]

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <div className="card-body">
              <div className="text-sm text-gray mb-md">{stat.label}</div>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: stat.color }}>{stat.value}</div>
              <div className="text-xs mt-sm" style={{ color: stat.change.startsWith('+') ? 'var(--success)' : 'var(--danger)' }}>
                {stat.change} from last month
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Recent Interactions</h2>
        </div>
        <div className="card-body" style={{ padding: 0 }}>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>HCP Name</th>
                  <th>Type</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentInteractions.map((interaction) => (
                  <tr key={interaction.id}>
                    <td className="font-medium">{interaction.hcp}</td>
                    <td>{interaction.type}</td>
                    <td>{interaction.date}</td>
                    <td>
                      <span className={`badge badge-${interaction.status.toLowerCase()}`}>
                        {interaction.status}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-sm btn-secondary">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
