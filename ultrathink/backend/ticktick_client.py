"""TickTick API client with OAuth2 support"""
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from requests_oauthlib import OAuth2Session
from config import settings


class TickTickClient:
    """Client for interacting with TickTick API"""

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.api_base = settings.ticktick_api_base
        self.session = requests.Session()
        if access_token:
            self.session.headers.update({"Authorization": f"Bearer {access_token}"})

    @staticmethod
    def get_authorization_url(state: str = "ultrathink") -> str:
        """Generate OAuth authorization URL"""
        oauth = OAuth2Session(
            settings.ticktick_client_id,
            redirect_uri=settings.ticktick_redirect_uri,
            scope=["tasks:read", "tasks:write"],
        )
        authorization_url, _ = oauth.authorization_url(
            settings.ticktick_oauth_url,
            state=state,
        )
        return authorization_url

    @staticmethod
    def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_data = {
            "client_id": settings.ticktick_client_id,
            "client_secret": settings.ticktick_client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.ticktick_redirect_uri,
            "scope": "tasks:read tasks:write",
        }

        response = requests.post(settings.ticktick_token_url, data=token_data)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        token_data = {
            "client_id": settings.ticktick_client_id,
            "client_secret": settings.ticktick_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(settings.ticktick_token_url, data=token_data)
        response.raise_for_status()
        return response.json()

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to TickTick API"""
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.text else {}

    # Task operations
    def get_tasks(
        self,
        project_id: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Get tasks, optionally filtered by project and completion status"""
        # TickTick API requires fetching tasks through projects
        # Get all projects first, then get tasks from each
        all_tasks = []

        try:
            if project_id:
                # Get tasks from specific project
                project_data = self._request("GET", f"/project/{project_id}/data")
                all_tasks.extend(project_data.get("tasks", []))
            else:
                # Get tasks from all projects
                projects = self.get_projects()
                for project in projects:
                    try:
                        project_data = self._request("GET", f"/project/{project['id']}/data")
                        all_tasks.extend(project_data.get("tasks", []))
                    except Exception as e:
                        print(f"Error fetching tasks from project {project.get('name', project['id'])}: {e}")
                        continue
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []

        # Filter by completion status if specified
        if completed is not None:
            status_filter = 2 if completed else 0  # TickTick: 0=active, 2=completed
            all_tasks = [t for t in all_tasks if t.get("status") == status_filter]

        return all_tasks

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID"""
        return self._request("GET", f"/task/{task_id}")

    def create_task(
        self,
        title: str,
        content: Optional[str] = None,
        project_id: Optional[str] = None,
        priority: Optional[int] = None,
        due_date: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new task"""
        task_data = {
            "title": title,
        }

        if content:
            task_data["content"] = content
        if project_id:
            task_data["projectId"] = project_id
        if priority is not None:
            task_data["priority"] = priority
        if due_date:
            task_data["dueDate"] = due_date.isoformat()
        if tags:
            task_data["tags"] = tags

        return self._request("POST", "/task", json=task_data)

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        priority: Optional[int] = None,
        completed: Optional[bool] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing task"""
        # First get the current task
        current_task = self.get_task(task_id)

        # Update fields
        if title is not None:
            current_task["title"] = title
        if content is not None:
            current_task["content"] = content
        if priority is not None:
            current_task["priority"] = priority
        if completed is not None:
            current_task["status"] = 1 if completed else 0
        if tags is not None:
            current_task["tags"] = tags

        return self._request("POST", f"/task/{task_id}", json=current_task)

    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as complete"""
        return self.update_task(task_id, completed=True)

    def delete_task(self, task_id: str) -> None:
        """Delete a task"""
        self._request("DELETE", f"/task/{task_id}")

    def add_subtask(
        self,
        parent_task_id: str,
        title: str,
        content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a subtask to a parent task"""
        subtask_data = {
            "title": title,
            "parentId": parent_task_id,
        }
        if content:
            subtask_data["content"] = content

        return self._request("POST", "/task", json=subtask_data)

    # Project operations
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        return self._request("GET", "/project")

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project by ID"""
        return self._request("GET", f"/project/{project_id}")

    # Tag operations
    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all tags"""
        return self._request("GET", "/tag")

    # Batch operations
    def batch_create_subtasks(
        self,
        parent_task_id: str,
        subtasks: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Create multiple subtasks at once"""
        results = []
        for subtask in subtasks:
            result = self.add_subtask(
                parent_task_id,
                subtask["title"],
                subtask.get("content"),
            )
            results.append(result)
        return results
