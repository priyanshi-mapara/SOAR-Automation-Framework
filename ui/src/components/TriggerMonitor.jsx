import React from 'react'

const TriggerMonitor = ({ triggers, onToggle }) => (
  <div className="card">
    <div className="section-title">Triggers</div>
    <div className="card-grid">
      {triggers.map((trigger) => (
        <div key={trigger.name} className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontWeight: 700 }}>{trigger.name}</div>
            <span className={`badge ${trigger.active ? 'green' : 'red'}`}>
              {trigger.active ? 'Active' : 'Disabled'}
            </span>
          </div>
          <div style={{ color: '#475569', fontSize: 13 }}>Last run: {trigger.last_run || '—'}</div>
          <button
            className="button secondary"
            style={{ marginTop: 12 }}
            onClick={() => onToggle(trigger)}
          >
            {trigger.active ? 'Disable' : 'Enable'}
          </button>
        </div>
      ))}
    </div>
  </div>
)

export default TriggerMonitor
