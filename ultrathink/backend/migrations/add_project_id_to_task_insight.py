"""
Migration: Add project_id column to task_insights table
Created: 2025-10-20

This migration adds the project_id field to TaskInsight model to support
proper TickTick URL generation with project context.

Usage: python3 add_project_id_to_task_insight.py [database_path]
Example: python3 add_project_id_to_task_insight.py ../../ultrathink.db
"""
import sys
import sqlite3
from pathlib import Path


def upgrade(db_path="../ultrathink.db"):
    """Add project_id column to task_insights table"""
    # Resolve the database path
    db_file = Path(__file__).parent.parent / db_path

    if not db_file.exists():
        print(f"✗ Database file not found: {db_file}")
        print(f"  Please provide the correct path to ultrathink.db")
        return False

    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(task_insights)")
        columns = [row[1] for row in cursor.fetchall()]

        if "project_id" in columns:
            print("✓ Column project_id already exists in task_insights table")
            conn.close()
            return True

        # Add the new column
        cursor.execute("ALTER TABLE task_insights ADD COLUMN project_id VARCHAR")
        conn.commit()
        conn.close()

        print("✓ Successfully added project_id column to task_insights table")
        print(f"  Database: {db_file}")
        return True

    except Exception as e:
        print(f"✗ Error adding project_id column: {e}")
        return False


def downgrade():
    """Remove project_id column from task_insights table"""
    with engine.connect() as conn:
        try:
            # SQLite doesn't support DROP COLUMN, so we need to recreate the table
            # This is a simplified version - in production you'd want to preserve data
            print("Note: SQLite doesn't support DROP COLUMN natively.")
            print("To downgrade, you would need to recreate the table without project_id.")
            print("This migration does not include automatic downgrade for SQLite.")
        except Exception as e:
            print(f"✗ Error in downgrade: {e}")
            raise


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
