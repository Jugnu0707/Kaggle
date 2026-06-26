"""OpenAPI metadata shared across the API."""

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Service health and connectivity checks.",
    },
    {
        "name": "dashboard",
        "description": "Aggregate metrics for the operations dashboard.",
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
