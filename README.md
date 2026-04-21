# 🤖 Omni Copilot

A chat-first universal AI workspace that lets users orchestrate their daily tools (Gmail, Calendar, GitHub, Notion, Slack, Drive, etc.) from a single chat interface.

## Architecture

```
omni-copilot/
├── frontend/          # Next.js 14 App Router + Tailwind CSS
└── backend/           # FastAPI + LangGraph multi-agent orchestration
```

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router), TypeScript
- **Styling:** Tailwind CSS 3.x
- **State:** Zustand
- **ORM:** Prisma (SQLite)

### Backend
- **API:** FastAPI + SSE streaming
- **Agents:** LangGraph (multi-agent orchestration)
- **LLM:** Groq (`llama-3.3-70b-versatile` by default)
- **Validation:** Pydantic v2

## Quick Start

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env         # then add your GROQ_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev                  # http://localhost:3000
```

## Environment Variables

### Backend `.env`
| Variable | Description |
|---|---|
| `GROQ_API_KEY` | **Required** — enables LLM responses |
| `DEFAULT_MODEL` | LLM model (default: `llama-3.3-70b-versatile`) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth |
| `SLACK_CLIENT_ID` / `SLACK_CLIENT_SECRET` | Slack OAuth |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | GitHub OAuth |
| `NOTION_CLIENT_ID` / `NOTION_CLIENT_SECRET` | Notion OAuth |

### Frontend `.env.local`
| Variable | Description |
|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | Backend URL (default: `http://localhost:8000`) |

## Features

- � Real-time streaming chat with SSE
- 🤖 Multi-agent orchestration via LangGraph (Calendar, Comms, Docs, Code, Browser, Memory)
- � Integrations Hub — connect Gmail, Calendar, GitHub, Notion, Slack, Drive, Discord, WhatsApp
- 🧠 Memory viewer — add, edit, delete AI memory entries
- 📜 Action history drawer — tracks all agent steps
- ⌨️ Command palette (Ctrl+K / ⌘K)
- 🌙 Dark/light theme support

## Agent Routing

The orchestrator classifies intent by keyword and routes to the appropriate specialist:

| Keywords | Agent |
|---|---|
| calendar, schedule, meeting, event | CalendarAgent |
| email, gmail, slack, message, send | CommsAgent |
| doc, notion, drive, document, wiki | DocsAgent |
| github, code, pr, issue, repo | CodeAgent |
| browse, search web, whatsapp, scrape | BrowserAgent |
| remember, memory, recall, forget | MemoryAgent |
| (everything else) | General LLM |
