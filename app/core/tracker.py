"""Applications the user has prepared, with status + follow-up reminders (SQLite)."""
from __future__ import annotations

import json
import secrets
import sqlite3
import threading
from datetime import date, datetime, timedelta
from pathlib import Path


class Tracker:
    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY, user_id TEXT NOT NULL, form_id TEXT NOT NULL,
                title TEXT NOT NULL, values_json TEXT NOT NULL, status TEXT NOT NULL,
                created_at TEXT NOT NULL, follow_up_on TEXT, next_step TEXT)"""
        )
        self._db.commit()

    def create(self, user_id: str, form: dict, values: dict, next_step: str = "") -> dict:
        app_id = "US-" + datetime.now().strftime("%y%m") + "-" + secrets.token_hex(3).upper()
        created = datetime.now().isoformat(timespec="seconds")
        sla_days = int(form.get("follow_up_days", 15))
        follow = (date.today() + timedelta(days=sla_days)).isoformat()
        title = form["title"]["en"] if isinstance(form["title"], dict) else form["title"]
        with self._lock:
            self._db.execute(
                "INSERT INTO applications VALUES (?,?,?,?,?,?,?,?,?)",
                (app_id, user_id, form["id"], title, json.dumps(values, ensure_ascii=False),
                 "prepared", created, follow, next_step),
            )
            self._db.commit()
        return self.get(app_id)

    def get(self, app_id: str) -> dict | None:
        row = self._db.execute("SELECT * FROM applications WHERE id=?", (app_id,)).fetchone()
        return self._row(row) if row else None

    def list(self, user_id: str) -> list[dict]:
        rows = self._db.execute(
            "SELECT * FROM applications WHERE user_id=? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        return [self._row(r) for r in rows]

    def update_status(self, app_id: str, status: str) -> dict | None:
        with self._lock:
            self._db.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
            self._db.commit()
        return self.get(app_id)

    @staticmethod
    def _row(row: sqlite3.Row) -> dict:
        d = dict(row)
        d["values"] = json.loads(d.pop("values_json"))
        d["overdue"] = bool(d["follow_up_on"]) and d["follow_up_on"] < date.today().isoformat() and d["status"] != "done"
        return d
