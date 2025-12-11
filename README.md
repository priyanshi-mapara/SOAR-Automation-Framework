# SOAR Automation Framework

A modular Security Orchestration, Automation, and Response (SOAR) framework built in Python. Playbooks are defined in YAML (JSON-compatible) and executed dynamically with discoverable triggers, conditions, and actions—mirroring how platforms like Cortex XSOAR, Swimlane, or Splunk SOAR orchestrate automation. The framework now ships with a FastAPI-powered REST layer and a modern React dashboard for visual management.

## Features
- **Dynamic discovery** of actions, conditions, and triggers via reflection (no hardcoded imports).
- **YAML playbooks** describing triggers, conditions, and ordered actions.
- **Custom logging** that traces each step of playbook execution.
- **Validation** to catch malformed playbooks before execution.
- **Extensible architecture** using base `Action`, `Condition`, and `Trigger` classes.
- **PyYAML optional**: falls back to JSON parsing if PyYAML is unavailable (playbooks in this repo are JSON-compatible YAML for portability).
- **FastAPI REST API** that exposes playbook CRUD, execution history, triggers, and live log streaming.
- **React dashboard** with live log viewer, trigger monitor, playbook browser, and execution history table.

## Project Layout
```
main.py
engine/
  __init__.py
  base.py
  executor.py
  loader.py
  logger.py
actions/
  __init__.py
  email_actions.py
  ticket_actions.py
  enrichment_actions.py
conditions/
  __init__.py
  basic_conditions.py
triggers/
  __init__.py
  schedule_trigger.py
  event_trigger.py
configs/
  playbooks/
    phishing_triage.yml
    iam_review.yml
utils/
  __init__.py
  validator.py
  helpers.py
```

## Getting Started
1. **Install dependencies**: The framework now includes a lightweight API/UI layer:
   ```bash
   pip install fastapi uvicorn "pydantic>=2" pyyaml
   ```
2. **Run a playbook (CLI unchanged)**:
   ```bash
   python main.py --playbook configs/playbooks/phishing_triage.yml
   ```
   By default, `main.py` runs the phishing triage playbook.
3. **Start the API + UI server**:
   ```bash
   python run_server.py
   ```
   - API served on `http://localhost:8000`.
   - If you build the React UI (`npm install && npm run build` in `ui/`), it will be served from the same origin.
4. **Run the React dashboard (development mode)**:
   ```bash
   cd ui
   npm install
   npm run dev -- --host
   ```
   Set `VITE_API_URL=http://localhost:8000` to point the UI at a different API host if needed.

## How It Works
1. **Loader** discovers available actions/conditions/triggers using `pkgutil` and `importlib` and maps their `type` identifiers to classes.
2. **Validator** checks the YAML for required fields (`name`, `trigger`, `conditions`, `actions`).
3. **Executor**
   - Instantiates the trigger and collects events (sync or scheduled).
   - Evaluates conditions against each event context.
   - Executes actions sequentially when all conditions pass.
4. **Logger** prints informative and debug statements, e.g.:
   - `[INFO] Loading playbook…`
   - `[DEBUG] Condition passed: equals(field=email.sender_domain)`
   - `[INFO] Executing action: create_ticket`

## Playbooks
Playbooks live under `configs/playbooks/`. Example (Phishing Triage):
```yaml
{
  "name": "Phishing Triage",
  "trigger": "event",
  "conditions": [
    {
      "type": "equals",
      "field": "email.sender_domain",
      "value": "suspicious.com"
    }
  ],
  "actions": [
    {
      "type": "enrich_ip",
      "field": "email.sender_ip"
    },
    {
      "type": "create_ticket",
      "priority": "High"
    }
  ]
}
```

### Included Playbooks
- **phishing_triage.yml**: Event-based flow that enriches sender IPs, creates a ticket, and sends an SOC notification.
- **iam_review.yml**: Scheduled flow that runs every second (twice by default) and notifies the identity team.

## REST API

Key endpoints (see `api/routes/` for full definitions):

- `GET /playbooks` — list available playbooks.
- `GET /playbooks/{name}` — retrieve the parsed YAML content.
- `POST /playbooks/run/{name}` — start an asynchronous execution run.
- `POST /playbooks/upload` — upload a new YAML file.
- `PUT /playbooks/{name}` / `DELETE /playbooks/{name}` — manage playbooks.
- `GET /runs` / `GET /runs/{id}` — execution history and log retrieval.
- `WEBSOCKET /logs/stream/{id}` — live log streaming per run.
- `GET /triggers` and `POST /triggers/(enable|disable)/{name}` — monitor trigger readiness.

Execution metadata and logs are stored in a lightweight SQLite database under `data/soar.db`.

## React Dashboard

The UI (in `ui/`) offers:
- Playbook browser with trigger badges and quick actions (run/view/delete).
- Detail view that surfaces trigger, conditions, and actions alongside the YAML content.
- Live log viewer backed by WebSockets and an execution history table.
- Trigger monitor with enable/disable controls and last-run timestamps.

Build artifacts from `npm run build` are automatically served by the FastAPI app when placed in `ui/build`.

## Extending the Framework
1. **Add a new action**
   - Create a class inheriting `Action` in `actions/` and set `type`.
   - Implement `execute(self, context)` to return the updated context.
2. **Add a new condition**
   - Create a class inheriting `Condition` in `conditions/` with `type`.
   - Implement `evaluate(self, context)` to return a boolean.
3. **Add a new trigger**
   - Create a class inheriting `Trigger` in `triggers/` with `type`.
   - Implement `async run(self)` returning a list of event contexts.
4. **Reference in YAML**
   - Use the `type` you defined in your playbook. Discovery happens automatically—no additional wiring required.

## Mock Data
Triggers supply mock data to demonstrate the flow:
- `EventTrigger` simulates an inbound phishing alert with sender details and severity.
- `ScheduleTrigger` emits periodic IAM review events based on the configured interval/runs values.

## Logging & Validation
- Logging shows when playbooks load, which components are discovered, and the result of each condition/action.
- Validation errors are explicit when required keys or types are missing.

## Notes
- Because the schedule trigger uses `asyncio.sleep`, it will pause between generated events to simulate a real scheduler.
- Extend or replace the mock data with integrations to real systems to build richer automations.
