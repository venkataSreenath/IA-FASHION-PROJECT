import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List

DB_PATH = Path("fashion_feedback.db")


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create and return a SQLite connection."""
    return sqlite3.connect(db_path)


def initialize_database(db_path: Path = DB_PATH) -> None:
    """Initialize SQLite database and feedback table."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_disliked_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                disliked_item_features TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_disliked_features_user_id
            ON user_disliked_features (user_id)
            """
        )
        
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_text TEXT NOT NULL,
                utility_score INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id
            ON user_preferences (user_id)
            """
        )
        conn.commit()


def add_user_preference(user_id: str, preference_text: str, utility_score: int, db_path: Path = DB_PATH) -> None:
    """Insert one utility-based preference row for a given user."""
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_preferences (user_id, preference_text, utility_score, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, preference_text, utility_score, timestamp),
        )
        conn.commit()


def get_recent_preferences(user_id: str, limit: int = 20, db_path: Path = DB_PATH) -> List[dict]:
    """Return latest user preferences with their utility scores."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT preference_text, utility_score
            FROM user_preferences
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
    return [{"text": row[0], "score": row[1]} for row in rows]


def add_disliked_feature(user_id: str, disliked_item_feature: str, db_path: Path = DB_PATH) -> None:
    """Insert one disliked feature row for a given user."""
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_disliked_features (user_id, disliked_item_features, timestamp)
            VALUES (?, ?, ?)
            """,
            (user_id, disliked_item_feature, timestamp),
        )
        conn.commit()


def get_disliked_features(user_id: str, db_path: Path = DB_PATH) -> List[str]:
    """Return all disliked item features for the given user."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT disliked_item_features
            FROM user_disliked_features
            WHERE user_id = ?
            ORDER BY timestamp ASC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()
    return [row[0] for row in rows]


def get_recent_disliked_features(
    user_id: str, limit: int = 20, db_path: Path = DB_PATH
) -> List[str]:
    """Return latest disliked features to support fast filtering during inference."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT disliked_item_features
            FROM user_disliked_features
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (user_id, limit),
        )
        rows = cursor.fetchall()
    return [row[0] for row in rows]


if __name__ == "__main__":
    initialize_database()
    print(f"SQLite database initialized at: {DB_PATH.resolve()}")
