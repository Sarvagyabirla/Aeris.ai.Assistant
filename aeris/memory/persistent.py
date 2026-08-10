import os
import json
from typing import Dict, Any
from aeris.app_logger.logger import log


class PersistentMemory:
    """A lightweight JSON-backed persistent memory store."""

    def __init__(self, filepath: str = "memory.json"):
        self.filepath = filepath
        self._data: Dict[str, Any] = {"facts": [], "summaries": []}
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                log.error(f"Failed to load persistent memory from {self.filepath}: {e}")
        else:
            self._save()

    def _save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save persistent memory to {self.filepath}: {e}")

    def add_fact(self, fact: str):
        if "facts" not in self._data:
            self._data["facts"] = []
        if fact not in self._data["facts"]:
            self._data["facts"].append(fact)
            self._save()

    def add_summary(self, summary: str):
        if "summaries" not in self._data:
            self._data["summaries"] = []
        self._data["summaries"].append(summary)
        self._save()

    def get_context_string(self) -> str:
        """Returns a string representation of the memory for the system prompt."""
        context = []
        facts = self._data.get("facts", [])
        if facts:
            context.append("Known Facts about User/Environment:")
            for fact in facts:
                context.append(f"- {fact}")

        summaries = self._data.get("summaries", [])
        if summaries:
            context.append("\nPast Session Summaries:")
            for summary in summaries[-5:]:  # Only include last 5 to save tokens
                context.append(f"- {summary}")

        return "\n".join(context)
