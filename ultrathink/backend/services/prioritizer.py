"""Task prioritization service"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from backend.ai_engine import AIEngine
from backend.models import TaskInsight


class TaskPrioritizer:
    """Prioritizes tasks using Eisenhower Matrix + AI"""

    def __init__(self, db: Session):
        self.db = db
        self.ai = AIEngine()

    def prioritize_user_tasks(
        self,
        user_id: int,
        tasks: List[Dict[str, Any]],
        current_energy: str = "medium",
    ) -> List[Dict[str, Any]]:
        """Prioritize tasks and update insights"""

        # Get AI prioritization
        priorities = self.ai.prioritize_tasks(tasks, current_energy)

        # Update database with priorities
        for priority in priorities:
            task_id = priority.get("task_id")
            insight = self.db.query(TaskInsight).filter(
                TaskInsight.ticktick_task_id == task_id
            ).first()

            if insight:
                insight.urgency_score = priority.get("urgency_score")
                insight.importance_score = priority.get("importance_score")
                insight.eisenhower_quadrant = priority.get("eisenhower_quadrant")
                insight.priority_score = priority.get("priority_score")
                insight.last_updated_at = datetime.utcnow()

        self.db.commit()

        # Merge task data with priorities
        prioritized_tasks = []
        for task in tasks:
            task_id = task.get("id")
            priority = next((p for p in priorities if p["task_id"] == task_id), None)

            if priority:
                prioritized_tasks.append({
                    **task,
                    "priority_data": priority,
                })

        # Sort by priority score (descending)
        prioritized_tasks.sort(
            key=lambda x: x.get("priority_data", {}).get("priority_score", 0),
            reverse=True,
        )

        return prioritized_tasks

    def get_top_tasks(
        self,
        user_id: int,
        limit: int = 3,
        energy_level: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get top N tasks to focus on"""

        query = self.db.query(TaskInsight).filter(
            TaskInsight.user_id == user_id,
            TaskInsight.completed == False,
        )

        if energy_level:
            query = query.filter(TaskInsight.energy_level == energy_level)

        # Order by priority score
        insights = query.order_by(
            TaskInsight.priority_score.desc()
        ).limit(limit).all()

        return [
            {
                "task_id": insight.ticktick_task_id,
                "title": insight.task_title,
                "priority_score": insight.priority_score,
                "eisenhower_quadrant": insight.eisenhower_quadrant,
                "energy_level": insight.energy_level,
                "estimated_minutes": insight.estimated_duration_minutes,
                "project_id": insight.project_id,  # Include projectId for proper TickTick URL generation
            }
            for insight in insights
        ]

    def get_tasks_by_quadrant(
        self,
        user_id: int,
        quadrant: str,
    ) -> List[Dict[str, Any]]:
        """Get tasks in a specific Eisenhower quadrant"""

        insights = self.db.query(TaskInsight).filter(
            TaskInsight.user_id == user_id,
            TaskInsight.completed == False,
            TaskInsight.eisenhower_quadrant == quadrant,
        ).order_by(TaskInsight.priority_score.desc()).all()

        return [
            {
                "task_id": insight.ticktick_task_id,
                "title": insight.task_title,
                "priority_score": insight.priority_score,
            }
            for insight in insights
        ]
