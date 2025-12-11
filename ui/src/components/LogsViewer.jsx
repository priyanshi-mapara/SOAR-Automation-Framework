import React, { useEffect, useState } from 'react'
import { websocketUrl } from '../api'

const LogsViewer = ({ runId }) => {
  const [logs, setLogs] = useState([])

  useEffect(() => {
    if (!runId) return
    const ws = new WebSocket(websocketUrl(runId))
    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      setLogs((prev) => [...prev, payload])
    }
    return () => ws.close()
  }, [runId])

  if (!runId) {
    return <div className="card">Start a run to see live logs.</div>
  }

  return (
    <div className="card">
      <div className="section-title">Live Logs</div>
      <div className="log-panel">
        {logs.map((log, idx) => (
          <div key={idx}>
            [{log.level}] {log.timestamp} - {log.message}
          </div>
        ))}
      </div>
    </div>
  )
}

export default LogsViewer
