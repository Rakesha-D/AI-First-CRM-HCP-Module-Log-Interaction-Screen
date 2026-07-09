import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchInteractions } from '../store/slices/interactionSlice'

function InteractionList() {
  const dispatch = useDispatch()
  const { items: interactions, loading } = useSelector((state) => state.interactions)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    dispatch(fetchInteractions({ skip: 0, limit: 50 }))
  }, [dispatch])

  const getStatusBadge = (status) => {
    const className = `badge badge-${(status || 'draft').toLowerCase()}`
    return <span className={className}>{status || 'Draft'}</span>
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div style={{ flex: 1, maxWidth: '400px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search interactions..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
        <select
          className="form-select"
          style={{ maxWidth: '200px' }}
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All Types</option>
          <option value="Call">Call</option>
          <option value="Visit">Visit</option>
          <option value="Email">Email</option>
          <option value="Meeting">Meeting</option>
          <option value="Virtual">Virtual</option>
        </select>
      </div>

      <div className="card">
        <div className="card-body" style={{ padding: 0 }}>
          {loading ? (
            <div className="empty-state">
              <div className="spinner" />
            </div>
          ) : interactions.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
              <h3>No interactions found</h3>
              <p className="text-sm text-gray">Log your first interaction to see it here.</p>
            </div>
          ) : (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>HCP</th>
                    <th>Type</th>
                    <th>Date</th>
                    <th>Duration</th>
                    <th>Status</th>
                    <th>Source</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {interactions.map((interaction) => (
                    <tr key={interaction.id}>
                      <td>#{interaction.id}</td>
                      <td className="font-medium">HCP #{interaction.hcp_id}</td>
                      <td>{interaction.interaction_type}</td>
                      <td>
                        {new Date(interaction.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </td>
                      <td>{interaction.duration_minutes ? `${interaction.duration_minutes} min` : '-'}</td>
                      <td>{getStatusBadge(interaction.status)}</td>
                      <td>
                        <span className="badge badge-draft">{interaction.source}</span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.25rem' }}>
                          <button className="btn btn-sm btn-secondary">View</button>
                          <button className="btn btn-sm btn-secondary">Edit</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default InteractionList
