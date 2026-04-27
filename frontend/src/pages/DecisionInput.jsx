import { useState } from 'react'
import { submitDecision } from '../services/api'

export default function DecisionInput({ userId, onResult }) {
  const [decision, setDecision] = useState('Should I commit to the new opportunity?')
  const [options, setOptions] = useState([
    { id: 'option_a', label: 'Accept', description: 'Commit now and reprioritize current work', estimated_time: 2, estimated_cost: 0, expected_value: 0.75 },
    { id: 'option_b', label: 'Decline', description: 'Protect focus on existing goals', estimated_time: 0.5, estimated_cost: 0, expected_value: 0.55 }
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const updateOption = (index, key, value) => {
    setOptions((current) => current.map((option, optionIndex) => (
      optionIndex === index ? { ...option, [key]: value } : option
    )))
  }

  const addOption = () => {
    setOptions((current) => [
      ...current,
      { id: `option_${current.length + 1}`, label: '', description: '', estimated_time: 1, estimated_cost: 0, expected_value: 0.5 }
    ])
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const payload = {
        user_id: userId,
        decision,
        options: options.map((option) => ({
          ...option,
          estimated_time: Number(option.estimated_time || 0),
          estimated_cost: Number(option.estimated_cost || 0),
          expected_value: Number(option.expected_value || 0.5)
        }))
      }
      const result = await submitDecision(payload)
      onResult(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="panel">
      <p className="eyebrow">Decision Input</p>
      <h2>Ask the PDIS for a scored recommendation</h2>
      <form onSubmit={handleSubmit} className="decision-form">
        <label>
          Decision
          <textarea value={decision} onChange={(event) => setDecision(event.target.value)} rows="4" />
        </label>

        <div className="option-header">
          <h3>Options</h3>
          <button type="button" onClick={addOption}>Add option</button>
        </div>

        {options.map((option, index) => (
          <div className="option-editor" key={option.id}>
            <input value={option.id} onChange={(event) => updateOption(index, 'id', event.target.value)} placeholder="id" />
            <input value={option.label} onChange={(event) => updateOption(index, 'label', event.target.value)} placeholder="label" />
            <textarea value={option.description} onChange={(event) => updateOption(index, 'description', event.target.value)} placeholder="description" />
            <div className="grid three">
              <input type="number" step="0.1" value={option.estimated_time} onChange={(event) => updateOption(index, 'estimated_time', event.target.value)} placeholder="hours/day" />
              <input type="number" step="1" value={option.estimated_cost} onChange={(event) => updateOption(index, 'estimated_cost', event.target.value)} placeholder="cost" />
              <input type="number" step="0.05" min="0" max="1" value={option.expected_value} onChange={(event) => updateOption(index, 'expected_value', event.target.value)} placeholder="expected value" />
            </div>
          </div>
        ))}

        {error && <p className="error">{error}</p>}
        <button className="primary" disabled={loading}>{loading ? 'Running agents...' : 'Generate recommendation'}</button>
      </form>
    </section>
  )
}
