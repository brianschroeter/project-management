# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Ultrathink** is an ADHD-friendly AI-powered task management system that integrates with TickTick. It provides dual interfaces (CLI + Web Dashboard) for task capture, AI-driven task breakdown, energy-level matching, and intelligent prioritization designed specifically for ADHD workflows.

## Tech Stack

**Backend:**
- FastAPI (Python 3.9+)
- SQLAlchemy with SQLite
- OpenRouter API (Claude 3.5 Sonnet)
- TickTick OAuth 2.0 integration

**Frontend:**
- React 19 with Vite
- TanStack Query for data fetching
- Radix UI components
- Framer Motion for animations

**CLI:**
- Typer with Rich for terminal UI
- HTTPX for API communication

## Development Commands

### Backend Development

```bash
# Start backend server (development mode with hot reload)
cd ultrathink
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload

# Run backend tests
cd backend
pytest

# Run specific test file
pytest tests/test_task_analyzer.py

# Install/update Python dependencies
pip install -e .
```

### Frontend Development

```bash
# Start web dashboard (development mode)
cd web
npm run dev

# Start with network access
npm run dev -- --host 0.0.0.0 --port 5173

# Build for production
npm run build

# Preview production build
npm run preview

# Lint frontend code
npm run lint
```

### CLI Usage

```bash
# Authenticate with TickTick (required first step)
ultra auth

# Add task with AI breakdown
ultra add "Task description"

# Analyze all tasks (bulk operation - optimized to ~1.6s per task)
ultra analyze

# List tasks filtered by energy level
ultra list --energy low|medium|high

# Get daily review
ultra daily

# View CLI help
ultra --help
```

## Architecture Overview

### System Flow

```
TickTick API (OAuth 2.0)
    ↓
Backend (FastAPI) @ localhost:8001
    ├── AI Engine (OpenRouter/Claude)
    ├── Task Analysis Service (optimized batching)
    ├── Energy Tracking
    ├── Prioritization (Eisenhower matrix)
    └── SQLite Database (ultrathink.db)
    ↓
    ├── CLI (Typer) - Quick capture and review
    └── Web Dashboard (React) @ localhost:5173 - Visual organization
```

### Key Backend Services

**Location: `backend/services/`**

- **task_analyzer.py**: AI-powered task breakdown, energy classification, time estimation
  - Uses batched concurrent processing (5 tasks at a time)
  - Single AI call combines breakdown + energy analysis
  - ~1.6s average per task (Phase 1 optimized)

- **prioritizer.py**: Eisenhower matrix implementation + AI-enhanced scoring
  - Urgency, importance, energy match, completion likelihood

- **energy_tracker.py**: Energy pattern tracking and task-energy matching
  - Predicts optimal energy level based on time of day
  - Suggests tasks matching current energy state

- **email_receiver.py**: Email-to-task conversion (Gmail/Outlook OAuth)

### Database Schema

**Tables in `ultrathink.db`:**

- `users`: OAuth tokens and user metadata
- `task_insights`: AI-generated analysis (subtasks, energy, time estimates, priority scores)
- `energy_logs`: User-logged energy levels with timestamps
- `task_completion_history`: Actual vs estimated time tracking for ML improvements
- `ai_interactions`: AI API call logs for debugging

### TickTick Integration Quirks

**IMPORTANT**: The TickTick API has a known issue where `GET /task` returns 500 errors. Always fetch tasks via `GET /project/{id}/data` instead (see `backend/ticktick_client.py:71-105`).

OAuth tokens last ~103 days. Refresh token handling is optional (missing in some responses).

## File Organization

```
ultrathink/
├── backend/
│   ├── main.py              # FastAPI app, all endpoints
│   ├── ai_engine.py         # OpenRouter integration
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # Database models
│   ├── ticktick_client.py   # TickTick API client
│   └── services/
│       ├── task_analyzer.py     # AI task analysis (OPTIMIZED)
│       ├── prioritizer.py       # Priority scoring
│       ├── energy_tracker.py    # Energy tracking
│       └── email_receiver.py    # Email integration
│
├── cli/
│   ├── main.py              # Typer CLI app
│   └── commands/            # Command implementations
│
├── web/
│   ├── src/
│   │   ├── App.jsx          # Main dashboard component
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   └── styles/          # CSS modules
│   └── package.json
│
├── config.py                # Environment configuration
├── .env                     # Environment variables (not in git)
├── .env.example             # Template for .env
├── ultrathink.db            # SQLite database
├── requirements.txt         # Python dependencies
└── setup.py                 # Package definition
```

## API Endpoints Reference

**Base URL**: `http://localhost:8001`

### Authentication
- `GET /auth/status` - Check if authenticated
- `GET /auth/login` - Get OAuth URL
- `GET /callback` - OAuth callback handler

### Tasks
- `POST /tasks` - Create task with AI breakdown
- `GET /tasks` - List all tasks with insights
- `GET /tasks/{task_id}` - Get task details
- `POST /tasks/{task_id}/complete` - Mark complete
- `POST /tasks/analyze-all` - Bulk analyze (optimized, ~40s for 25 tasks)

### Analysis
- `GET /tasks/analyze/vague` - Find unclear tasks
- `GET /tasks/analyze/stale` - Find procrastinated tasks (3+ days)
- `POST /tasks/prioritize` - Re-prioritize all tasks
- `GET /tasks/top` - Get top N priority tasks

### Energy
- `POST /energy/log` - Log current energy level
- `GET /energy/current` - Predict current energy
- `GET /energy/suggest-tasks` - Tasks matching current energy
- `GET /energy/patterns` - Energy patterns over time

### Daily
- `GET /daily` - Daily review summary

Full API documentation available at: `http://localhost:8001/docs`

## ADHD-Optimized Design Patterns

When adding features, maintain these principles:

1. **Minimal Friction**: One command/click to capture tasks
2. **Energy Awareness**: Always consider user's current mental state
3. **Gentle Accountability**: No guilt, only encouragement
4. **Quick Wins**: Highlight easy completions for momentum
5. **Clear Next Steps**: Always show "tiny first step"
6. **Visual Clarity**: Color-code energy levels (🟢 low, 🟡 medium, 🔴 high)
7. **Non-Overwhelming**: Smart filtering over complete lists

## Environment Configuration

**File**: `.env` (copy from `.env.example`)

Required variables:
```env
# OpenRouter AI
OPENROUTER_API_KEY=sk-or-v1-...
AI_MODEL=anthropic/claude-3.5-sonnet
AI_TEMPERATURE=0.7

# TickTick OAuth
TICKTICK_CLIENT_ID=...
TICKTICK_CLIENT_SECRET=...
TICKTICK_REDIRECT_URI=http://localhost:8001/callback

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Database
DATABASE_URL=sqlite:///./ultrathink.db

# Session
SECRET_KEY=ultrathink-secret-key-change-in-production
```

## Performance Characteristics

**Current metrics (Phase 1 optimized):**
- Single task analysis: ~2-3s (AI call)
- Bulk analysis (25 tasks): ~40.8s total (~1.6s per task)
- Task list retrieval: ~200ms
- Daily review: ~300ms
- Energy suggestions: ~150ms

**Optimization approach:**
- Batch processing: 5 concurrent tasks max
- Combined AI prompts: Single call for breakdown + energy + time estimation
- Async TickTick API calls

## Common Development Tasks

### Adding a New CLI Command

1. Add function to `cli/main.py` with `@app.command()` decorator
2. Use `get_api_client()` for backend communication
3. Use `console.print()` from Rich for formatted output
4. Handle errors with `handle_api_error()`

### Adding a New API Endpoint

1. Add route function to `backend/main.py`
2. Add Pydantic models if needed (at top of main.py)
3. Use `get_current_user()` dependency for auth
4. Return standard JSON responses
5. Update API docs at `/docs`

### Modifying AI Prompts

AI prompts are in `backend/ai_engine.py`. Current model: Claude 3.5 Sonnet via OpenRouter.

**IMPORTANT**: Always combine related analyses in a single prompt to reduce API calls (e.g., task breakdown + energy classification + time estimation).

### Adding Database Models

1. Define model in `backend/models.py` (SQLAlchemy)
2. Create migration in `backend/migrations/`
3. Update relevant services
4. Restart backend to apply changes

### Modifying the Web Dashboard

1. Components in `web/src/components/`
2. Use TanStack Query for API calls
3. Follow existing patterns for loading states and error handling
4. Energy levels use consistent color scheme:
   - Low: `#10b981` (green)
   - Medium: `#f59e0b` (amber)
   - High: `#ef4444` (red)

## Testing

```bash
# Run all backend tests
cd backend && pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_task_analyzer.py::test_analyze_task

# Test CLI commands (requires running backend)
ultra analyze  # Should complete in ~40-45s for 25 tasks
```

## Known Issues & Workarounds

1. **TickTick GET /task returns 500**: Use `GET /project/{id}/data` instead
2. **OAuth refresh token sometimes missing**: Refresh token is optional in token response
3. **Multiple backend processes**: Only one should run with `--reload` flag
4. **Energy logging unused**: Feature exists but needs user adoption

## Future Optimization Phases

- **Phase 2**: Caching layer (40-60% fewer API calls)
- **Phase 3**: Database indexing (50-70% faster queries)
- **Phase 4**: Real-time updates (WebSockets)
- **Phase 5**: ML-based time estimation improvements

See `OPTIMIZATION_PHASES.md` for detailed implementation specs.

## Troubleshooting

### Backend won't start
```bash
# Check if port in use
lsof -i :8001
# Kill process and restart
kill <PID>
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### Tasks not showing
```bash
# Check authentication
curl http://localhost:8001/auth/status
# Re-authenticate
ultra auth
```

### Web dashboard not connecting
1. Verify backend running on port 8001
2. Verify frontend running on port 5173
3. Check CORS settings in `backend/main.py`
4. Clear browser cache

## Code Style

- Python: Follow PEP 8, use type hints
- JavaScript: Use modern ES6+, functional components
- API responses: Always include success/error status
- Error messages: ADHD-friendly (encouraging, not overwhelming)
- Comments: Explain "why", not "what"
