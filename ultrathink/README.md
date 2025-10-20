# Ultrathink 🧠

ADHD-friendly AI-powered task management for TickTick

## Features

- 🚀 **Dual Interface**: CLI for quick capture, Web for deep organization
- 🤖 **AI Task Breakdown**: Automatically generates actionable subtasks
- ⚡ **Energy-Level Matching**: Suggests tasks based on your current focus state
- ⏱️ **Smart Time Estimation**: AI learns your actual completion patterns
- 🎯 **Intelligent Prioritization**: Eisenhower matrix + AI scoring
- 🔍 **Procrastination Detection**: Identifies stale tasks and helps you unstuck
- 💬 **Clarifying Questions**: AI helps make vague tasks actionable

## Installation

```bash
# Clone and install
cd ultrathink
pip install -e .

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start the backend server
uvicorn backend.main:app --reload

# In another terminal, use the CLI
ultra --help
```

## Quick Start

### CLI Commands

```bash
# Add a task (AI breaks it down automatically)
ultra add "Build presentation for Monday"

# Work on tasks matching your energy level
ultra work --energy low
ultra work --energy high

# Daily review
ultra daily

# List tasks with filters
ultra list --project "Work"
ultra list --priority high

# Mark task as done
ultra done "Task name"

# Get AI help with a specific task
ultra detail "Build presentation"
```

### Web Dashboard

```bash
# Start the web interface
cd web
npm run dev
```

Visit http://localhost:5173 for the visual dashboard.

## Configuration

Required in `.env`:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `TICKTICK_CLIENT_ID`: TickTick OAuth client ID
- `TICKTICK_CLIENT_SECRET`: TickTick OAuth client secret
- `TICKTICK_REDIRECT_URI`: OAuth redirect URL (default: http://localhost:8000/callback)

## ADHD-Optimized Design

✅ Minimal friction for task capture
✅ Visual progress indicators
✅ No overwhelming lists - smart filtering
✅ Gentle, encouraging tone
✅ Energy-aware task matching
✅ Quick wins highlighted for momentum
✅ AI does the organizational heavy lifting

## Development

```bash
# Backend
uvicorn backend.main:app --reload --port 8000

# Frontend
cd web && npm run dev

# Run tests
pytest
```

## License

MIT
