"""Generate repository statistics for README and Kaggle submission."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "backend"

CODE_DIRS = [
    "agents",
    "backend/app",
    "backend/scripts",
    "evaluation",
    "mcp",
    "tests",
    "frontend/src",
    "scripts",
]
CODE_EXTENSIONS = {".py", ".ts", ".tsx"}


def count_openapi_operations() -> dict[str, int]:
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-c",
            (
                "import json; from app.main import app; "
                "p=app.openapi()['paths']; "
                "print(json.dumps({'paths':len(p),'operations':sum(len(m) for m in p.values())}))"
            ),
        ],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [
        line for line in result.stdout.splitlines() if line.strip().startswith("{")
    ]
    return json.loads(lines[-1])


def count_tests() -> int:
    result = subprocess.run(
        ["uv", "run", "pytest", "--collect-only", "-q"],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        check=False,
    )
    for line in result.stdout.splitlines():
        if "tests collected" in line:
            return int(line.split()[0])
    return 0


def count_frontend_pages() -> int:
    pages_dir = REPO_ROOT / "frontend" / "src" / "pages"
    return len(list(pages_dir.glob("*Page.tsx")))


def count_mcp_tools() -> int:
    result = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-c",
            "import mcp.tools; from mcp.registry import get_registry; print(get_registry().tool_count())",
        ],
        cwd=BACKEND,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [
        line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()
    ]
    return int(lines[-1])


def count_agents() -> int:
    agents_dir = REPO_ROOT / "agents"
    return len(
        [p for p in agents_dir.iterdir() if p.is_dir() and (p / "agent.py").exists()]
    )


def count_db_tables() -> int:
    models_dir = REPO_ROOT / "backend" / "app" / "models"
    skip = {"__init__.py", "base.py", "enums.py"}
    return len([p for p in models_dir.glob("*.py") if p.name not in skip])


def count_documentation_files() -> int:
    docs_dir = REPO_ROOT / "docs"
    root_docs = ["README.md", "CHANGELOG.md", "ROADMAP.md", "CONTRIBUTING.md"]
    count = sum(1 for p in root_docs if (REPO_ROOT / p).exists())
    count += len(list(docs_dir.rglob("*.md")))
    return count


def count_lines_of_code() -> int:
    total = 0
    for rel_dir in CODE_DIRS:
        base = REPO_ROOT / rel_dir
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix not in CODE_EXTENSIONS:
                continue
            if any(
                part in path.parts for part in (".venv", "node_modules", "__pycache__")
            ):
                continue
            try:
                total += sum(1 for _ in path.open(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
    return total


def generate_stats() -> dict[str, int]:
    openapi = count_openapi_operations()
    return {
        "api_paths": openapi["paths"],
        "api_operations": openapi["operations"],
        "ai_agents": count_agents(),
        "database_tables": count_db_tables(),
        "frontend_pages": count_frontend_pages(),
        "mcp_tools": count_mcp_tools(),
        "tests": count_tests(),
        "documentation_files": count_documentation_files(),
        "lines_of_code": count_lines_of_code(),
    }


def main() -> None:
    stats = generate_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
