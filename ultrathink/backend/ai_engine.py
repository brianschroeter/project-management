"""AI engine using OpenRouter for task intelligence"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import settings
import json


class AIEngine:
    """AI-powered task intelligence using OpenRouter"""

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
        )
        self.model = settings.ai_model
        self.temperature = settings.ai_temperature

    def _chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """Make a chat completion request"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
        )
        return response.choices[0].message.content

    def breakdown_task(
        self,
        task_title: str,
        task_description: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Break down a task into actionable subtasks"""
        system_prompt = """You are an ADHD-friendly task breakdown assistant. Your goal is to:
1. Break down tasks into 3-7 specific, actionable subtasks
2. Make each subtask concrete and achievable in one sitting
3. Order subtasks logically
4. Identify the energy level needed (low/medium/high)
5. Estimate time for each subtask in minutes
6. Suggest the first "quick win" step to build momentum

Respond ONLY with valid JSON in this exact format:
{
    "subtasks": [
        {"title": "...", "energy": "low|medium|high", "estimated_minutes": 15}
    ],
    "first_step": "The easiest first action to build momentum",
    "total_estimated_minutes": 90,
    "cognitive_load": "light|moderate|heavy",
    "tips": "Optional ADHD-friendly tips for completing this task"
}"""

        context_str = ""
        if context:
            context_str = f"\n\nAdditional context: {json.dumps(context, indent=2)}"

        user_prompt = f"""Task: {task_title}
{f'Description: {task_description}' if task_description else ''}{context_str}

Break this down into actionable subtasks."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages)

        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "subtasks": [{"title": task_title, "energy": "medium", "estimated_minutes": 30}],
                "first_step": task_title,
                "total_estimated_minutes": 30,
                "cognitive_load": "moderate",
            }

    def generate_clarifying_questions(
        self,
        task_title: str,
        task_description: Optional[str] = None,
    ) -> List[str]:
        """Generate clarifying questions for vague tasks"""
        system_prompt = """You are an ADHD-friendly task clarification assistant.
Generate 2-4 specific clarifying questions that will help make a vague task more actionable.
Focus on: desired outcome, success criteria, first steps, potential blockers.

Respond ONLY with valid JSON in this format:
{
    "questions": ["Question 1?", "Question 2?", "Question 3?"]
}"""

        user_prompt = f"""Task: {task_title}
{f'Description: {task_description}' if task_description else ''}

This task seems vague. What questions should I ask to make it more actionable?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            data = json.loads(response)
            return data.get("questions", [])
        except json.JSONDecodeError:
            return [
                "What does success look like for this task?",
                "What's the first concrete step?",
                "What might block progress on this?",
            ]

    def help_with_procrastination(
        self,
        task_title: str,
        task_description: Optional[str] = None,
        days_stale: int = 0,
    ) -> Dict[str, Any]:
        """Help identify blockers and suggest ways to unstuck"""
        system_prompt = """You are an ADHD-friendly productivity coach helping someone unstuck.
Be empathetic, specific, and action-oriented. Avoid guilt or pressure.

Respond ONLY with valid JSON in this format:
{
    "likely_blockers": ["Blocker 1", "Blocker 2"],
    "unstuck_questions": ["Question to identify the real issue?"],
    "tiny_first_step": "The smallest possible action to start",
    "reframe": "A less overwhelming way to think about this task",
    "encouragement": "Brief, genuine encouragement"
}"""

        user_prompt = f"""Task: {task_title}
{f'Description: {task_description}' if task_description else ''}
Days sitting: {days_stale}

Help me figure out why I'm stuck and how to move forward."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "likely_blockers": ["Task feels overwhelming", "Unclear where to start"],
                "unstuck_questions": ["What's the easiest part of this?"],
                "tiny_first_step": "Spend 5 minutes researching the first step",
                "reframe": "You don't have to finish it all today",
                "encouragement": "Starting is the hardest part. You've got this!",
            }

    def prioritize_tasks(
        self,
        tasks: List[Dict[str, Any]],
        current_energy: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Score and prioritize tasks using Eisenhower matrix + AI"""
        system_prompt = """You are a task prioritization expert using the Eisenhower Matrix.
For each task, provide:
- urgency_score (0-10): How time-sensitive is this?
- importance_score (0-10): How much does this matter for goals?
- eisenhower_quadrant: Q1 (urgent+important), Q2 (important, not urgent), Q3 (urgent, not important), Q4 (neither)
- priority_score (0-100): Overall priority
- reasoning: Brief explanation

Respond ONLY with valid JSON array:
[
    {
        "task_id": "id",
        "urgency_score": 8,
        "importance_score": 9,
        "eisenhower_quadrant": "Q1",
        "priority_score": 95,
        "reasoning": "..."
    }
]"""

        tasks_summary = "\n".join([
            f"- [{t.get('id', 'unknown')}] {t.get('title', 'Untitled')}"
            + (f": {t.get('description', '')[:100]}" if t.get('description') else "")
            for t in tasks
        ])

        user_prompt = f"""Tasks to prioritize:
{tasks_summary}

{f'Current energy level: {current_energy}' if current_energy else ''}

Prioritize these tasks."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: simple scoring
            return [
                {
                    "task_id": task.get("id", "unknown"),
                    "urgency_score": 5,
                    "importance_score": 5,
                    "eisenhower_quadrant": "Q2",
                    "priority_score": 50,
                    "reasoning": "Unable to analyze",
                }
                for task in tasks
            ]

    def estimate_time(
        self,
        task_title: str,
        task_description: Optional[str] = None,
        similar_tasks_history: Optional[List[Dict[str, int]]] = None,
    ) -> int:
        """Estimate task duration in minutes"""
        system_prompt = """You are a time estimation expert. Provide realistic time estimates.
Consider: task complexity, typical planning fallacy (people underestimate by 2-3x), and ADHD factors.

Respond ONLY with valid JSON:
{
    "estimated_minutes": 60,
    "reasoning": "Brief explanation",
    "range_low": 45,
    "range_high": 90
}"""

        history_str = ""
        if similar_tasks_history:
            history_str = "\n\nSimilar tasks history:\n" + "\n".join([
                f"- {h.get('title', 'Task')}: estimated {h.get('estimated', 0)}min, actual {h.get('actual', 0)}min"
                for h in similar_tasks_history[:5]
            ])

        user_prompt = f"""Task: {task_title}
{f'Description: {task_description}' if task_description else ''}{history_str}

Estimate realistic time needed."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            data = json.loads(response)
            return data.get("estimated_minutes", 30)
        except json.JSONDecodeError:
            return 30  # Default 30 minutes

    def classify_energy_level(
        self,
        task_title: str,
        task_description: Optional[str] = None,
    ) -> str:
        """Classify task energy level: low, medium, high"""
        system_prompt = """You are an energy classification expert.
Classify tasks by energy/focus needed:
- low: Routine, mechanical, doesn't need deep focus
- medium: Requires some thinking but not exhausting
- high: Complex, creative, or requires deep concentration

Respond ONLY with valid JSON:
{
    "energy_level": "low|medium|high",
    "reasoning": "Why"
}"""

        user_prompt = f"""Task: {task_title}
{f'Description: {task_description}' if task_description else ''}

What energy level does this require?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages, temperature=0.3)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            data = json.loads(response)
            return data.get("energy_level", "medium")
        except json.JSONDecodeError:
            return "medium"

    def detect_vague_task(
        self,
        task_title: str,
        task_description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Detect if a task is vague and needs clarification
        Returns: {
            "is_vague": bool,
            "vagueness_score": float (0-10),
            "reasons": ["reason 1", "reason 2"],
            "clarifying_questions": ["question 1", "question 2"]
        }
        """
        system_prompt = """You are a task clarity analyst. Evaluate if a task is vague or well-defined.

A task is vague if it:
- Lacks specific action verbs
- Has unclear success criteria
- Is too broad or abstract
- Missing important details (who, what, when, where, how)
- Contains ambiguous or subjective terms

Respond ONLY with valid JSON:
{
    "is_vague": true/false,
    "vagueness_score": 7.5,
    "reasons": ["Lacks specific action", "No clear deadline"],
    "clarifying_questions": ["What specific action needs to be taken?", "When should this be completed?"],
    "suggestions": "Optional: how to make it more specific"
}"""

        user_prompt = f"""Task: {task_title}
{f'Description: {task_description}' if task_description else 'No description provided'}

Is this task vague? Does it need clarification?"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages, temperature=0.3)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            data = json.loads(response)

            # Ensure all required fields are present
            return {
                "is_vague": data.get("is_vague", False),
                "vagueness_score": data.get("vagueness_score", 0.0),
                "reasons": data.get("reasons", []),
                "clarifying_questions": data.get("clarifying_questions", []),
                "suggestions": data.get("suggestions", "")
            }
        except json.JSONDecodeError:
            # Conservative fallback - assume not vague if AI fails
            return {
                "is_vague": False,
                "vagueness_score": 0.0,
                "reasons": [],
                "clarifying_questions": [],
                "suggestions": ""
            }

    def parse_email_to_task(
        self,
        email_subject: str,
        email_body: str,
        email_from: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Parse email into task information
        Extracts task title, description, priority, and identifies if clarification is needed
        """
        system_prompt = """You are an email-to-task parser for an ADHD-friendly task manager.
Extract actionable task information from emails. Focus on:
1. Clear, concise task title (what needs to be done)
2. Relevant description (remove email signatures, headers, irrelevant content)
3. Suggested priority based on urgency indicators
4. Whether the task needs clarification

Respond ONLY with valid JSON:
{
    "task_title": "Clean, action-oriented title",
    "task_description": "Concise description with key details",
    "suggested_priority": "high|medium|low",
    "needs_clarification": true/false,
    "clarifying_questions": ["Question 1?", "Question 2?"],
    "suggested_project": "Work|Personal|null",
    "is_actionable": true/false,
    "reasoning": "Brief explanation of parsing decisions"
}"""

        user_prompt = f"""Email Subject: {email_subject}
{f'From: {email_from}' if email_from else ''}

Email Body:
{email_body[:2000]}  # Limit to first 2000 chars

Parse this email into a task."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self._chat_completion(messages)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "task_title": email_subject,
                "task_description": email_body[:500],
                "suggested_priority": "medium",
                "needs_clarification": True,
                "clarifying_questions": [
                    "What is the desired outcome?",
                    "When does this need to be done?",
                ],
                "suggested_project": None,
                "is_actionable": True,
                "reasoning": "Fallback parsing due to AI response error",
            }
