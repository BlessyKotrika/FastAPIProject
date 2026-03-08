import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any

from app.utils.exceptions import ResourceNotFoundError, ValidationException


class ChatHistoryService:
    def __init__(self, db_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or str(data_dir / "chat_history.db")
        self._init_schema()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    language TEXT,
                    crop TEXT,
                    location TEXT,
                    summary_text TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content_json TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
                """
            )
            conn.commit()

    def _new_conversation_id(self) -> str:
        return f"conv_{uuid.uuid4().hex[:12]}"

    def _new_message_id(self) -> str:
        return f"msg_{uuid.uuid4().hex[:12]}"

    def create_conversation(
        self,
        user_id: str,
        language: str,
        crop: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        conversation_id = self._new_conversation_id()

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (id, user_id, language, crop, location, summary_text)
                VALUES (?, ?, ?, ?, ?, '')
                """,
                (conversation_id, user_id, language, crop, location),
            )
            conn.commit()

            cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
            row = cursor.fetchone()
            return dict(row)

    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
                (conversation_id, user_id),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def require_conversation(self, conversation_id: str, user_id: str) -> Dict[str, Any]:
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ResourceNotFoundError("Conversation", conversation_id)
        return conversation

    def upsert_conversation_metadata(
        self,
        conversation_id: str,
        user_id: str,
        language: Optional[str] = None,
        crop: Optional[str] = None,
        location: Optional[str] = None
    ) -> None:
        # Ensure it belongs to user
        self.require_conversation(conversation_id, user_id)

        updates = []
        values = []

        if language is not None:
            updates.append("language = ?")
            values.append(language)
        if crop is not None:
            updates.append("crop = ?")
            values.append(crop)
        if location is not None:
            updates.append("location = ?")
            values.append(location)

        if not updates:
            return

        values.extend([conversation_id, user_id])

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                UPDATE conversations
                SET {", ".join(updates)}
                WHERE id = ? AND user_id = ?
                """,
                tuple(values),
            )
            conn.commit()

    def update_summary(self, conversation_id: str, user_id: str, summary_text: str) -> None:
        self.require_conversation(conversation_id, user_id)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE conversations
                SET summary_text = ?
                WHERE id = ? AND user_id = ?
                """,
                (summary_text, conversation_id, user_id),
            )
            conn.commit()

    def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        content: Dict[str, Any],
        message_id: Optional[str] = None,
    ) -> str:
        if role not in {"user", "assistant"}:
            raise ValidationException("Invalid role. Must be 'user' or 'assistant'.")

        # Ensure conversation ownership
        self.require_conversation(conversation_id, user_id)

        msg_id = message_id or self._new_message_id()
        content_json = json.dumps(content, ensure_ascii=False)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages (id, conversation_id, role, content_json)
                VALUES (?, ?, ?, ?)
                """,
                (msg_id, conversation_id, role, content_json),
            )
            # touch conversation timestamp explicitly
            cursor.execute(
                "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (conversation_id,),
            )
            conn.commit()

        return msg_id

    def get_recent_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 8
    ) -> List[Dict[str, Any]]:
        self.require_conversation(conversation_id, user_id)

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, role, content_json, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (conversation_id, limit),
            )
            rows = cursor.fetchall()

        # Reverse to chronological order
        rows = list(reversed(rows))

        results = []
        for row in rows:
            try:
                content = json.loads(row["content_json"])
            except Exception:
                content = {"raw_text": row["content_json"]}

            results.append({
                "id": row["id"],
                "role": row["role"],
                "content": content,
                "created_at": row["created_at"],
            })
        return results

    def list_conversations(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM conversations
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
