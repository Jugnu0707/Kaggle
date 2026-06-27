"""OpenAPI metadata shared across the API."""

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Service health and connectivity checks.",
    },
    {
        "name": "ai",
        "description": "Google AI Studio API verification.",
    },
    {
        "name": "agents",
        "description": "Coordinator orchestration and agent workflow endpoints.",
    },
    {
        "name": "evaluation",
        "description": "Agent evaluation metrics and health scores.",
    },
    {
        "name": "dashboard",
        "description": "Aggregate metrics for the operations dashboard.",
    },
    {
        "name": "investigations",
        "description": "End-to-end investigation workflow execution.",
    },
    {
        "name": "incidents",
        "description": "Incident CRUD operations and investigation metadata.",
    },
    {
        "name": "logs",
        "description": "Secure log file upload and metadata management.",
    },
    {
        "name": "system",
        "description": "System introspection and database metadata.",
    },
    {
        "name": "root",
        "description": "Application root endpoints.",
    },
]
