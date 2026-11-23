# AI Model Bias & Fairness Auditor

A web application for auditing machine learning models for bias and fairness. Upload model predictions alongside demographic data, compute industry-standard fairness metrics, and generate AI-powered audit reports.

## Features

- **Bias Metric Computation** — Disparate impact ratio, statistical parity difference, equal opportunity difference, per-group selection rates, TPR, and FPR
- **CSV Dataset Upload** — Upload any CSV with predictions, labels, and a protected attribute column
- **AI-Powered Reports** — Generate detailed audit reports via Kindo AI agent integration
- **Getting Started Guide** — Step-by-step onboarding page
- **Light/Dark Theme** — Toggle between themes with session persistence
- **Context Help** — Per-page help panels explaining features

## Quick Start

```bash
# Clone the repository
git clone https://github.com/kinhelm-ai-fabric/ai-model-bias-fairness-auditor.git
cd ai-model-bias-fairness-auditor

# Copy environment file
cp .env.example .env

# Build and run with Docker
docker build -t bias-auditor .
docker run -p 5000:5000 bias-auditor
```

Visit `http://localhost:5000` to access the application.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session secret key | Auto-generated |
| `SESSION_COOKIE_PATH` | Cookie path | `/` |
| `DATA_DIR` | Data directory for DB and uploads | `/app/data` |
| `KINDO_API_KEY` | Kindo platform API key | *(empty)* |
| `KINDO_BIAS_AUDIT_AGENT_ID` | Kindo agent ID for bias audit reports | *(empty)* |
| `PORT` | Server port | `5000` |
| `WEB_CONCURRENCY` | Gunicorn worker count | `2` |

## CSV Format

Your dataset CSV should include:

| Column | Description |
|---|---|
| `label` | Ground truth outcome (e.g., 1 or 0) |
| `prediction` | Model's predicted outcome |
| *protected attribute* | Demographic group column (e.g., gender, race) |

## Built With

- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [Gunicorn](https://gunicorn.org/) — WSGI HTTP server
- [Kindo](https://kindo.ai/) — AI agent platform for report generation
