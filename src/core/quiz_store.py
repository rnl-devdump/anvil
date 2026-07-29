# src/core/quiz_store.py
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.core.config import QUIZ_HISTORY_PATH


class QuizStore:

    def __init__(self, path: str = QUIZ_HISTORY_PATH):

        self.path = Path(path)

        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._records: list[dict[str, Any]] = []

        self._load()


    def _load(self) -> None:

        if self.path.exists():

            with open(self.path, encoding="utf-8") as f:

                self._records = json.load(f)

        else:

            self._records = []

            self._save()


    def _save(self) -> None:

        with open(self.path, "w", encoding="utf-8") as f:

            json.dump(self._records, f, indent=2, ensure_ascii=False)


    @property
    def all(self) -> list[dict[str, Any]]:

        return list(reversed(self._records))


    def get(self, quiz_id: str) -> dict[str, Any] | None:

        for record in self._records:

            if record["id"] == quiz_id:

                return record

        return None


    def add(
        self,
        title: str,
        source: str,
        questions: list[dict[str, Any]],
    ) -> dict[str, Any]:

        record = {
            "id": uuid.uuid4().hex[:12],
            "title": title,
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "question_count": len(questions),
            "questions": questions,
        }

        self._records.append(record)

        self._save()

        return record


    def delete(self, quiz_id: str) -> bool:

        before = len(self._records)

        self._records = [r for r in self._records if r["id"] != quiz_id]

        if len(self._records) < before:

            self._save()

            return True

        return False
