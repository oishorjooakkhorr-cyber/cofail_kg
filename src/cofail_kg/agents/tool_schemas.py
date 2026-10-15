"""T1 tool definitions for Ollama chat (protocol §10), wording B approved 2026-10-15.

Envelope: https://docs.ollama.com/capabilities/tool-calling
The source file's exact bytes are the `tools` identity under protocol §3.4.
"""

TOOL_VERSION = "T1"

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_entity",
            "description": (
                "Return an entity’s ID, name, and type, followed by relation summaries ordered "
                "alphabetically by label. Each summary includes display labels, neighbor types, "
                "and a unique neighbor count."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Canonical entity ID."},
                },
                "required": ["entity_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_neighbors",
            "description": (
                "Return unique neighbors for the specified entity and relation label in "
                "ascending numeric ID order, optionally filtered by neighbor type. Each item "
                "includes ID, name, type, and display labels. Return total_count, page, "
                "page_size, and has_more."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "Canonical entity ID."},
                    "relation": {"type": "string", "description": "Relation label."},
                    "neighbor_type": {
                        "type": "string",
                        "description": "Optional neighbor node type; omit to include all types.",
                    },
                    "page": {
                        "type": "integer", "minimum": 1, "default": 1,
                        "description": "Page number, starting at 1. Defaults to 1.",
                    },
                },
                "required": ["entity_id", "relation"],
            },
        },
    },
]
