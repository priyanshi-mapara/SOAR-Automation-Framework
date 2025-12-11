import React from 'react'

const PlaybookDetails = ({ playbook, content, onEdit }) => {
  if (!playbook) return null
  return (
    <div className="card" style={{ marginTop: 16 }}>
      <div className="section-title">Playbook Detail</div>
      <div style={{ display: 'flex', gap: 12 }}>
        <div className="flex-grow">
          <div><strong>Name:</strong> {playbook.name}</div>
          <div><strong>Trigger:</strong> {playbook.trigger?.type || playbook.trigger || 'Manual'}</div>
          <div className="section-title">Conditions</div>
          <pre style={{ background: '#f1f5f9', padding: 12, borderRadius: 8 }}>
            {JSON.stringify(playbook.conditions || [], null, 2)}
          </pre>
          <div className="section-title">Actions</div>
          <pre style={{ background: '#f1f5f9', padding: 12, borderRadius: 8 }}>
            {JSON.stringify(playbook.actions || [], null, 2)}
          </pre>
        </div>
        <div className="flex-grow">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div className="section-title" style={{ margin: 0 }}>YAML</div>
            <button className="button secondary" onClick={onEdit}>Edit</button>
          </div>
          <pre className="editor">{content}</pre>
        </div>
      </div>
    </div>
  )
}

export default PlaybookDetails
