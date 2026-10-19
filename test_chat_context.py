import unittest

from chat_context import infer_adaptive_profile, recent_chat_messages


class RecentChatMessagesTests(unittest.TestCase):
    def test_preserves_system_prompt_and_latest_messages(self):
        system = {"role": "system", "content": "Instructions"}
        messages = [
            system,
            *[
                {"role": "user", "content": f"Message {index}"}
                for index in range(5)
            ],
        ]

        result = recent_chat_messages(messages, max_messages=2)

        self.assertEqual(result, [system, *messages[-2:]])
        self.assertEqual(len(messages), 6)

    def test_keeps_every_message_when_within_limit(self):
        messages = [
            {"role": "system", "content": "Instructions"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        self.assertEqual(recent_chat_messages(messages), messages)

    def test_rejects_non_positive_limit(self):
        with self.assertRaisesRegex(ValueError, "at least 1"):
            recent_chat_messages([], max_messages=0)

    def test_detects_adaptive_preferences_from_recent_user_messages(self):
        messages = [
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "Please be brief and show me examples."},
            {"role": "assistant", "content": "Sure"},
            {"role": "user", "content": "Also, walk me through it step by step."},
        ]

        profile = infer_adaptive_profile(messages)

        self.assertIn("brief", profile.lower())
        self.assertIn("example", profile.lower())
        self.assertIn("structured", profile.lower())


if __name__ == "__main__":
    unittest.main()
