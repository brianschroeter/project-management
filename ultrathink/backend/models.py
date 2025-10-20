"""Database models for Ultrathink"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class User(Base):
    """User with TickTick OAuth credentials"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    ticktick_user_id = Column(String, unique=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Gmail OAuth tokens
    gmail_access_token = Column(String, nullable=True)
    gmail_refresh_token = Column(String, nullable=True)
    gmail_token_expiry = Column(DateTime, nullable=True)
    gmail_email = Column(String, nullable=True)

    # Outlook OAuth tokens
    outlook_access_token = Column(String, nullable=True)
    outlook_refresh_token = Column(String, nullable=True)
    outlook_token_expiry = Column(DateTime, nullable=True)
    outlook_email = Column(String, nullable=True)

    # Relationships
    task_insights = relationship("TaskInsight", back_populates="user")
    energy_logs = relationship("EnergyLog", back_populates="user")


class TaskInsight(Base):
    """AI-generated insights and metadata for tasks"""
    __tablename__ = "task_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticktick_task_id = Column(String, index=True)
    project_id = Column(String, nullable=True)  # TickTick project ID for proper URL generation

    # Task metadata
    task_title = Column(String)
    task_description = Column(Text, nullable=True)

    # Email source metadata
    email_source = Column(String, nullable=True)  # 'gmail' or 'outlook'
    email_message_id = Column(String, nullable=True, index=True)  # Original email message ID
    email_link = Column(String, nullable=True)  # Direct link to email in Gmail/Outlook
    email_has_attachments = Column(Boolean, default=False)
    email_attachment_count = Column(Integer, nullable=True)
    email_subject = Column(String, nullable=True)  # Original email subject
    email_from = Column(String, nullable=True)  # Email sender
    email_received_at = Column(DateTime, nullable=True)  # When email was received

    # AI-generated content
    ai_breakdown = Column(JSON, nullable=True)  # List of subtask suggestions
    clarifying_questions = Column(JSON, nullable=True)  # Questions asked
    clarifying_answers = Column(JSON, nullable=True)  # User's answers

    # Energy and difficulty
    energy_level = Column(String, nullable=True)  # low, medium, high
    estimated_duration_minutes = Column(Integer, nullable=True)
    actual_duration_minutes = Column(Integer, nullable=True)
    cognitive_load = Column(String, nullable=True)  # light, moderate, heavy

    # Prioritization
    priority_score = Column(Float, nullable=True)
    urgency_score = Column(Float, nullable=True)
    importance_score = Column(Float, nullable=True)
    eisenhower_quadrant = Column(String, nullable=True)  # Q1, Q2, Q3, Q4

    # Procrastination tracking
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    days_since_created = Column(Integer, default=0)
    times_deferred = Column(Integer, default=0)
    blockers_identified = Column(JSON, nullable=True)

    # Completion
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="task_insights")


class EnergyLog(Base):
    """User energy level logs for pattern tracking"""
    __tablename__ = "energy_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    energy_level = Column(String)  # low, medium, high
    focus_quality = Column(String, nullable=True)  # scattered, moderate, focused

    # Context
    time_of_day = Column(String, nullable=True)  # morning, afternoon, evening, night
    day_of_week = Column(String, nullable=True)

    # Tasks completed during this energy level
    tasks_completed = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="energy_logs")


class TaskCompletionHistory(Base):
    """Track actual vs estimated completion times"""
    __tablename__ = "task_completion_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ticktick_task_id = Column(String, index=True)

    task_title = Column(String)
    task_type = Column(String, nullable=True)  # meeting, coding, writing, etc.

    estimated_minutes = Column(Integer)
    actual_minutes = Column(Integer)
    accuracy_ratio = Column(Float)  # actual / estimated

    energy_level_at_completion = Column(String, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)


class AIInteraction(Base):
    """Log AI interactions for learning and improvement"""
    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    interaction_type = Column(String)  # breakdown, clarify, prioritize, unstuck
    task_id = Column(String, nullable=True)

    prompt = Column(Text)
    response = Column(Text)
    model_used = Column(String)
    tokens_used = Column(Integer, nullable=True)

    user_feedback = Column(String, nullable=True)  # helpful, not_helpful, neutral

    created_at = Column(DateTime, default=datetime.utcnow)
