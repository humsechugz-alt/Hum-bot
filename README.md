# HUGZ AI

**Enterprise-Grade AI Platform with Cybersecurity, Voice Interaction, and Revenue Ecosystem**

[![CI](https://github.com/humsechugz-alt/Hum-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/humsechugz-alt/Hum-bot/actions)

---

## Overview

HUGZ AI is a powerful, scalable, secure, intelligent software platform designed to compete with enterprise-level solutions. It combines advanced AI conversation, cybersecurity protection, smart automation, and a complete monetization engine.

### Key Capabilities

| Module | Features |
|--------|----------|
| **AI Brain** | Natural conversation, emotion detection, learning memory, personality engine |
| **Voice** | Speech-to-text (Whisper), text-to-speech (Edge TTS), multilingual |
| **Security Shield** | E2E encryption, intrusion detection, fraud monitoring, WAF, rate limiting |
| **Automation** | Task scheduling, workflows, predictive recommendations, command execution |
| **Revenue Engine** | Wallet system, subscriptions, API marketplace, referral rewards |
| **Integration Hub** | Third-party APIs, IoT bridge, camera intelligence (future) |

## Architecture

See the [docs/](docs/) folder for detailed documentation:

- [System Architecture](docs/SYSTEM_ARCHITECTURE.md) — Full platform architecture
- [Tech Stack](docs/TECH_STACK.md) — Technology recommendations
- [Development Roadmap](docs/DEVELOPMENT_ROADMAP.md) — 18-month phased roadmap
- [Security Layers](docs/SECURITY_LAYERS.md) — 7-layer defense-in-depth model
- [Monetization Strategy](docs/MONETIZATION_STRATEGY.md) — 5 revenue streams
- [Scaling Strategy](docs/SCALING_STRATEGY.md) — Path to 1M+ users

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for full stack)

### Backend (API Server)

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

### Frontend (Web UI)

```bash
cd frontend
npm install
npm run dev
```

### Full Stack (Docker)

```bash
docker-compose up -d
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

### Lint

```bash
cd backend
ruff check app/ tests/
ruff format --check app/ tests/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Platform info |
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/auth/register` | User registration |
| `POST` | `/api/v1/auth/login` | User login |
| `POST` | `/api/v1/chat/message` | Send chat message (AI response + emotion) |
| `POST` | `/api/v1/voice/transcribe` | Speech-to-text |
| `POST` | `/api/v1/voice/synthesize` | Text-to-speech |
| `GET` | `/api/v1/voice/voices` | List available voices |
| `POST` | `/api/v1/security/scan` | Scan input for threats |
| `GET` | `/api/v1/security/status` | Security status |
| `POST` | `/api/v1/security/fraud-check` | Fraud risk scoring |
| `POST` | `/api/v1/automation/tasks` | Create automation task |
| `POST` | `/api/v1/automation/workflows` | Create workflow |
| `GET` | `/api/v1/automation/recommendations` | AI recommendations |

## Project Structure

```
Hum-bot/
├── docs/                          # Architecture & strategy docs
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── TECH_STACK.md
│   ├── DEVELOPMENT_ROADMAP.md
│   ├── SECURITY_LAYERS.md
│   ├── MONETIZATION_STRATEGY.md
│   └── SCALING_STRATEGY.md
├── backend/                       # Python FastAPI backend
│   ├── app/
│   │   ├── api/                   # API route handlers
│   │   ├── core/                  # Config, security, database
│   │   ├── middleware/            # Security middleware
│   │   ├── models/                # SQLAlchemy database models
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   ├── services/              # Business logic services
│   │   │   ├── ai_brain.py        # AI conversation engine
│   │   │   ├── security_shield.py # Cybersecurity engine
│   │   │   ├── voice_processor.py # Voice STT/TTS
│   │   │   └── automation_engine.py # Task automation
│   │   └── main.py               # FastAPI app entry point
│   └── tests/                     # Test suite
├── frontend/                      # React TypeScript frontend
│   └── src/
│       ├── App.tsx                # Main chat UI
│       └── main.tsx               # Entry point
├── infrastructure/
│   ├── docker/                    # Dockerfiles
│   └── kubernetes/                # K8s manifests (planned)
├── docker-compose.yml             # Local dev environment
└── .github/workflows/ci.yml      # CI/CD pipeline
```

## License

MIT License — see [LICENSE](LICENSE) for details.
