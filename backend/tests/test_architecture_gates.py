from __future__ import annotations

import ast
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = BACKEND_ROOT / "app"

FORBIDDEN_DOMAIN = {
    "sqlalchemy",
    "fastapi",
    "httpx",
    "playwright",
    "app.infrastructure",
    "app.composition",
    "app.api",
}

FORBIDDEN_APPLICATION = {
    "sqlalchemy",
    "fastapi",
    "httpx",
    "playwright",
    "app.infrastructure",
    "app.api",
}


def _imports_in(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
            found.add(node.module)
            # also record full module path prefixes used in checks
            parts = node.module.split(".")
            for i in range(1, len(parts) + 1):
                found.add(".".join(parts[:i]))
    return found


def _iter_py(dir_path: Path):
    for path in dir_path.rglob("*.py"):
        if path.name == "__init__.py" and path.read_text(encoding="utf-8").strip() == "":
            continue
        yield path


def test_domain_has_no_forbidden_imports():
    for path in _iter_py(APP_ROOT / "domains"):
        imports = _imports_in(path)
        for banned in FORBIDDEN_DOMAIN:
            assert banned not in imports, f"{path} imports {banned}"


def test_application_has_no_forbidden_imports():
    for path in _iter_py(APP_ROOT / "application"):
        imports = _imports_in(path)
        for banned in FORBIDDEN_APPLICATION:
            assert banned not in imports, f"{path} imports {banned}"


def test_no_physical_foreign_key_in_orm_models():
    models = (APP_ROOT / "infrastructure/persistence/models.py").read_text(encoding="utf-8")
    assert "ForeignKey" not in models
    assert "relationship(" not in models
    assert "event_id" not in models


def test_legacy_modules_removed():
    assert not (APP_ROOT / "services").exists()
    assert not (APP_ROOT / "models").exists()
    assert not (APP_ROOT / "schemas").exists()
    assert not (APP_ROOT / "database.py").exists()
    assert not (APP_ROOT / "services" / "event_cluster.py").exists()
