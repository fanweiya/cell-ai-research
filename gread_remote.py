#!/usr/bin/env python3
"""Read and inspect GitHub repositories through the public gread HTTP API.

The collector deliberately never clones a repository.  It performs a bounded,
multi-pass static inspection instead: repository overview, deep tree, generic
symbol/risk searches, ranked source selection, and batched source reads.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any
from urllib.parse import urlencode


GREAD_API_URL = "https://api.gread.dev"
GITHUB_RE = re.compile(r"^https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$")

CODE_EXTENSIONS = {
    ".py", ".pyi", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".java",
    ".kt", ".kts", ".scala", ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp",
    ".cu", ".cuh", ".go", ".rs", ".rb", ".php", ".swift", ".m", ".mm",
    ".r", ".jl", ".lua", ".sh", ".bash", ".zsh", ".ps1",
}
TEXT_EXTENSIONS = CODE_EXTENSIONS | {
    ".md", ".rst", ".txt", ".toml", ".yaml", ".yml", ".json", ".ini",
    ".cfg", ".conf", ".xml", ".gradle", ".properties", ".env",
}
MANIFEST_NAMES = {
    "readme", "readme.md", "readme.rst", "pyproject.toml", "requirements.txt",
    "environment.yml", "environment.yaml", "setup.py", "setup.cfg", "package.json",
    "cargo.toml", "go.mod", "pom.xml", "build.gradle", "build.gradle.kts",
    "makefile", "cmakelists.txt", "dockerfile", "compose.yaml", "docker-compose.yml",
    ".env", ".python-version", "license", "license.md", "license.txt",
}
EXCLUDED_PARTS = {
    ".git", ".github", "node_modules", "dist", "build", "vendor", "third_party",
    "__pycache__", ".venv", "venv", "site-packages", "coverage", "checkpoints",
}
SEARCH_QUERIES = (
    r"class |def |function |interface |struct |fn |func ",
    r"main\(|train\(|forward\(|fit\(|predict\(|infer|generate",
    r"TODO|FIXME|NotImplemented|raise |throw ",
    r"pytest|unittest|test_|describe\(|@Test",
    r"import |from |require\(|use |#include",
)
MAX_SELECTED_FILES = 28
MAX_SOURCE_CHARS = 160_000


def repository_name(url: str) -> str:
    match = GITHUB_RE.fullmatch(url.strip())
    if not match:
        raise ValueError(f"Unsupported GitHub URL: {url}")
    return f"{match.group(1)}/{match.group(2)}"


def _get(path: str, params: dict[str, Any], timeout: int = 90) -> str:
    normalized = {
        key: (str(value).lower() if isinstance(value, bool) else value)
        for key, value in params.items()
        if value not in (None, "")
    }
    url = f"{GREAD_API_URL}{path}?{urlencode(normalized)}"
    request = urllib.request.Request(
        url,
        headers={"Accept": "text/markdown, text/plain", "User-Agent": "cell-ai-research/2.0"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace").strip()


def _tree_paths(tree: str) -> set[str]:
    """Extract readable file paths from gread's markdown tree response."""
    paths: set[str] = set()
    in_fence = False
    for raw_line in (tree or "").splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence or not line or line.startswith("## "):
            continue
        path = line.lstrip("./")
        pure = PurePosixPath(path)
        if any(part in EXCLUDED_PARTS for part in pure.parts):
            continue
        suffix = pure.suffix.lower()
        if suffix in TEXT_EXTENSIONS or pure.name.lower() in MANIFEST_NAMES:
            paths.add(path)
    return paths


def _search_paths(searches: list[str]) -> set[str]:
    paths: set[str] = set()
    # gread grep emits HEAD:path/to/file.ext:line:content.
    pattern = re.compile(r"(?:^|\n)(?:HEAD:)?([^:\n]+):\d+(?::|-)" )
    for search in searches:
        for path in pattern.findall(search or ""):
            path = path.strip().lstrip("./")
            pure = PurePosixPath(path)
            if not any(part in EXCLUDED_PARTS for part in pure.parts):
                paths.add(path)
    return paths


def _path_score(path: str, repository: str, search_hits: set[str]) -> tuple[int, int, str]:
    pure = PurePosixPath(path)
    name = pure.name.lower()
    stem = pure.stem.lower().replace("-", "_")
    parts = {part.lower() for part in pure.parts}
    repo_token = repository.rsplit("/", 1)[-1].lower().replace("-", "_")
    score = 0

    if path in search_hits:
        score -= 220
    if name in {"readme", "readme.md", "readme.rst"}:
        score -= 210
    elif name in MANIFEST_NAMES:
        score -= 150
    if stem in {"main", "train", "training", "infer", "inference", "predict", "evaluate", "evaluation", "app", "cli"}:
        score -= 190
    if any(token in stem for token in ("model", "network", "pipeline", "algorithm", "generator", "segment", "forward")):
        score -= 145
    if repo_token and (repo_token in stem or stem in repo_token) and len(stem) >= 4:
        score -= 135
    if parts & {"src", "lib", "models", "model", "core", "modules", "algorithms", "lesion_generator"}:
        score -= 95
    if parts & {"config", "configs"}:
        score -= 70
    if "test" in stem or parts & {"test", "tests"}:
        score -= 65
    if pure.suffix.lower() in CODE_EXTENSIONS:
        score -= 40
    # Prefer shallower, shorter paths only as a tie-breaker.
    return score, len(pure.parts) * 20 + len(path), path


def _candidate_paths(tree: str, searches: list[str], repository: str = "") -> list[str]:
    tree_paths = _tree_paths(tree)
    search_hits = _search_paths(searches)
    candidates = tree_paths | {
        path for path in search_hits
        if PurePosixPath(path).suffix.lower() in TEXT_EXTENSIONS
        or PurePosixPath(path).name.lower() in MANIFEST_NAMES
    }
    ranked = sorted(candidates, key=lambda path: _path_score(path, repository, search_hits))

    selected = ranked[:MAX_SELECTED_FILES]
    # Preserve at least one test and one manifest when they exist; those are
    # important for reproducibility but can otherwise lose to model files.
    for predicate in (
        lambda p: "test" in PurePosixPath(p).stem.lower() or "tests" in PurePosixPath(p).parts,
        lambda p: PurePosixPath(p).name.lower() in MANIFEST_NAMES,
    ):
        extra = next((path for path in ranked if predicate(path) and path not in selected), None)
        if extra and selected:
            selected[-1] = extra
    return sorted(set(selected), key=lambda path: _path_score(path, repository, search_hits))


def _read_paths(name: str, paths: list[str], batch_size: int = 8) -> tuple[str, list[str]]:
    chunks: list[str] = []
    errors: list[str] = []
    used = 0
    for start in range(0, len(paths), batch_size):
        batch = paths[start:start + batch_size]
        try:
            content = _get("/read", {"name": name, "paths": ",".join(batch)})
        except Exception as exc:
            errors.append(f"{','.join(batch)}: {exc}")
            continue
        remaining = MAX_SOURCE_CHARS - used
        if remaining <= 0:
            break
        chunks.append(content[:remaining])
        used += min(len(content), remaining)
    return "\n\n".join(chunk for chunk in chunks if chunk), errors


def _coverage(paths: set[str], selected: list[str], read_errors: list[str]) -> dict[str, Any]:
    code_files = sorted(path for path in paths if PurePosixPath(path).suffix.lower() in CODE_EXTENSIONS)
    selected_code = [path for path in selected if PurePosixPath(path).suffix.lower() in CODE_EXTENSIONS]
    languages = Counter(PurePosixPath(path).suffix.lower().lstrip(".") for path in code_files)
    tests = [path for path in paths if "test" in PurePosixPath(path).stem.lower() or "tests" in PurePosixPath(path).parts]
    manifests = [path for path in paths if PurePosixPath(path).name.lower() in MANIFEST_NAMES]
    has_implementation = bool(code_files)
    return {
        "repository_kind": "implementation" if has_implementation else "placeholder_or_docs_only",
        "has_implementation": has_implementation,
        "code_file_count_in_tree": len(code_files),
        "selected_file_count": len(selected),
        "selected_code_file_count": len(selected_code),
        "languages_by_extension": dict(sorted(languages.items())),
        "tests_present": bool(tests),
        "test_files": tests[:20],
        "manifest_files": manifests[:20],
        "read_errors": read_errors,
        "limitations": [
            "Static remote inspection only; files were not executed.",
            "gread responses describe HEAD and do not prove runtime compatibility or paper-result reproduction.",
        ],
    }


def collect_repository(url: str) -> dict[str, Any]:
    name = repository_name(url)
    overview = _get("/repo", {"name": name})
    tree = _get("/tree", {"name": name, "dir": "", "depth": 8, "limit": 400})
    searches: list[str] = []
    search_errors: list[str] = []
    for query in SEARCH_QUERIES:
        try:
            searches.append(_get("/grep", {
                "name": name,
                "q": query,
                "i": True,
                "E": True,
                "C": 1,
            }))
        except Exception as exc:
            searches.append("")
            search_errors.append(f"{query}: {exc}")

    paths = _candidate_paths(tree, searches, repository=name)
    files, read_errors = _read_paths(name, paths)
    all_paths = _tree_paths(tree) | _search_paths(searches)
    coverage = _coverage(all_paths, paths, read_errors)
    coverage["search_errors"] = search_errors
    return {
        "source": "gread",
        "analysis_depth": "multi_pass_static",
        "repository": name,
        "repository_url": url,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "coverage": coverage,
        "overview": overview[:30_000],
        "tree": tree[:50_000],
        "key_files": paths,
        "source_files": files[:MAX_SOURCE_CHARS],
        "search_queries": list(SEARCH_QUERIES),
        "search_results": [item[:16_000] for item in searches],
    }


def as_analysis_context(data: dict[str, Any]) -> str:
    """Render a source-first, bounded context for an LLM code reviewer."""
    context = {
        "source": data.get("source"),
        "analysis_depth": data.get("analysis_depth"),
        "repository": data.get("repository"),
        "repository_url": data.get("repository_url"),
        "collected_at": data.get("collected_at"),
        "coverage": data.get("coverage", {}),
        "overview": str(data.get("overview", ""))[:12_000],
        "tree": str(data.get("tree", ""))[:25_000],
        "key_files": data.get("key_files", []),
        # Source is intentionally before grep output so a downstream hard
        # context limit cannot silently reduce the review to README metadata.
        "source_files": str(data.get("source_files", ""))[:135_000],
        "search_results": [str(item)[:4_000] for item in data.get("search_results", [])],
    }
    return json.dumps(context, ensure_ascii=False, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a GitHub repository remotely through gread HTTP")
    parser.add_argument("url")
    parser.add_argument("--output")
    args = parser.parse_args()
    data = collect_repository(args.url)
    rendered = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
