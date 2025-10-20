"""FastAPI application for Ultrathink backend"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from config import settings
from backend.database import get_db, init_db
from backend.models import User, TaskInsight
from backend.ticktick_client import TickTickClient
from backend.services.task_analyzer import TaskAnalyzer
from backend.services.prioritizer import TaskPrioritizer
from backend.services.energy_tracker import EnergyTracker
from backend.services.email_receiver import EmailReceiver
from backend.services.gmail_oauth import GmailOAuth
from backend.services.outlook_oauth import OutlookOAuth
from pydantic import BaseModel, EmailStr
import secrets


# Initialize FastAPI app
app = FastAPI(
    title="Ultrathink API",
    description="ADHD-friendly AI task management for TickTick",
    version="0.1.0",
)

# CORS middleware for web dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://192.168.1.87:5173",
        "http://192.168.1.87:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for requests/responses
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: Optional[str] = None
    priority: Optional[int] = None
    auto_breakdown: bool = True


class EnergyLogCreate(BaseModel):
    energy_level: str  # low, medium, high
    focus_quality: Optional[str] = None


class EmailData(BaseModel):
    subject: str
    body: str
    from_email: EmailStr
    message_id: str
    has_attachments: bool = False
    attachment_count: int = 0
    email_source: str  # 'gmail' or 'outlook'


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# Health check
@app.get("/")
async def root():
    return {
        "message": "Ultrathink API",
        "version": "0.1.0",
        "status": "running",
    }


# OAuth Flow
@app.get("/auth/status")
async def auth_status(db: Session = Depends(get_db)):
    """Check if user is authenticated"""
    user = db.query(User).first()
    if user and user.access_token:
        return {
            "authenticated": True,
            "user_id": user.id,
        }
    return {"authenticated": False}


@app.get("/auth/login")
async def login():
    """Initiate OAuth flow with TickTick"""
    auth_url = TickTickClient.get_authorization_url()
    return {"auth_url": auth_url}


@app.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """Handle OAuth callback from TickTick"""
    try:
        # Exchange code for token
        token_data = TickTickClient.exchange_code_for_token(code)
        print(f"Token data received: {token_data}")

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token", None)
        expires_in = token_data.get("expires_in", 7200)
        print(f"Access token: {access_token[:20]}... Refresh token: {refresh_token}")

        # Skip token verification for now - TickTick API sometimes has issues
        # The token exchange worked, so we'll trust it
        # We'll verify it works when the user actually tries to use it
        print(f"Token obtained successfully, skipping verification")

        # Store user and tokens
        user = db.query(User).filter(
            User.ticktick_user_id == "default"  # TickTick API doesn't expose user ID easily
        ).first()

        if not user:
            user = User(
                ticktick_user_id="default",
                access_token=access_token,
                refresh_token=refresh_token,
                token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            )
            db.add(user)
        else:
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        db.commit()

        # Redirect back to the web app after successful authentication
        return RedirectResponse(url=f"{settings.frontend_url}/?auth=success")

    except Exception as e:
        # Redirect to frontend with error parameter
        return RedirectResponse(url=f"{settings.frontend_url}/?auth=error&message={str(e)}")


# Helper to get current user
def get_current_user(db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user"""
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated. Please login first.")

    # Check if token is expired
    if user.token_expires_at < datetime.utcnow():
        try:
            # Refresh token
            token_data = TickTickClient.refresh_access_token(user.refresh_token)
            user.access_token = token_data["access_token"]
            user.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 7200))
            db.commit()
        except Exception:
            raise HTTPException(status_code=401, detail="Token expired. Please login again.")

    return user


# Task endpoints
@app.post("/tasks")
async def create_task(
    task: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new task with AI analysis"""

    client = TickTickClient(user.access_token)
    analyzer = TaskAnalyzer(db, client)

    # Create task in TickTick
    ticktick_task = client.create_task(
        title=task.title,
        content=task.description,
        project_id=task.project_id,
        priority=task.priority,
    )

    task_id = ticktick_task["id"]

    # Analyze with AI
    analysis = analyzer.analyze_new_task(
        user_id=user.id,
        task_id=task_id,
        task_title=task.title,
        task_description=task.description,
        auto_create_subtasks=task.auto_breakdown,
    )

    return {
        "task": ticktick_task,
        "analysis": analysis,
    }


@app.get("/tasks")
async def list_tasks(
    completed: Optional[bool] = None,
    energy_level: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List tasks with AI insights"""

    client = TickTickClient(user.access_token)

    try:
        tasks = client.get_tasks(completed=completed)
    except Exception as e:
        print(f"TickTick API error in list_tasks: {e}")
        # Fallback to cached tasks from database
        insights = db.query(TaskInsight).filter(
            TaskInsight.user_id == user.id,
            TaskInsight.completed == (completed if completed is not None else False)
        ).all()

        # Convert insights to task format
        tasks = []
        for insight in insights:
            tasks.append({
                "id": insight.ticktick_task_id,
                "title": insight.task_title,
                "content": insight.task_description,
                "projectId": insight.project_id,  # Include projectId for proper URL generation
                "ai_insights": {
                    "energy_level": insight.energy_level,
                    "estimated_minutes": insight.estimated_duration_minutes,
                    "priority_score": insight.priority_score,
                    "eisenhower_quadrant": insight.eisenhower_quadrant,
                },
                "email_source": insight.email_source,
                "email_link": insight.email_link,
                "email_has_attachments": insight.email_has_attachments,
                "email_attachment_count": insight.email_attachment_count,
            })

    # Filter by energy level if specified
    if energy_level:
        task_ids = [
            insight.ticktick_task_id
            for insight in db.query(TaskInsight).filter(
                TaskInsight.user_id == user.id,
                TaskInsight.energy_level == energy_level,
                TaskInsight.completed == False,
            ).all()
        ]
        tasks = [t for t in tasks if t["id"] in task_ids]

    # Enrich with insights
    enriched_tasks = []
    for task in tasks:
        insight = db.query(TaskInsight).filter(
            TaskInsight.ticktick_task_id == task["id"]
        ).first()

        task_data = {**task}
        if insight:
            task_data["ai_insights"] = {
                "energy_level": insight.energy_level,
                "estimated_minutes": insight.estimated_duration_minutes,
                "priority_score": insight.priority_score,
                "eisenhower_quadrant": insight.eisenhower_quadrant,
            }

            # Add projectId from insight if not already in task
            if not task_data.get("projectId") and insight.project_id:
                task_data["projectId"] = insight.project_id

            # Add email metadata if available
            if insight.email_source:
                task_data["email_source"] = insight.email_source
                task_data["email_link"] = insight.email_link
                task_data["email_has_attachments"] = insight.email_has_attachments
                task_data["email_attachment_count"] = insight.email_attachment_count

        enriched_tasks.append(task_data)

    return enriched_tasks


@app.get("/tasks/{task_id}")
async def get_task_details(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get detailed task information with AI insights"""

    client = TickTickClient(user.access_token)
    analyzer = TaskAnalyzer(db, client)

    task = client.get_task(task_id)
    insights = analyzer.get_task_details(task_id)

    return {
        "task": task,
        "insights": insights,
    }


@app.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    actual_minutes: Optional[int] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark task as complete and update insights"""

    client = TickTickClient(user.access_token)
    analyzer = TaskAnalyzer(db, client)

    # Complete in TickTick
    client.complete_task(task_id)

    # Update insights
    analyzer.update_completion(task_id, actual_minutes)

    return {"message": "Task completed successfully"}


@app.get("/tasks/analyze/vague")
async def find_vague_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Find tasks that need clarification"""

    client = TickTickClient(user.access_token)
    analyzer = TaskAnalyzer(db, client)

    vague_tasks = analyzer.identify_vague_tasks(user.id)
    return vague_tasks


@app.get("/tasks/analyze/stale")
async def find_stale_tasks(
    days: int = Query(default=3, ge=1),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Find procrastinated tasks and get unstuck help"""

    client = TickTickClient(user.access_token)
    analyzer = TaskAnalyzer(db, client)

    stale_tasks = analyzer.detect_stale_tasks(user.id, days)
    return stale_tasks


# Prioritization endpoints
@app.post("/tasks/prioritize")
async def prioritize_tasks(
    energy_level: str = "medium",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Prioritize all tasks using AI"""

    client = TickTickClient(user.access_token)
    prioritizer = TaskPrioritizer(db)

    tasks = client.get_tasks(completed=False)
    prioritized = prioritizer.prioritize_user_tasks(user.id, tasks, energy_level)

    return prioritized


@app.get("/tasks/top")
async def get_top_tasks(
    limit: int = Query(default=3, ge=1, le=10),
    energy_level: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get top priority tasks"""

    prioritizer = TaskPrioritizer(db)
    top_tasks = prioritizer.get_top_tasks(user.id, limit, energy_level)

    return top_tasks


# Energy tracking endpoints
@app.post("/energy/log")
async def log_energy(
    energy: EnergyLogCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log current energy level"""

    tracker = EnergyTracker(db)
    log = tracker.log_energy(user.id, energy.energy_level, energy.focus_quality)

    return {"message": "Energy logged", "log_id": log.id}


@app.get("/energy/current")
async def get_current_energy(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recommended current energy based on patterns"""

    tracker = EnergyTracker(db)
    recommendation = tracker.get_current_energy_recommendation(user.id)

    return {"recommended_energy": recommendation}


@app.get("/energy/suggest-tasks")
async def suggest_tasks_by_energy(
    energy_level: str,
    limit: int = Query(default=5, ge=1, le=20),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get task suggestions for current energy level"""

    tracker = EnergyTracker(db)
    suggestions = tracker.suggest_tasks_by_energy(user.id, energy_level, limit)

    return suggestions


@app.get("/energy/patterns")
async def get_energy_patterns(
    days: int = Query(default=30, ge=7, le=90),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze energy patterns over time"""

    tracker = EnergyTracker(db)
    patterns = tracker.get_energy_patterns(user.id, days)

    return patterns


# Daily review endpoint
@app.get("/daily")
async def daily_review(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get daily review summary"""

    client = TickTickClient(user.access_token)
    analyzer = TaskAnalyzer(db, client)
    prioritizer = TaskPrioritizer(db)
    tracker = EnergyTracker(db)

    # Get various insights
    stale_tasks = analyzer.detect_stale_tasks(user.id, stale_threshold_days=3)
    top_tasks = prioritizer.get_top_tasks(user.id, limit=3)
    current_energy = tracker.get_current_energy_recommendation(user.id)

    # Get tasks due today
    try:
        all_tasks = client.get_tasks(completed=False)
    except Exception as e:
        print(f"TickTick API error in daily_review: {e}")
        all_tasks = []

    today = datetime.utcnow().date()

    def parse_ticktick_date(date_str):
        """Parse TickTick date string which can be in various formats"""
        try:
            # Replace various TickTick date formats
            # '2025-09-29T23:59:00.000+0000' -> '2025-09-29T23:59:00.000+00:00'
            # '2025-09-29T23:59:00.000Z' -> '2025-09-29T23:59:00.000+00:00'
            if date_str.endswith('Z'):
                date_str = date_str.replace('Z', '+00:00')
            elif '+0000' in date_str:
                date_str = date_str.replace('+0000', '+00:00')
            elif '-0000' in date_str:
                date_str = date_str.replace('-0000', '+00:00')
            return datetime.fromisoformat(date_str)
        except (ValueError, AttributeError):
            return None

    due_today = [
        t for t in all_tasks
        if t.get("dueDate") and parse_ticktick_date(t["dueDate"]) and parse_ticktick_date(t["dueDate"]).date() == today
    ]

    return {
        "date": today.isoformat(),
        "recommended_energy": current_energy,
        "top_priorities": top_tasks,
        "due_today": due_today,
        "stale_tasks": stale_tasks[:5],
        "message": "Good morning! Here's your focus for today.",
    }


# Email Integration Endpoints

@app.get("/email/status")
async def email_status(
    user: User = Depends(get_current_user),
):
    """Check email authentication status"""
    return {
        "gmail": {
            "authenticated": bool(user.gmail_access_token),
            "email": user.gmail_email,
        },
        "outlook": {
            "authenticated": bool(user.outlook_access_token),
            "email": user.outlook_email,
        },
    }


@app.get("/email/gmail/auth")
async def gmail_auth_init(
    user: User = Depends(get_current_user),
):
    """Initiate Gmail OAuth flow"""
    if not settings.gmail_client_id or not settings.gmail_client_secret:
        raise HTTPException(
            status_code=501,
            detail="Gmail OAuth not configured. Please set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET environment variables."
        )

    gmail_oauth = GmailOAuth(
        client_id=settings.gmail_client_id,
        client_secret=settings.gmail_client_secret,
        redirect_uri=settings.gmail_redirect_uri
    )

    # Generate state token for security
    state = secrets.token_urlsafe(32)
    auth_url = gmail_oauth.get_authorization_url(state)

    return {"auth_url": auth_url, "state": state}


@app.get("/email/gmail/callback")
async def gmail_auth_callback(
    code: str,
    state: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle Gmail OAuth callback"""
    try:
        gmail_oauth = GmailOAuth(
            client_id=settings.gmail_client_id,
            client_secret=settings.gmail_client_secret,
            redirect_uri=settings.gmail_redirect_uri
        )

        # Exchange code for token
        token_data = gmail_oauth.exchange_code_for_token(code)

        # Store tokens
        user.gmail_access_token = token_data["access_token"]
        user.gmail_refresh_token = token_data.get("refresh_token")
        user.gmail_email = token_data.get("email")

        if token_data.get("token_expiry"):
            from dateutil import parser
            user.gmail_token_expiry = parser.parse(token_data["token_expiry"])

        db.commit()

        return {
            "message": "Gmail authentication successful!",
            "email": user.gmail_email
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/email/outlook/auth")
async def outlook_auth_init(
    user: User = Depends(get_current_user),
):
    """Initiate Outlook OAuth flow"""
    if not settings.outlook_client_id or not settings.outlook_client_secret:
        raise HTTPException(
            status_code=501,
            detail="Outlook OAuth not configured. Please set OUTLOOK_CLIENT_ID and OUTLOOK_CLIENT_SECRET environment variables."
        )

    outlook_oauth = OutlookOAuth(
        client_id=settings.outlook_client_id,
        client_secret=settings.outlook_client_secret,
        redirect_uri=settings.outlook_redirect_uri,
        tenant_id=settings.outlook_tenant_id
    )

    # Generate state token for security
    state = secrets.token_urlsafe(32)
    auth_url = outlook_oauth.get_authorization_url(state)

    return {"auth_url": auth_url, "state": state}


@app.get("/email/outlook/callback")
async def outlook_auth_callback(
    code: str,
    state: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle Outlook OAuth callback"""
    try:
        outlook_oauth = OutlookOAuth(
            client_id=settings.outlook_client_id,
            client_secret=settings.outlook_client_secret,
            redirect_uri=settings.outlook_redirect_uri,
            tenant_id=settings.outlook_tenant_id
        )

        # Exchange code for token
        token_data = outlook_oauth.exchange_code_for_token(code)

        # Store tokens
        user.outlook_access_token = token_data["access_token"]
        user.outlook_refresh_token = token_data.get("refresh_token")
        user.outlook_email = token_data.get("email")

        if token_data.get("token_expiry"):
            user.outlook_token_expiry = datetime.utcnow() + timedelta(seconds=token_data["token_expiry"])

        db.commit()

        return {
            "message": "Outlook authentication successful!",
            "email": user.outlook_email
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/email/receive")
async def receive_email(
    email_data: EmailData,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Receive forwarded email and create task

    This endpoint can be called by email forwarding services (SendGrid, Mailgun, etc.)
    or directly with parsed email data.
    """
    try:
        client = TickTickClient(user.access_token)
        email_receiver = EmailReceiver(db, client)

        # Process email and create task
        result = email_receiver.process_email(
            email_data={
                "subject": email_data.subject,
                "body": email_data.body,
                "from": email_data.from_email,
                "message_id": email_data.message_id,
                "has_attachments": email_data.has_attachments,
                "attachment_count": email_data.attachment_count,
            },
            user_id=user.id,
            email_source=email_data.email_source
        )

        return {
            "message": "Email processed and task created successfully",
            "task_id": result["task"]["id"],
            "task_title": result["task"]["title"],
            "email_link": result["email_metadata"]["link"],
            "ai_insights": result["ai_parsing"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing email: {str(e)}")


@app.post("/email/parse-raw")
async def parse_raw_email(
    raw_email: bytes,
    email_source: str = "gmail",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Parse raw email (RFC 822 format) and create task

    Useful for direct IMAP integration or email forwarding services
    that provide raw email content.
    """
    try:
        client = TickTickClient(user.access_token)
        email_receiver = EmailReceiver(db, client)

        # Parse raw email
        email_data = EmailReceiver.parse_email_raw(raw_email)

        # Process email and create task
        result = email_receiver.process_email(
            email_data=email_data,
            user_id=user.id,
            email_source=email_source
        )

        return {
            "message": "Email processed and task created successfully",
            "task_id": result["task"]["id"],
            "task_title": result["task"]["title"],
            "email_link": result["email_metadata"]["link"],
            "ai_insights": result["ai_parsing"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing raw email: {str(e)}")


@app.post("/tasks/analyze-all")
async def analyze_all_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Analyze all existing TickTick tasks and add AI insights with async batch processing"""

    client = TickTickClient(user.access_token)
    analyzer = TaskAnalyzer(db, client)

    # Get all tasks from TickTick
    all_tasks = client.get_tasks(completed=False)

    # Filter out already-analyzed tasks
    tasks_to_analyze = []
    skipped_count = 0

    for task in all_tasks:
        task_id = task["id"]
        existing = db.query(TaskInsight).filter(
            TaskInsight.ticktick_task_id == task_id
        ).first()

        if existing:
            skipped_count += 1
        else:
            tasks_to_analyze.append(task)

    # Process tasks in parallel batches of 5
    analyzed_count = 0
    errors = []
    batch_size = 5

    def analyze_single_task(task):
        """Helper to analyze a single task (runs in thread pool)"""
        try:
            analyzer.analyze_new_task(
                user_id=user.id,
                task_id=task["id"],
                task_title=task["title"],
                task_description=task.get("content", ""),
                auto_create_subtasks=False,
            )
            return {"success": True, "task_id": task["id"]}
        except Exception as e:
            return {"success": False, "task_id": task["id"], "error": str(e)}

    # Process in batches with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        for i in range(0, len(tasks_to_analyze), batch_size):
            batch = tasks_to_analyze[i:i + batch_size]
            print(f"Processing batch {i // batch_size + 1}/{(len(tasks_to_analyze) + batch_size - 1) // batch_size} ({len(batch)} tasks)")

            # Run batch concurrently
            loop = asyncio.get_event_loop()
            results = await asyncio.gather(
                *[loop.run_in_executor(executor, analyze_single_task, task) for task in batch]
            )

            # Count successes and errors
            for result in results:
                if result["success"]:
                    analyzed_count += 1
                else:
                    errors.append(result)
                    print(f"Error analyzing task {result['task_id']}: {result['error']}")

    return {
        "message": f"Analysis complete",
        "analyzed": analyzed_count,
        "skipped": skipped_count,
        "errors": len(errors),
        "total": len(all_tasks),
    }


@app.get("/tasks/{task_id}/clarifying-questions")
async def get_clarifying_questions(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get clarifying questions for a vague task"""

    # Get task insight
    insight = db.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == task_id,
        TaskInsight.user_id == user.id
    ).first()

    if not insight:
        # Task not analyzed yet, get from TickTick and check vagueness
        client = TickTickClient(user.access_token)
        task = client.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if task is vague
        ai = AIEngine()
        vagueness_check = ai.detect_vague_task(
            task_title=task.get("title", ""),
            task_description=task.get("content")
        )

        if not vagueness_check.get("is_vague", False):
            return {
                "is_vague": False,
                "vagueness_score": vagueness_check.get("vagueness_score", 0),
                "questions": []
            }

        return {
            "is_vague": True,
            "vagueness_score": vagueness_check.get("vagueness_score", 0),
            "reasons": vagueness_check.get("reasons", []),
            "questions": vagueness_check.get("clarifying_questions", []),
            "suggestions": vagueness_check.get("suggestions", "")
        }

    # Task already has insight, return stored questions
    if not insight.clarifying_questions:
        return {
            "is_vague": False,
            "vagueness_score": 0,
            "questions": []
        }

    return {
        "is_vague": True,
        "vagueness_score": len(insight.clarifying_questions) / 10.0,  # Estimate based on question count
        "questions": insight.clarifying_questions,
        "existing_answers": insight.clarifying_answers or {},
        "suggestions": ""
    }


@app.post("/tasks/{task_id}/clarifying-answers")
async def save_clarifying_answers(
    task_id: str,
    answers: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save user's answers to clarifying questions"""

    # Get or create task insight
    insight = db.query(TaskInsight).filter(
        TaskInsight.ticktick_task_id == task_id,
        TaskInsight.user_id == user.id
    ).first()

    if not insight:
        # Create new insight with answers
        client = TickTickClient(user.access_token)
        task = client.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        insight = TaskInsight(
            user_id=user.id,
            ticktick_task_id=task_id,
            task_title=task.get("title", ""),
            task_description=task.get("content"),
            project_id=task.get("projectId"),  # Store projectId for proper URL generation
            clarifying_answers=answers
        )
        db.add(insight)
    else:
        # Update existing insight
        insight.clarifying_answers = answers

    db.commit()
    db.refresh(insight)

    # Optionally: Update task description in TickTick with clarifications
    if answers:
        try:
            client = TickTickClient(user.access_token)

            # Build clarification summary
            clarification_text = "\n\n--- Clarifications ---\n"
            for question, answer in answers.items():
                if answer and answer.strip():
                    clarification_text += f"• {question}\n  → {answer}\n"

            # Append to task description
            current_desc = insight.task_description or ""
            if "--- Clarifications ---" not in current_desc:
                new_desc = current_desc + clarification_text

                client.update_task(task_id, content=new_desc)
                insight.task_description = new_desc
                db.commit()
        except Exception as e:
            print(f"Error updating task with clarifications: {e}")
            # Don't fail the request if TickTick update fails

    return {
        "message": "Answers saved successfully",
        "task_id": task_id,
        "answers": answers
    }


@app.post("/tasks/backfill-project-ids")
async def backfill_project_ids(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Backfill projectId for all existing TaskInsight records

    This endpoint fetches all tasks from TickTick and updates the TaskInsight
    records with the correct projectId for each task. This is useful for tasks
    that were analyzed before the projectId field was added.
    """
    client = TickTickClient(user.access_token)

    # Get all task insights for this user
    insights = db.query(TaskInsight).filter(
        TaskInsight.user_id == user.id
    ).all()

    updated_count = 0
    error_count = 0
    already_has_project_id = 0
    no_project_id_count = 0

    for insight in insights:
        # Skip if already has projectId
        if insight.project_id:
            already_has_project_id += 1
            continue

        try:
            # Fetch task from TickTick to get projectId
            task = client.get_task(insight.ticktick_task_id)
            project_id = task.get("projectId")

            if project_id:
                insight.project_id = project_id
                updated_count += 1
                print(f"✓ Updated task '{insight.task_title[:50]}...' with projectId: {project_id}")
            else:
                no_project_id_count += 1
                print(f"⚠ Task '{insight.task_title[:50]}...' has no projectId (might be in Inbox)")

        except Exception as e:
            error_count += 1
            print(f"❌ Error fetching task {insight.ticktick_task_id}: {e}")

    # Commit all changes
    db.commit()

    return {
        "message": "ProjectId backfill complete",
        "updated": updated_count,
        "already_had_project_id": already_has_project_id,
        "no_project_id": no_project_id_count,
        "errors": error_count,
        "total": len(insights)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
