import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from assistant_actions import execute_action
from database import (
    get_all_preferences,
    get_preference,
    initialize_database,
    set_preference,
)


class AssistantActionTests(unittest.TestCase):
    def test_remember_fact_validates_and_saves_memory(self):
        with patch("assistant_actions.save_memory") as save_memory:
            result = execute_action(
                "remember_fact",
                json.dumps({
                    "fact": "I prefer concise explanations.",
                    "category": "preference",
                }),
                conversation_id=1,
            )

        self.assertTrue(result["ok"])
        save_memory.assert_called_once_with(
            "I prefer concise explanations.",
            "preference",
        )

    def test_search_memories_returns_only_serializable_fields(self):
        with patch(
            "assistant_actions.search_memories",
            return_value=[{
                "id": 7,
                "category": "project",
                "fact": "Building a personal AI.",
                "created_at": "ignored",
            }],
        ):
            result = execute_action(
                "search_memories",
                {"query": "personal AI"},
                conversation_id=1,
            )

        self.assertEqual(
            result,
            {
                "ok": True,
                "memories": [{
                    "id": 7,
                    "category": "project",
                    "fact": "Building a personal AI.",
                }],
            },
        )

    def test_web_search_validates_and_returns_results(self):
        results = [{
            "title": "A source",
            "url": "https://example.com",
            "snippet": "A short summary.",
        }]
        with patch(
            "assistant_actions.web_search",
            return_value=results,
        ) as search:
            result = execute_action(
                "web_search",
                {"query": "current information"},
                conversation_id=1,
            )

        self.assertEqual(result, {"ok": True, "results": results})
        search.assert_called_once_with("current information")

        invalid = execute_action(
            "web_search",
            {"query": " "},
            conversation_id=1,
        )
        self.assertFalse(invalid["ok"])

    def test_rename_current_conversation_updates_active_chat(self):
        with patch("assistant_actions.update_conversation_title") as rename:
            result = execute_action(
                "rename_current_conversation",
                {"title": "Project planning"},
                conversation_id=12,
            )

        self.assertTrue(result["ok"])
        rename.assert_called_once_with(12, "Project planning")

    def test_rejects_invalid_or_unknown_actions(self):
        invalid_memory = execute_action(
            "remember_fact",
            {"fact": "x" * 501, "category": "general"},
            conversation_id=1,
        )
        invalid_category = execute_action(
            "remember_fact",
            {"fact": "A valid fact.", "category": []},
            conversation_id=1,
        )
        malformed = execute_action(
            "remember_fact",
            "{",
            conversation_id=1,
        )
        unknown = execute_action(
            "run_shell_command",
            {},
            conversation_id=1,
        )

        self.assertFalse(invalid_memory["ok"])
        self.assertFalse(invalid_category["ok"])
        self.assertFalse(malformed["ok"])
        self.assertFalse(unknown["ok"])

    def test_preferences_persist_in_database(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "personal_ai.db"
            with patch("database.DB_PATH", database_path):
                initialize_database()
                self.assertEqual(
                    get_preference("assistant_role", "default"),
                    "default",
                )
                set_preference("assistant_role", "Coding partner")

                self.assertEqual(
                    get_preference("assistant_role"),
                    "Coding partner",
                )
                self.assertEqual(
                    get_all_preferences(),
                    {"assistant_role": "Coding partner"},
                )


if __name__ == "__main__":
    unittest.main()
