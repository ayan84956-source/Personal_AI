import json

from database import (
    save_memory,
    search_memories,
    update_conversation_title,
)
from web_tools import WebSearchError, web_search


ACTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": (
                "Save a durable, user-provided fact to the user's "
                "editable long-term memory. Use only when asked to remember."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "The concise fact to remember.",
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "preference",
                            "goal",
                            "project",
                            "technical",
                            "general",
                        ],
                    },
                },
                "required": ["fact", "category"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_memories",
            "description": (
                "Search the user's saved memories for context relevant "
                "to the current request."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A short search phrase.",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the public web for current information and return "
                "titles, snippets, and source URLs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A concise web search query.",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rename_current_conversation",
            "description": (
                "Rename the current conversation when the user asks."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "A concise conversation title.",
                    },
                },
                "required": ["title"],
                "additionalProperties": False,
            },
        },
    },
]


def execute_action(name, raw_arguments, conversation_id):
    """Execute one explicitly requested, allowlisted app action."""
    try:
        arguments = (
            json.loads(raw_arguments)
            if isinstance(raw_arguments, str)
            else raw_arguments
        )
    except json.JSONDecodeError:
        return {"ok": False, "error": "Action arguments were not valid JSON."}

    if not isinstance(arguments, dict):
        return {"ok": False, "error": "Action arguments must be an object."}

    if name == "remember_fact":
        fact = arguments.get("fact")
        category = arguments.get("category")
        allowed_categories = {
            "preference", "goal", "project", "technical", "general",
        }
        if not isinstance(fact, str) or not fact.strip() or len(fact) > 500:
            return {
                "ok": False,
                "error": "A memory must be between 1 and 500 characters.",
            }
        if not isinstance(category, str) or category not in allowed_categories:
            return {"ok": False, "error": "Unsupported memory category."}
        save_memory(fact.strip(), category)
        return {"ok": True, "message": "The fact was saved to memory."}

    if name == "search_memories":
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip() or len(query) > 500:
            return {
                "ok": False,
                "error": "A search query must be between 1 and 500 characters.",
            }
        matches = search_memories(query.strip(), limit=8)
        return {
            "ok": True,
            "memories": [
                {
                    "id": memory["id"],
                    "category": memory["category"],
                    "fact": memory["fact"],
                }
                for memory in matches
            ],
        }

    if name == "web_search":
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip() or len(query) > 500:
            return {
                "ok": False,
                "error": "A search query must be between 1 and 500 characters.",
            }
        try:
            results = web_search(query.strip())
        except WebSearchError as error:
            return {"ok": False, "error": str(error)}
        return {"ok": True, "results": results}

    if name == "rename_current_conversation":
        title = arguments.get("title")
        if (
            not isinstance(title, str)
            or not title.strip()
            or len(title.strip()) > 60
        ):
            return {
                "ok": False,
                "error": "A conversation title must be between 1 and 60 characters.",
            }
        if conversation_id is None:
            return {"ok": False, "error": "There is no active conversation."}
        update_conversation_title(conversation_id, title.strip())
        return {"ok": True, "message": "The conversation was renamed."}

    return {"ok": False, "error": "This action is not available."}
