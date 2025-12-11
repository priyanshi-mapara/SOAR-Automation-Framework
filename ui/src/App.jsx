import React, { useEffect, useState } from 'react'
import { api } from './api'
import PlaybookList from './components/PlaybookList'
import PlaybookDetails from './components/PlaybookDetails'
import RunPlaybookButton from './components/RunPlaybookButton'
import LogsViewer from './components/LogsViewer'
import TriggerMonitor from './components/TriggerMonitor'

const App = () => {
  const [playbooks, setPlaybooks] = useState([])
  const [selected, setSelected] = useState(null)
  const [selectedContent, setSelectedContent] = useState('')
  const [triggers, setTriggers] = useState([])
  const [runs, setRuns] = useState([])
  const [activeRun, setActiveRun] = useState(null)

  const loadData = async () => {
    const [pbRes, trigRes, runRes] = await Promise.all([
      api.get('/playbooks'),
      api.get('/triggers'),
      api.get('/runs'),
    ])
    setPlaybooks(pbRes.data)
    setTriggers(trigRes.data.triggers)
    setRuns(runRes.data.runs)
  }

  useEffect(() => {
    loadData()
  }, [])

  const selectPlaybook = async (pb) => {
    const res = await api.get(`/playbooks/${pb.file || pb.name}`)
    setSelected(res.data)
    setSelectedContent(JSON.stringify(res.data, null, 2))
  }

  const runPlaybook = async (pb) => {
    const res = await api.post(`/playbooks/run/${pb.file || pb.name}`)
    setActiveRun(res.data.run_id)
  }

  const deletePlaybook = async (pb) => {
    await api.delete(`/playbooks/${pb.file || pb.name}`)
    loadData()
  }

  const toggleTrigger = async (trigger) => {
    if (trigger.active) {
      await api.post(`/triggers/disable/${trigger.name}`)
    } else {
      await api.post(`/triggers/enable/${trigger.name}`)
    }
    loadData()
  }

  const refreshRuns = async () => {
    const res = await api.get('/runs')
    setRuns(res.data.runs)
  }

  return (
    <div className="app-shell">
      <div className="header">
        <div>
          <div style={{ fontSize: 28, fontWeight: 800 }}>SOAR Automation Dashboard</div>
          <div style={{ color: '#475569' }}>Monitor playbooks, triggers, and executions.</div>
        </div>
        <RunPlaybookButton onRun={() => selected && runPlaybook(selected)} label="Run selected" />
      </div>

      <PlaybookList
        playbooks={playbooks}
        onSelect={selectPlaybook}
        onRun={runPlaybook}
        onDelete={deletePlaybook}
      />

      <div className="card-grid" style={{ marginTop: 16 }}>
        <div className="card">
          <div className="section-title">Execution History</div>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Playbook</th>
                <th>Status</th>
                <th>Started</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr key={run.id}>
                  <td>{run.id.slice(0, 8)}</td>
                  <td>{run.playbook}</td>
                  <td>
                    <span className={`badge ${run.status === 'success' ? 'green' : run.status === 'running' ? '' : 'red'}`}>
                      {run.status}
                    </span>
                  </td>
                  <td>{run.started_at}</td>
                  <td>{run.duration ? `${run.duration.toFixed(2)}s` : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="button secondary" onClick={refreshRuns}>Refresh</button>
        </div>
        <LogsViewer runId={activeRun} />
      </div>

      <TriggerMonitor triggers={triggers} onToggle={toggleTrigger} />

      <PlaybookDetails
        playbook={selected}
        content={selectedContent}
        onEdit={() => alert('Edit in YAML editor coming soon. Use upload/update endpoints meanwhile.')}
      />
    </div>
  )
}

export default App
