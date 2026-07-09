import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { createInteraction } from '../store/slices/interactionSlice'
import { createHCP } from '../store/slices/hcpSlice'

const initialFormData = () => ({
  hcp_id: '',
  hcp_name: '',
  rep_id: 1,
  rep_name: 'John Rep',
  interaction_type: 'Meeting',
  date: new Date().toISOString().split('T')[0],
  time: '19:36',
  duration_minutes: '',
  summary: '',
  details: '',
  key_topics: '',
  products_discussed: '',
  attendees: '',
  materials_shared: '',
  samples_distributed: '',
  sentiment: 'Neutral',
  next_steps: '',
  follow_up_date: '',
})

function InteractionForm({ hcps }) {
  const dispatch = useDispatch()
  const [loading, setLoading] = useState(false)
  const currentInteraction = useSelector((state) => state.interactions.current)
  const [formData, setFormData] = useState(initialFormData)

  useEffect(() => {
    if (currentInteraction) {
      setFormData((prev) => ({
        ...prev,
        hcp_id: currentInteraction.hcp_id || prev.hcp_id,
        hcp_name: currentInteraction.hcp_name || prev.hcp_name,
        rep_id: currentInteraction.rep_id || prev.rep_id,
        rep_name: currentInteraction.rep_name || prev.rep_name,
        interaction_type: currentInteraction.interaction_type || prev.interaction_type,
        date: currentInteraction.date ? new Date(currentInteraction.date).toISOString().split('T')[0] : prev.date,
        time: currentInteraction.time || (
          currentInteraction.date
            ? new Date(currentInteraction.date).toTimeString().slice(0, 5)
            : prev.time
        ),
        duration_minutes: currentInteraction.duration_minutes ?? prev.duration_minutes,
        summary: currentInteraction.summary || prev.summary,
        details: currentInteraction.details || prev.details,
        attendees: currentInteraction.attendees || prev.attendees,
        materials_shared: currentInteraction.materials_shared || prev.materials_shared,
        samples_distributed: currentInteraction.samples_distributed || prev.samples_distributed,
        sentiment: currentInteraction.sentiment || prev.sentiment,
        key_topics: Array.isArray(currentInteraction.key_topics)
          ? currentInteraction.key_topics.join(', ')
          : (currentInteraction.key_topics || prev.key_topics),
        products_discussed: Array.isArray(currentInteraction.products_discussed)
          ? currentInteraction.products_discussed.join(', ')
          : (currentInteraction.products_discussed || prev.products_discussed),
        next_steps: currentInteraction.next_steps || prev.next_steps,
        follow_up_date: currentInteraction.follow_up_date ? currentInteraction.follow_up_date.split('T')[0] : prev.follow_up_date,
      }))
    }
  }, [currentInteraction])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const hcpName = formData.hcp_name.trim()
      const existingHcp = hcps.find((hcp) => (
        `${hcp.first_name} ${hcp.last_name}`.trim().toLowerCase() === hcpName.toLowerCase()
      ))
      const hcp = existingHcp || await dispatch(createHCP({
        first_name: hcpName.split(' ')[0],
        last_name: hcpName.split(' ').slice(1).join(' ') || 'Unknown',
      })).unwrap()

      const interactionDate = formData.date && formData.time
        ? new Date(`${formData.date}T${formData.time}`)
        : new Date(formData.date)

      const payload = {
        hcp_id: hcp.id,
        rep_id: formData.rep_id,
        rep_name: formData.rep_name,
        interaction_type: formData.interaction_type,
        date: interactionDate.toISOString(),
        duration_minutes: parseInt(formData.duration_minutes) || null,
        summary: formData.summary || formData.key_topics || 'HCP interaction logged',
        details: [
          formData.details,
          formData.attendees ? `Attendees: ${formData.attendees}` : '',
          formData.materials_shared ? `Materials shared: ${formData.materials_shared}` : '',
          formData.samples_distributed ? `Samples distributed: ${formData.samples_distributed}` : '',
          formData.sentiment ? `Observed sentiment: ${formData.sentiment}` : '',
        ].filter(Boolean).join('\n'),
        key_topics: formData.key_topics ? formData.key_topics.split(',').map((s) => s.trim()) : [],
        products_discussed: formData.products_discussed ? formData.products_discussed.split(',').map((s) => s.trim()) : [],
        next_steps: formData.next_steps,
        follow_up_date: formData.follow_up_date ? new Date(formData.follow_up_date).toISOString() : null,
        source: 'manual',
      }

      await dispatch(createInteraction(payload)).unwrap()
      alert('Interaction logged successfully!')
      setFormData(initialFormData())
    } catch (error) {
      alert('Failed to log interaction: ' + error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="log-card interaction-card">
      <div className="log-card-header">
        <h2 className="log-card-title">Interaction Details</h2>
      </div>
      <div className="log-card-body">
        <form onSubmit={handleSubmit}>
          <div className="compact-form-row">
            <div className="form-group">
              <label className="form-label">HCP Name</label>
              <input
                type="text"
                name="hcp_name"
                className="form-input"
                value={formData.hcp_name}
                onChange={handleChange}
                placeholder="Enter HCP name"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Interaction Type</label>
              <select
                name="interaction_type"
                className="form-select"
                value={formData.interaction_type}
                onChange={handleChange}
                required
              >
                <option value="Visit">In person</option>
                <option value="Meeting">Meeting</option>
                <option value="Virtual">Online</option>
                <option value="Call">Call</option>
                <option value="Email">Email</option>
                <option value="Webinar">Webinar</option>
                <option value="Phone">Phone</option>
              </select>
            </div>
          </div>

          <div className="compact-form-row">
            <div className="form-group">
              <label className="form-label">Date</label>
              <input
                type="date"
                name="date"
                className="form-input"
                value={formData.date}
                onChange={handleChange}
                required
                readOnly
              />
            </div>

            <div className="form-group">
              <label className="form-label">Time</label>
              <input
                type="time"
                name="time"
                className="form-input"
                value={formData.time}
                onChange={handleChange}
                readOnly
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Attendees</label>
            <input
              type="text"
              name="attendees"
              className="form-input"
              value={formData.attendees}
              onChange={handleChange}
              placeholder="Enter names or search..."
              readOnly
            />
          </div>

          <div className="form-group">
            <label className="form-label">Topics Discussed</label>
            <textarea
              name="key_topics"
              className="form-textarea"
              value={formData.key_topics}
              onChange={handleChange}
              placeholder="Enter key discussion points..."
              readOnly
            />
            <button type="button" className="voice-summary-btn" disabled>
              <span aria-hidden="true">&gt;&gt;</span> Summarize from Voice Note (Requires Consent)
            </button>
          </div>

          <div className="materials-section">
            <label className="form-label">Materials Shared / Samples Distributed</label>
            <div className="material-row">
              <div>
                <div className="material-title">Materials Shared</div>
                <div className="material-empty">
                  {formData.materials_shared || 'No materials added'}
                </div>
              </div>
              <button type="button" className="small-action-btn" disabled>Search/Add</button>
            </div>
            <div className="material-row">
              <div>
                <div className="material-title">Samples Distributed</div>
                <div className="material-empty">
                  {formData.samples_distributed || 'No samples added'}
                </div>
              </div>
              <button type="button" className="small-action-btn" disabled>Add Sample</button>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Observed/Inferred HCP Sentiment</label>
            <div className="sentiment-options">
              {[{ value: 'Positive', emoji: '😊' }, { value: 'Neutral', emoji: '😐' }, { value: 'Negative', emoji: '😞' }].map((item) => (
                <label key={item.value} className="sentiment-option">
                  <input
                    type="radio"
                    name="sentiment"
                    value={item.value}
                    checked={formData.sentiment === item.value}
                    onChange={handleChange}
                    disabled
                  />
                  <span>{item.emoji} {item.value}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Outcomes</label>
            <textarea
              name="summary"
              className="form-textarea"
              value={formData.summary}
              onChange={handleChange}
              placeholder="Key outcomes or agreements..."
              readOnly
            />
          </div>

          <div className="form-group">
            <label className="form-label">Follow-up Actions</label>
            <textarea
              name="next_steps"
              className="form-textarea"
              value={formData.next_steps}
              onChange={handleChange}
              placeholder="Enter next steps or tasks..."
              readOnly
            />
          </div>

          <div className="suggested-followups">
            <div>AI Suggested Follow-ups:</div>
            <ul>
              <li>Schedule follow-up meeting in 2 weeks</li>
              <li>Send OncoBoost Phase II PDF</li>
              <li>Add Dr. Sharma to advisory board invite list</li>
            </ul>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn btn-primary log-submit-btn" disabled={loading}>
              {loading ? <span className="spinner" /> : 'Log'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default InteractionForm
