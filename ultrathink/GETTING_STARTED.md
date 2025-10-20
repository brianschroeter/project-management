# Getting Started with Ultrathink

Welcome to Ultrathink! This guide will help you set up and start using your ADHD-friendly task management system.

## Quick Start

### 1. Install Dependencies

```bash
cd ultrathink
pip install -e .
```

This will install all Python dependencies and make the `ultra` command available globally.

### 2. Install Web Dashboard Dependencies

```bash
cd web
npm install
```

### 3. Authenticate with TickTick

First, start the backend server:

```bash
# In one terminal window
uvicorn backend.main:app --reload
```

The server will start at http://localhost:8000

Now authenticate with TickTick:

```bash
# In another terminal window
ultra auth
```

This will give you a URL to open in your browser. After authorizing, you'll be redirected back and authenticated!

### 4. Start Using Ultrathink!

## CLI Commands

### Quick Task Capture

```bash
# Add a task with AI breakdown
ultra add "Build presentation for Monday"

# Add with description
ultra add "Research competitors" --desc "Focus on pricing and features"

# Add without AI breakdown (faster)
ultra add "Buy groceries" --no-breakdown
```

### View Tasks

```bash
# List all tasks
ultra list

# Filter by energy level
ultra list --energy low
ultra list --energy high

# Show completed tasks
ultra list --completed
```

### Work by Energy Level

```bash
# See tasks matching your current energy
ultra work --energy low     # For low-energy moments
ultra work --energy medium  # Normal focus
ultra work --energy high    # Peak concentration
```

### Complete Tasks

```bash
# Mark a task as done
ultra done "Build presentation"

# Track actual time spent
ultra done "Research competitors" --time 45
```

### Daily Review

```bash
# Get your daily overview
ultra daily
```

This shows:
- Predicted energy level
- Top 3 priorities
- Tasks due today
- Stale tasks needing attention

### Task Details

```bash
# Get AI insights for a task
ultra detail "Build presentation"
```

Shows:
- Energy level needed
- Estimated time
- Subtasks breakdown
- First step suggestion
- Procrastination help (if applicable)

### Prioritize Tasks

```bash
# Re-prioritize all tasks with AI
ultra prioritize
```

### Get Unstuck

```bash
# Find stale tasks and get help
ultra unstuck
```

Shows tasks you've been avoiding with:
- Tiny first steps
- Reframing suggestions
- Encouragement

### Log Energy

```bash
# Track your current energy level
ultra energy high
ultra energy medium
ultra energy low

# Add focus quality
ultra energy medium --focus scattered
```

## Web Dashboard

Start the web dashboard:

```bash
cd web
npm run dev
```

Visit http://localhost:5173

The dashboard shows:
- Daily review summary
- Energy-matched task suggestions
- All tasks with AI insights
- Stale tasks warnings
- One-click task completion

## ADHD-Friendly Features

### 1. Automatic Task Breakdown

When you add a task, Ultrathink automatically:
- Breaks it into 3-7 actionable subtasks
- Estimates time for each
- Identifies the energy level needed
- Suggests the easiest first step

### 2. Energy-Based Task Matching

Tasks are classified by energy level:
- 🟢 **Low**: Routine, mechanical tasks
- 🟡 **Medium**: Moderate thinking required
- 🔴 **High**: Deep focus, creative work

Use `ultra work --energy <level>` to see tasks matching your current state.

### 3. Procrastination Detection

Ultrathink identifies tasks you've been avoiding (3+ days) and helps you:
- Understand what might be blocking you
- Find tiny first steps to build momentum
- Reframe overwhelming tasks
- Get encouraging (not guilt-inducing) support

### 4. Smart Prioritization

Uses the Eisenhower Matrix + AI to score tasks by:
- Urgency (time-sensitive?)
- Importance (goal-aligned?)
- Energy match
- Completion likelihood

### 5. Time Estimation with Learning

AI estimates task duration and learns from your actual completion times to improve accuracy.

### 6. Clarifying Questions

For vague tasks, Ultrathink asks questions to make them actionable:
- "What does success look like?"
- "What's the first concrete step?"
- "What might block progress?"

## Tips for Success

### Daily Workflow

1. **Morning**: Run `ultra daily` to see your priorities
2. **Check energy**: Use `ultra energy <level>` to log your state
3. **Start working**: `ultra work --energy <your-level>` shows matched tasks
4. **Complete tasks**: `ultra done <task>` to track progress
5. **Evening**: Check web dashboard for overview

### When Stuck

1. Run `ultra unstuck` to find blocking tasks
2. Use `ultra detail <task>` for AI help
3. Focus on the "tiny first step" suggestion
4. Break tasks down further if needed

### Energy Management

- Track your energy throughout the day
- Notice patterns (morning = high energy?)
- Schedule high-energy tasks accordingly
- Keep low-energy tasks for dips

### Quick Wins

- Check `ultra list --energy low` for easy completions
- Complete 1-2 quick tasks to build momentum
- Use the web dashboard to visualize progress

## Troubleshooting

### "Not authenticated" error

Run `ultra auth` and follow the authentication flow.

### Backend not running

Make sure the FastAPI server is running:
```bash
uvicorn backend.main:app --reload
```

### Web dashboard not connecting

1. Check backend is running on http://localhost:8000
2. Check web dev server is running on http://localhost:5173
3. Clear browser cache and refresh

### Import errors

Make sure you installed the package:
```bash
pip install -e .
```

## Advanced Usage

### API Endpoints

The backend exposes a REST API at http://localhost:8000

Key endpoints:
- `GET /tasks` - List tasks
- `POST /tasks` - Create task with AI analysis
- `GET /tasks/{id}` - Get task details
- `POST /tasks/prioritize` - AI prioritization
- `GET /daily` - Daily review
- `POST /energy/log` - Log energy level
- `GET /energy/suggest-tasks` - Energy-matched tasks

See http://localhost:8000/docs for full API documentation.

### Database

Task insights are stored in `ultrathink.db` (SQLite).

Contains:
- Task metadata and AI analysis
- Energy logs and patterns
- Completion history
- Priority scores

## Next Steps

1. Add your first few tasks
2. Try the daily review workflow
3. Experiment with energy-based work
4. Check the web dashboard
5. Let the AI help you stay organized!

## Need Help?

- Check the README.md for feature overview
- API docs: http://localhost:8000/docs
- GitHub Issues: [Report bugs or suggest features]

Remember: The goal isn't perfection, it's progress. Ultrathink is here to work WITH your ADHD, not against it. 🧠✨
