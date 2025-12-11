import React from 'react'

const PlaybookList = ({ playbooks, onSelect, onRun, onDelete }) => {
  return (
    <div className="card">
      <div className="section-title">Playbooks</div>
      <div className="card-grid">
        {playbooks.map((pb) => (
          <div key={pb.file} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 700 }}>{pb.name}</div>
                <div style={{ color: '#475569', fontSize: 13 }}>{pb.file}</div>
              </div>
              <span className={`badge ${pb.trigger ? 'green' : ''}`}>
                {pb.trigger?.type || pb.trigger || 'Manual'}
              </span>
            </div>
            <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
              <button className="button" onClick={() => onRun(pb)}>
                Run
              </button>
              <button className="button secondary" onClick={() => onSelect(pb)}>
                Details
              </button>
              <button className="button secondary" onClick={() => onDelete(pb)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PlaybookList
