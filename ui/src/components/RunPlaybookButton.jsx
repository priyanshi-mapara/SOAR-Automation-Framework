import React from 'react'

const RunPlaybookButton = ({ onRun, label = 'Run playbook' }) => (
  <button className="button" onClick={onRun}>
    {label}
  </button>
)

export default RunPlaybookButton
