"""
Backfill projectId for existing TaskInsight records

This script fetches all tasks from TickTick and updates the TaskInsight records
with the correct projectId for each task.
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
    """Backfill projectId for all TaskInsight records"""

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

        # Get all task insights
        insights = db.query(TaskInsight).all()
        print(f"\n📊 Found {len(insights)} task insights to process")

        updated_count = 0
        error_count = 0
        already_has_project_id = 0

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
                    print(f"  ✓ Updated task '{insight.task_title[:50]}...' with projectId: {project_id}")
                else:
                    print(f"  ⚠ Task '{insight.task_title[:50]}...' has no projectId (might be in Inbox)")

            except Exception as e:
                error_count += 1
                print(f"  ❌ Error fetching task {insight.ticktick_task_id}: {e}")

        # Commit all changes
        db.commit()

        print(f"\n{'='*60}")
        print(f"✅ Backfill complete!")
        print(f"  - Updated: {updated_count}")
        print(f"  - Already had projectId: {already_has_project_id}")
        print(f"  - Errors: {error_count}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"\n❌ Error during backfill: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Starting projectId backfill...\n")
    backfill_project_ids()
