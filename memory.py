import json
from database import save_memory, search_memories

def extract_and_save_memories(client, model, user_message):
    """Extract useful long-term facts from a user message."""

    instructions = """
You are a memory extraction assistant.

Extract up to 3 useful, durable facts explicitly stated by
the user in the supplied message.

Prioritize:
- Learning goals and interests
- Projects and their technical details
- Long-term preferences
- Development environment and tools

Rules:
- Never invent facts or infer uncertain personal details.
- Do not save passwords, API keys, or other credentials.
- Do not save highly sensitive personal information.
- Ignore requests, questions, temporary tasks, and greetings
  unless they contain a useful durable fact.
- Return only valid JSON in this format:
  {"memories": [{"fact": "...", "category": "..."}]}
- Categories can be: preference, goal, project, technical,
  or general.
- Return an empty memories array if nothing useful is present.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": instructions},
                {
                    "role": "user",
                    "content": json.dumps({
                        "message": user_message
                    }),
                },
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        memories = data.get("memories", [])

        if not isinstance(memories, list):
            return 0

        saved_count = 0

        for item in memories[:3]:
            if not isinstance(item, dict):
                continue

            fact = item.get("fact", "")
            category = item.get("category", "general")

            if not isinstance(fact, str) or not fact.strip():
                continue

            if category not in {
                "preference", "goal", "project",
                "technical", "general",
            }:
                category = "general"

            save_memory(fact, category)
            saved_count += 1

        return saved_count

    except Exception as error:
        raise RuntimeError(f"Memory extraction failed: {error}") from error

def get_relevant_memories(query):
    """Retrieve memories relevant to the current question."""
    return search_memories(query, limit=8)