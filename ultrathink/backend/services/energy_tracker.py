"""Energy level tracking and pattern analysis"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models import EnergyLog, TaskInsight


class EnergyTracker:
    """Tracks energy levels and suggests tasks accordingly"""

    def __init__(self, db: Session):
        self.db = db

    def log_energy(
        self,
        user_id: int,
        energy_level: str,
        focus_quality: Optional[str] = None,
    ) -> EnergyLog:
        """Log current energy level"""

        now = datetime.utcnow()
        hour = now.hour

        # Determine time of day
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        log = EnergyLog(
            user_id=user_id,
            energy_level=energy_level,
            focus_quality=focus_quality,
            time_of_day=time_of_day,
            day_of_week=now.strftime("%A"),
        )

        self.db.add(log)
        self.db.commit()
        return log

    def get_current_energy_recommendation(self, user_id: int) -> str:
        """Predict likely current energy based on patterns"""

        now = datetime.utcnow()
        hour = now.hour
        day_of_week = now.strftime("%A")

        # Determine time of day
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        # Look at historical patterns for this time/day
        recent_logs = self.db.query(EnergyLog).filter(
            EnergyLog.user_id == user_id,
            EnergyLog.time_of_day == time_of_day,
            EnergyLog.day_of_week == day_of_week,
        ).order_by(EnergyLog.timestamp.desc()).limit(10).all()

        if not recent_logs:
            # Default heuristics
            if time_of_day == "morning":
                return "high"
            elif time_of_day == "afternoon":
                return "medium"
            else:
                return "low"

        # Most common energy level for this pattern
        energy_counts = {}
        for log in recent_logs:
            energy_counts[log.energy_level] = energy_counts.get(log.energy_level, 0) + 1

        return max(energy_counts, key=energy_counts.get)

    def suggest_tasks_by_energy(
        self,
        user_id: int,
        energy_level: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Suggest tasks matching current energy level"""

        insights = self.db.query(TaskInsight).filter(
            TaskInsight.user_id == user_id,
            TaskInsight.completed == False,
            TaskInsight.energy_level == energy_level,
        ).order_by(
            TaskInsight.priority_score.desc()
        ).limit(limit).all()

        return [
            {
                "task_id": insight.ticktick_task_id,
                "title": insight.task_title,
                "energy_level": insight.energy_level,
                "estimated_minutes": insight.estimated_duration_minutes,
                "priority_score": insight.priority_score,
                "first_step": insight.ai_breakdown.get("first_step") if insight.ai_breakdown else None,
            }
            for insight in insights
        ]

    def get_energy_patterns(
        self,
        user_id: int,
        days_back: int = 30,
    ) -> Dict[str, Any]:
        """Analyze energy patterns over time"""

        cutoff = datetime.utcnow() - timedelta(days=days_back)

        logs = self.db.query(EnergyLog).filter(
            EnergyLog.user_id == user_id,
            EnergyLog.timestamp >= cutoff,
        ).all()

        if not logs:
            return {"message": "Not enough data yet"}

        # Analyze by time of day
        by_time = {}
        for log in logs:
            time = log.time_of_day
            if time not in by_time:
                by_time[time] = []
            by_time[time].append(log.energy_level)

        patterns = {}
        for time, energies in by_time.items():
            energy_counts = {}
            for e in energies:
                energy_counts[e] = energy_counts.get(e, 0) + 1

            most_common = max(energy_counts, key=energy_counts.get)
            patterns[time] = {
                "most_common_energy": most_common,
                "distribution": energy_counts,
            }

        return {
            "total_logs": len(logs),
            "patterns_by_time_of_day": patterns,
            "insights": self._generate_energy_insights(patterns),
        }

    def _generate_energy_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights from patterns"""

        insights = []

        for time, data in patterns.items():
            energy = data["most_common_energy"]
            insights.append(f"You're usually {energy} energy in the {time}")

        return insights

    def mark_task_completed_at_energy(
        self,
        user_id: int,
        task_id: str,
        energy_level: str,
    ) -> None:
        """Record that a task was completed at a certain energy level"""

        # Update the latest energy log
        latest_log = self.db.query(EnergyLog).filter(
            EnergyLog.user_id == user_id
        ).order_by(EnergyLog.timestamp.desc()).first()

        if latest_log:
            tasks = latest_log.tasks_completed or []
            tasks.append(task_id)
            latest_log.tasks_completed = tasks
            self.db.commit()
