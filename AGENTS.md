# AGENTS.md — AI Model Bias & Fairness Auditor

## Project Structure

```
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── routes/
│   │   ├── main.py              # Dashboard, getting started, health, theme toggle
│   │   ├── audits.py            # Audit CRUD and analysis routes
│   │   └── api.py               # JSON API endpoints
│   ├── models/
│   │   ├── database.py          # SQLite schema and connection management
│   │   └── audit_store.py       # Audit data access layer
│   ├── services/
│   │   ├── bias_metrics.py      # Fairness metric computation
│   │   └── kindo_agent.py       # Kindo AI agent integration
│   ├── templates/
│   │   ├── layouts/
│   │   │   └── base.html        # Base template with nav, theme, help panel
│   │   ├── pages/
│   │   │   ├── index.html       # Dashboard
│   │   │   ├── getting_started.html
│   │   │   ├── audit_list.html
│   │   │   ├── audit_new.html
│   │   │   └── audit_detail.html
│   │   └── errors/
│   │       └── 500.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── agent/
│   ├── agent-config.yaml        # Agent index
│   └── agents/
│       └── bias-audit-agent.yaml
├── wsgi.py                      # WSGI entry point with stable SECRET_KEY
├── gunicorn.conf.py             # Gunicorn configuration
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```

## Kindo Agent Integration

The application integrates with one Kindo AI agent:

| Agent | Env Var | Purpose |
|---|---|---|
| Model Bias Audit Agent | `KINDO_BIAS_AUDIT_AGENT_ID` | Analyzes fairness metrics and generates structured audit reports |

See `agent/agents/bias-audit-agent.yaml` for the full agent configuration including system prompt and I/O schemas.
