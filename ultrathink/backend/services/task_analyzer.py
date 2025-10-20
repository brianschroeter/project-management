"""Task analysis service combining AI and database operations"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.ai_engine import AIEngine
from backend.ticktick_client import TickTickClient
from backend.models import TaskInsight, User


class TaskAnalyzer:
    """Analyzes tasks using AI and stores insights"""

    def __init__(self, db: Session, ticktick_client: TickTickClient):
        self.db = db
        self.ticktick = ticktick_client
        self.ai = AIEngine()

    def analyze_new_task(
        self,
        user_id: int,
        task_id: str,
        task_title: str,
        task_description: Optional[str] = None,
        auto_create_subtasks: bool = True,
    ) -> Dict[str, Any]:
        """Analyze a new task and optionally create subtasks"""

        # Generate AI breakdown (single call with all insights)
        breakdown = self.ai.breakdown_task(task_title, task_description)

        # Map cognitive_load to energy_level (no additional API call needed!)
        cognitive_load = breakdown.get("cognitive_load", "moderate")
        energy_level_map = {"light": "low", "moderate": "medium", "heavy": "high"}
        energy_level = energy_level_map.get(cognitive_load, "medium")

        # Estimate time
        estimated_duration = breakdown.get("total_estimated_minutes", 30)

        # Create or update insight record
        insight = self.db.query(TaskInsight).filter(
            TaskInsight.ticktick_task_id == task_id
        ).first()

        if not insight:
            # Fetch full task to get projectId
            try:
                full_task = self.ticktick.get_task(task_id)
                project_id = full_task.get("projectId")
            except Exception as e:
                print(f"Warning: Could not fetch projectId for task {task_id}: {e}")
                project_id = None

            insight = TaskInsight(
                user_id=user_id,
                ticktick_task_id=task_id,
                task_title=task_title,
                task_description=task_description,
                project_id=project_id,
            )
            self.db.add(insight)

        insight.ai_breakdown = breakdown
        insight.energy_level = energy_level
        insight.estimated_duration_minutes = estimated_duration
        insight.cognitive_load = breakdown.get("cognitive_load", "moderate")
        insight.last_updated_at = datetime.utcnow()

        self.db.commit()

        # Optionally create subtasks in TickTick
        created_subtasks = []
        if auto_create_subtasks and breakdown.get("subtasks"):
            for subtask in breakdown["subtasks"]:
                created = self.ticktick.add_subtask(
                    parent_task_id=task_id,
                    title=subtask["title"],
                    content=f"Energy: {subtask.get('energy', 'medium')}, Est: {subtask.get('estimated_minutes', 15)}min",
                )
                created_subtasks.append(created)

        return {
            "breakdown": breakdown,
            "energy_level": energy_level,
            "estimated_minutes": estimated_duration,
            "created_subtasks": created_subtasks,
        }

    def identify_vague_tasks(self, user_id: int) -> List[Dict[str, Any]]:
        """Find tasks that might need clarification"""

        # Get tasks from TickTick
        tasks = self.ticktick.get_tasks(completed=False)

        vague_tasks = []
        for task in tasks:
            task_id = task.get("id")
            title = task.get("title", "")
            description = task.get("content", "")

            # Heuristics for vagueness
            is_vague = (
                len(title.split()) <= 3  # Very short title
                or not description  # No description
                or any(word in title.lower() for word in ["research", "plan", "think about", "look into"])
            )

            if is_vague:
                # Check if we already have insights
                insight = self.db.query(TaskInsight).filter(
                    TaskInsight.ticktick_task_id == task_id
                ).first()

                if not insight or not insight.clarifying_questions:
                    # Generate clarifying questions
                    questions = self.ai.generate_clarifying_questions(title, description)

                    if not insight:
                        insight = TaskInsight(
                            user_id=user_id,
                            ticktick_task_id=task_id,
                            task_title=title,
                            task_description=description,
                            project_id=task.get("projectId"),  # Extract projectId from task object
                        )
                        self.db.add(insight)

                    insight.clarifying_questions = questions
                    self.db.commit()

                    vague_tasks.append({
                        "task": task,
                        "questions": questions,
                    })

        return vague_tasks

    def detect_stale_tasks(
        self,
        user_id: int,
        stale_threshold_days: int = 3,
    ) -> List[Dict[str, Any]]:
        """Detect tasks that have been sitting for too long"""

        cutoff_date = datetime.utcnow() - timedelta(days=stale_threshold_days)

        # Get insights for old tasks
        stale_insights = self.db.query(TaskInsight).filter(
            TaskInsight.user_id == user_id,
            TaskInsight.completed == False,
            TaskInsight.first_seen_at < cutoff_date,
        ).all()

        stale_tasks = []
        for insight in stale_insights:
            days_stale = (datetime.utcnow() - insight.first_seen_at).days

            # Get help from AI
            unstuck_help = self.ai.help_with_procrastination(
                insight.task_title,
                insight.task_description,
                days_stale,
            )

            # Update insight
            insight.days_since_created = days_stale
            insight.blockers_identified = unstuck_help.get("likely_blockers", [])

            # Fetch full task from TickTick to get projectId and other metadata
            full_task_data = {}
            try:
                full_task = self.ticktick.get_task(insight.ticktick_task_id)
                full_task_data = {
                    "projectId": full_task.get("projectId"),
                    "id": full_task.get("id"),
                    "title": full_task.get("title"),
                    "content": full_task.get("content"),
                }
            except Exception as e:
                print(f"Error fetching full task data for {insight.ticktick_task_id}: {e}")
                if insight.project_id:
                    print(f"Using stored projectId for task {insight.ticktick_task_id}: {insight.project_id}")
                else:
                    print(f"WARNING: No projectId available for task {insight.ticktick_task_id} - link may not work!")
                # Fallback to insight data (includes stored projectId)
                full_task_data = {
                    "id": insight.ticktick_task_id,
                    "title": insight.task_title,
                    "content": insight.task_description,
                    "projectId": insight.project_id,  # Use stored projectId as fallback
                }

            stale_tasks.append({
                **full_task_data,
                "task_id": insight.ticktick_task_id,  # Keep for compatibility
                "task_title": insight.task_title,  # Keep for compatibility
                "days_stale": days_stale,
                "unstuck_help": unstuck_help,
            })

        self.db.commit()
        return stale_tasks

    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed AI insights for a specific task"""

        insight = self.db.query(TaskInsight).filter(
            TaskInsight.ticktick_task_id == task_id
        ).first()

        if not insight:
            return None

        return {
            "task_title": insight.task_title,
            "breakdown": insight.ai_breakdown,
            "energy_level": insight.energy_level,
            "estimated_minutes": insight.estimated_duration_minutes,
            "cognitive_load": insight.cognitive_load,
            "priority_score": insight.priority_score,
            "eisenhower_quadrant": insight.eisenhower_quadrant,
            "clarifying_questions": insight.clarifying_questions,
            "days_since_created": insight.days_since_created,
            "blockers": insight.blockers_identified,
        }

    def update_completion(
        self,
        task_id: str,
        actual_duration_minutes: Optional[int] = None,
    ) -> None:
        """Update task as completed and record actual time"""

        insight = self.db.query(TaskInsight).filter(
            TaskInsight.ticktick_task_id == task_id
        ).first()

        if insight:
            insight.completed = True
            insight.completed_at = datetime.utcnow()
            if actual_duration_minutes:
                insight.actual_duration_minutes = actual_duration_minutes

            self.db.commit()
