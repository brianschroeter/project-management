"""
Backfill projectId for existing TaskInsight records (Version 2)

This version uses the bulk tasks endpoint instead of individual task lookups
to avoid 500 errors from the TickTick API.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db
from backend.models import TaskInsight, User
from backend.ticktick_client import TickTickClient


def backfill_project_ids():
    """Backfill projectId for all TaskInsight records using bulk tasks endpoint"""

    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # Get the user (assumes single user for now)
        user = db.query(User).first()
        if not user:
            print("❌ No user found. Please authenticate with TickTick first.")
            return

        print(f"✓ Found user ID: {user.id}")

        # Initialize TickTick client
        client = TickTickClient(user.access_token)

        # Get all tasks from TickTick (bulk endpoint)
        print("\n📥 Fetching all tasks from TickTick...")
        try:
            all_tasks = client.get_tasks(completed=False)
            print(f"✓ Retrieved {len(all_tasks)} tasks from TickTick")
        except Exception as e:
            print(f"❌ Error fetching tasks from TickTick: {e}")
            return

        # Create a mapping of task_id -> projectId
        task_project_map = {}
        for task in all_tasks:
            task_id = task.get("id")
            project_id = task.get("projectId")
            if task_id and project_id:
                task_project_map[task_id] = project_id

        print(f"✓ Built mapping for {len(task_project_map)} tasks with projectId")

        # Get all task insights
        insights = db.query(TaskInsight).all()
        print(f"\n📊 Found {len(insights)} task insights to process")

        updated_count = 0
        error_count = 0
        already_has_project_id = 0
        no_project_id_count = 0
        not_found_count = 0

        for insight in insights:
            # Skip if already has projectId
            if insight.project_id:
                already_has_project_id += 1
                continue

            task_id = insight.ticktick_task_id

            # Check if task exists in our mapping
            if task_id in task_project_map:
                project_id = task_project_map[task_id]
                insight.project_id = project_id
                updated_count += 1
                print(f"  ✓ Updated task '{insight.task_title[:50]}...' with projectId: {project_id}")
            else:
                not_found_count += 1
                print(f"  ⚠ Task '{insight.task_title[:50]}...' not found in current TickTick tasks (may be completed/deleted)")

        # Commit all changes
        db.commit()

        print(f"\n{'='*60}")
        print(f"✅ Backfill complete!")
        print(f"  - Updated: {updated_count}")
        print(f"  - Already had projectId: {already_has_project_id}")
        print(f"  - Not found in TickTick: {not_found_count}")
        print(f"  - Errors: {error_count}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ Error during backfill: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Starting projectId backfill (V2 - using bulk endpoint)...\n")
    backfill_project_ids()
