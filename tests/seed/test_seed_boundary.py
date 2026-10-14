"""AC-2: verify no `aprendiz` or `fastapi` imports under src/sap_mcp or tests/seed."""

import ast
from pathlib import Path


FORBIDDEN = {"aprendiz", "fastapi"}

ROOTS = [
    Path("src/sap_mcp"),
    Path("tests/seed"),
]


def _imports_in(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            # Full dotted import: module.name for relative, "module.sub" for absolute
            for alias in node.names:
                names.append(f"{module}.{alias.name}" if module else alias.name)
    return names


def _python_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.py") if p.name != "__pycache__")


def test_no_aprendiz_or_fastapi_imports():
    violations: list[tuple[Path, str]] = []
    for root in ROOTS:
        for py_file in _python_files(root):
            tree = ast.parse(py_file.read_text(), filename=str(py_file))
            for imp in _imports_in(tree):
                top = imp.split(".")[0]
                if top in FORBIDDEN:
                    violations.append((py_file, imp))
    assert not violations, (
        f"Forbidden imports found:\n"
        + "\n".join(f"  {f}: {i}" for f, i in violations)
    )