import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchHCPs, createHCP } from '../store/slices/hcpSlice'

function HCPList() {
  const dispatch = useDispatch()
  const { items: hcps, loading } = useSelector((state) => state.hcps)
  const [search, setSearch] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    npi: '',
    specialty: '',
    email: '',
    phone: '',
    organization: '',
    city: '',
    state: '',
  })

  useEffect(() => {
    dispatch(fetchHCPs({ skip: 0, limit: 100, search }))
  }, [dispatch, search])

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await dispatch(createHCP(formData)).unwrap()
      alert('HCP created successfully!')
      setFormData({
        first_name: '',
        last_name: '',
        npi: '',
        specialty: '',
        email: '',
        phone: '',
        organization: '',
        city: '',
        state: '',
      })
      setShowForm(false)
    } catch (error) {
      alert('Failed to create HCP: ' + error)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div style={{ flex: 1, maxWidth: '400px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search HCPs by name, NPI, or organization..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : '+ Add New HCP'}
        </button>
      </div>

      {showForm && (
        <div className="card mb-lg">
          <div className="card-header">
            <h2 className="card-title">Add New Healthcare Professional</h2>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">First Name *</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Last Name *</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">NPI</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.npi}
                    onChange={(e) => setFormData({ ...formData, npi: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Specialty</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.specialty}
                    onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-input"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Phone</label>
                  <input
                    type="tel"
                    className="form-input"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Organization</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.organization}
                    onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">City</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create HCP
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-body" style={{ padding: 0 }}>
          {loading ? (
            <div className="empty-state">
              <div className="spinner" />
            </div>
          ) : hcps.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👨‍⚕️</div>
              <h3>No HCPs found</h3>
              <p className="text-sm text-gray">Add your first Healthcare Professional to get started.</p>
            </div>
          ) : (
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Specialty</th>
                    <th>Organization</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Location</th>
                  </tr>
                </thead>
                <tbody>
                  {hcps.map((hcp) => (
                    <tr key={hcp.id}>
                      <td className="font-medium">
                        {hcp.first_name} {hcp.last_name}
                      </td>
                      <td>{hcp.specialty || '-'}</td>
                      <td>{hcp.organization || '-'}</td>
                      <td>{hcp.email || '-'}</td>
                      <td>{hcp.phone || '-'}</td>
                      <td>
                        {hcp.city && hcp.state
                          ? `${hcp.city}, ${hcp.state}`
                          : '-'}
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

export default HCPList
