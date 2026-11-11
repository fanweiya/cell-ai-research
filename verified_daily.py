from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote

if sys.platform != "win32":
    import fcntl
else:
    import msvcrt

PROJECT = Path(os.environ.get("CELL_AI_PROJECT", str(Path(__file__).resolve().parent)))
DB_PATH = PROJECT / "papers.json"
EVIDENCE_DIR = Path(os.environ.get("CELL_AI_EVIDENCE_DIR", str(PROJECT / "evidence")))
LOCK_PATH = EVIDENCE_DIR / ".daily.lock"
sys.path.insert(0, str(PROJECT))
from gread_remote import collect_repository
from daily_site_update import update_site, mark_site_pending
ARXIV_QUERY = (
    "(cat:cs.CV OR cat:cs.AI OR cat:q-bio.QM OR cat:eess.IV) AND "
    "(all:cell OR all:microscopy OR all:histopathology OR all:cytology OR "
    "all:spatial transcriptomics)"
)
ARXIV_API = (
    "https://export.arxiv.org/api/query?search_query="
    + quote(ARXIV_QUERY, safe=":()")
    + "&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending"
)
ARXIV_RSS = "https://rss.arxiv.org/rss/cs.CV+cs.AI+q-bio.QM+eess.IV"
ID_RE = re.compile(r"^(\d{4}\.\d{4,5})(v\d+)?$")
GITHUB_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", re.I
)
GITHUB_PAGES_RE = re.compile(
    r"https?://([A-Za-z0-9_.-]+)\.github\.io/([A-Za-z0-9_.-]+)", re.I
)
OFFICIAL_CODE_CONTEXT_RE = re.compile(
    r"(?:"
    r"(?:source\s+)?codes?(?:\s*(?:and|/)\s*[a-z0-9 _-]+)?\s+"
    r"(?:is|are|will\s+be|can\s+be|has\s+been)?\s*"
    r"(?:publicly\s+)?(?:available|released|provided|accessible|hosted|found)"
    r"|(?:our|the)\s+(?:official\s+)?(?:implementation|codebase|repository)\s+"
    r"(?:is|are|will\s+be|can\s+be)?\s*(?:publicly\s+)?(?:available|released|provided|hosted)"
    r"|implementation\s+(?:is|are|will\s+be|can\s+be)?\s*"
    r"(?:publicly\s+)?(?:available|released|provided|hosted)"
    r"|(?:algorithm|software|framework|pipeline|tool|model)\s+"
    r"(?:is|are)\s+(?:publicly\s+)?open[- ]source"
    r"|(?:github\s+)?link\s+to\s+(?:the\s+)?(?:source\s+)?code(?:/repository)?"
    r"|github\s+(?:link|repository)\s+(?:to|for)\s+(?:the\s+)?(?:code|implementation)"
    r"|implemented\s+as\s+part\s+of.{0,80}\bcode\s*base"
    r"|codes?\s*:"
    r")",
    re.I,
)
IGNORED_GITHUB_REPOSITORIES = {
    ("arxiv", "html_feedback"),
    ("arxiv", "arxiv"),
    # 论文页面里常见的第三方工具/构建依赖引用，并非论文自己的代码仓库。
    ("brucemiller", "latexml"),
    ("latexml", "latexml"),
}
POSITIVE = (
    "cell segmentation", "cell detection", "cell counting", "cell tracking",
    "microscopy", "microscopic", "histopathology", "cytology", "pathology image",
    "whole slide image", "nuclei segmentation", "nucleus segmentation",
    "spatial transcriptomics", "single-cell imaging", "biomedical image",
    "cell image", "tissue image", "organoid imaging",
    "medical image segmentation", "medical imaging", "computational pathology",
    "digital pathology", "gland segmentation",
)
NEGATIVE = (
    "cellular network", "wireless network", "base station", "solar cell",
    "fuel cell", "battery cell", "electrochemical cell", "cell-free massive mimo",
)


def run(command: list[str], timeout: int = 90) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, timeout=timeout)


EVIDENCE_KEEP = 30


def prune_evidence_snapshots() -> None:
    """运行证据快照按时间保留最近 EVIDENCE_KEEP 份，防止工作区无限增长。"""
    if not EVIDENCE_DIR.is_dir():
        return
    for prefix in ("papers-before-", "run-"):
        snapshots = sorted(
            (p for p in EVIDENCE_DIR.glob(f"{prefix}*.json") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
        )
        for stale in snapshots[:-EVIDENCE_KEEP]:
            try:
                stale.unlink()
            except OSError:
                pass


def index_build_command(python_executable: str) -> list[str]:
    """Build the public index and incrementally fill all page-facing caches."""
    return [
        python_executable,
        str(PROJECT / "generate_index.py"),
    ]


def fetch_candidates(url: str) -> list[str]:
    """Return equivalent arXiv API endpoints without changing non-API URLs."""
    if url.startswith("https://export.arxiv.org/api/query?"):
        return [url, url.replace("https://export.arxiv.org", "https://arxiv.org", 1)]
    return [url]


def fetch(url: str, timeout: int = 45) -> str:
    errors: list[str] = []
    for candidate in fetch_candidates(url):
        try:
            result = run(
                ["curl", "--fail", "--silent", "--show-error", "--location",
                 "--retry", "2", "--retry-delay", "3", "--retry-max-time", "15",
                 "--retry-all-errors",
                 "--max-time", str(timeout), "--user-agent", "cell-ai-research/1.0", candidate],
                timeout=timeout + 10,
            )
        except (subprocess.TimeoutExpired, TimeoutError) as exc:
            errors.append(f"{candidate}: {type(exc).__name__}")
            continue
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        detail = clean_text(result.stderr) or f"curl exit {result.returncode}"
        errors.append(f"{candidate}: {detail[:300]}")
    raise RuntimeError("all fetch candidates failed: " + " | ".join(errors))


def clean_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def _repository_matches_title(repo: str, paper_title: str) -> bool:
    def normalized(value: str) -> str:
        value = re.sub(r"\++", " plus ", value.lower())
        return re.sub(r"[^a-z0-9]+", "", value)

    repo_key = normalized(repo)
    title_key = normalized(paper_title)
    if len(repo_key) >= 5 and len(title_key) >= 5 and (repo_key in title_key or title_key in repo_key):
        return True
    title_head = re.split(r"[:,;]", paper_title, maxsplit=1)[0]
    words = re.findall(r"[A-Za-z0-9]+", title_head)
    acronym = "".join(word[0] for word in words if word).lower()
    return len(repo_key) >= 4 and len(acronym) >= 4 and repo_key == acronym


def official_github_candidates(body: str, paper_title: str = "") -> list[dict]:
    """Return only repositories explicitly presented as this paper's code.

    Papers routinely link datasets, pretrained denoisers, baselines and cited
    libraries.  Reachability proves that a repository exists; it does not prove
    that it implements the paper.  We therefore fail closed unless the nearby
    paper text contains an explicit code/implementation availability statement.
    """
    decoded = html.unescape(body or "")
    # PDF-to-text and some arXiv HTML conversions insert whitespace directly
    # after the GitHub host slash ("github.com/ owner/repo").
    decoded = re.sub(r"(https?://github\.com/)\s+", r"\1", decoded, flags=re.I)
    candidates: list[dict] = []
    seen: set[str] = set()
    for match in GITHUB_RE.finditer(decoded):
        owner, repo = match.group(1), match.group(2).removesuffix(".git").rstrip(".,;:'\")]>}")
        if (owner.lower(), repo.lower()) in IGNORED_GITHUB_REPOSITORIES:
            continue
        url = f"https://github.com/{owner}/{repo}"
        if url.lower() in seen:
            continue
        seen.add(url.lower())

        # Check if match is inside a bibliography entry (ltx_bibitem)
        last_bib = decoded[:match.start()].lower().rfind("ltx_bibitem")
        if last_bib != -1:
            last_close = decoded[last_bib:match.start()].lower().rfind("</li")
            if last_close == -1:
                continue

        raw_context = decoded[max(0, match.start() - 420):min(len(decoded), match.end() + 120)]
        context = clean_text(re.sub(r"<[^>]+>", " ", raw_context))
        explicit_statement = bool(OFFICIAL_CODE_CONTEXT_RE.search(context))
        title_match = _repository_matches_title(repo, paper_title)
        if not explicit_statement and not title_match:
            continue
        candidates.append({
            "url": url,
            "provenance": "paper_code_statement",
            "context": context[-500:],
            "relation_signal": "explicit_code_statement" if explicit_statement else "paper_title_match",
        })
    for match in GITHUB_PAGES_RE.finditer(decoded):
        owner = match.group(1)
        repo = match.group(2).removesuffix(".git").rstrip(".,;:'\")]>}")
        if (owner.lower(), repo.lower()) in IGNORED_GITHUB_REPOSITORIES:
            continue
        url = f"https://github.com/{owner}/{repo}"
        if url.lower() in seen or not _repository_matches_title(repo, paper_title):
            continue

        # Check if Pages link is inside bibliography
        last_bib = decoded[:match.start()].lower().rfind("ltx_bibitem")
        if last_bib != -1 and decoded[last_bib:match.start()].lower().rfind("</li") == -1:
            continue

        raw_context = decoded[max(0, match.start() - 260):min(len(decoded), match.end() + 80)]
        context = clean_text(re.sub(r"<[^>]+>", " ", raw_context))
        if "project page" not in context.lower() and "code" not in context.lower():
            continue
        seen.add(url.lower())
        candidates.append({
            "url": url,
            "provenance": "paper_code_statement",
            "context": context[-500:],
            "relation_signal": "paper_project_page",
        })
    return candidates


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def parse_feed(xml_text: str) -> list[dict]:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_text)
    entries: list[dict] = []
    for node in root.findall("a:entry", ns):
        raw_id = clean_text(node.findtext("a:id", default="", namespaces=ns)).rstrip("/").split("/")[-1]
        match = ID_RE.fullmatch(raw_id)
        if not match:
            continue
        categories = [item.attrib.get("term", "") for item in node.findall("a:category", ns)]
        entries.append({
            "arxiv_id": raw_id,
            "base_id": match.group(1),
            "title": clean_text(node.findtext("a:title", default="", namespaces=ns)),
            "abstract": clean_text(node.findtext("a:summary", default="", namespaces=ns)),
            "published": clean_text(node.findtext("a:published", default="", namespaces=ns)),
            "updated": clean_text(node.findtext("a:updated", default="", namespaces=ns)),
            "authors": [clean_text(a.findtext("a:name", default="", namespaces=ns)) for a in node.findall("a:author", ns)],
            "categories": [c for c in categories if c],
        })
    return entries


def parse_rss(xml_text: str) -> list[dict]:
    """Parse the official arXiv RSS feed into the Atom-compatible entry shape."""
    root = ET.fromstring(xml_text)
    dc = {"dc": "http://purl.org/dc/elements/1.1/"}
    entries: list[dict] = []
    for node in root.findall("./channel/item"):
        link = clean_text(node.findtext("link", default="")).rstrip("/")
        raw_id = link.split("/")[-1]
        match = ID_RE.fullmatch(raw_id)
        if not match:
            continue
        raw_description = html.unescape(node.findtext("description", default=""))
        description = clean_text(re.sub(r"<[^>]+>", " ", raw_description))
        description = re.sub(r"^arXiv:\S+\s+(?:Announce Type:\s*\S+\s+)?Abstract:\s*", "", description, flags=re.I)
        raw_date = clean_text(node.findtext("pubDate", default=""))
        try:
            published = parsedate_to_datetime(raw_date).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        except (TypeError, ValueError):
            continue
        creator = clean_text(node.findtext("dc:creator", default="", namespaces=dc))
        entries.append({
            "arxiv_id": raw_id,
            "base_id": match.group(1),
            "title": clean_text(node.findtext("title", default="")),
            "abstract": description,
            "published": published,
            "updated": published,
            "authors": [name.strip() for name in creator.split(",") if name.strip()],
            "categories": [clean_text(item.text) for item in node.findall("category") if clean_text(item.text)],
            "source_url": link,
        })
    return entries


def fetch_recent_entries(evidence: dict) -> list[dict]:
    """Prefer the query API, falling back to the official daily RSS channel."""
    try:
        entries = parse_feed(fetch(ARXIV_API, timeout=60))
        evidence["source_mode"] = "atom_api"
        return entries
    except Exception as exc:
        evidence["source_warnings"].append(f"Atom API unavailable: {type(exc).__name__}: {str(exc)[:300]}")
    entries = parse_rss(fetch(ARXIV_RSS, timeout=45))
    evidence["source_mode"] = "official_rss_fallback"
    return entries


def relevant(entry: dict) -> tuple[bool, str]:
    text = f"{entry['title']} {entry['abstract']}".lower()
    if any(term in text for term in NEGATIVE):
        return False, "negative-domain keyword"
    if any(term in text for term in POSITIVE):
        return True, "matched cell-imaging keyword"
    return False, "no cell-imaging keyword"


def task_types(entry: dict) -> list[str]:
    text = f"{entry['title']} {entry['abstract']}".lower()
    mapping = {
        "segmentation": ("segment", "mask"),
        "detection": ("detect", "localiz"),
        "tracking": ("track",),
        "classification": ("classif", "phenotyp"),
        "reconstruction": ("reconstruct", "super-resolution", "restoration"),
        "histopathology": ("histopath", "whole slide", "pathology"),
        "spatial_transcriptomics": ("spatial transcript",),
    }
    found = [name for name, words in mapping.items() if any(word in text for word in words)]
    return found or ["cell_imaging"]


def discover_github_from_paper(
    arxiv_id: str,
    evidence: dict,
    paper_title: str = "",
    paper_abstract: str = "",
) -> dict:
    """Resolve paper-repository provenance without touching the repository."""
    clean_id = re.sub(r"v\d+$", "", arxiv_id)
    if not ID_RE.fullmatch(clean_id) and not ID_RE.fullmatch(arxiv_id):
        raise ValueError(f"Unsafe or invalid arXiv identifier: {arxiv_id}")

    pages = [f"https://arxiv.org/html/{arxiv_id}", f"https://arxiv.org/abs/{arxiv_id}"]
    body = ""
    source_url = ""
    for page in pages:
        try:
            candidate = fetch(page)
            if candidate and "No HTML for" not in candidate:
                body = candidate
                source_url = page
                break
        except Exception as exc:
            evidence["page_errors"].append({"arxiv_id": arxiv_id, "url": page, "error": str(exc)[:300]})
    if not body:
        context_dir = (PROJECT / "data" / "paper_context").resolve()
        context_path = (context_dir / f"{clean_id}.txt").resolve()
        if not context_path.is_relative_to(context_dir):
            raise ValueError(f"Directory traversal detected in paper context path: {arxiv_id}")
        try:
            body = context_path.read_text(encoding="utf-8")
            source_url = str(context_path)
        except OSError:
            body = ""
    if not body:
        return {
            "status": "error",
            "has_code": False,
            "url": "",
            "analysis_source": "gread",
            "provenance_status": "source_unavailable",
            "stars": 0,
            "framework": "",
            "commit_hash": "",
        }
    # LaTeXML can degrade a real \href into plain ``here`` text (or an
    # ``ltx_ref_self`` span) in the arXiv HTML.  The verified Atom/RSS abstract
    # often still carries the canonical URL, so scan both representations.
    # The same explicit-code-statement filter continues to reject unrelated
    # dependency and bibliography links.
    discovery_text = "\n".join(part for part in (body, paper_abstract) if part)
    candidates = official_github_candidates(discovery_text, paper_title=paper_title)
    if candidates:
        candidate = candidates[0]
        return {
            "status": "done",
            "has_code": False,
            "url": candidate["url"],
            "analysis_source": "gread",
            "provenance": candidate["provenance"],
            "provenance_status": "verified",
            "provenance_context": candidate["context"],
            "relation_signal": candidate["relation_signal"],
            "provenance_source": source_url,
            "stars": 0,
            "framework": "",
            "commit_hash": "",
        }
    return {
        "status": "done",
        "has_code": False,
        "url": "",
        "analysis_source": "gread",
        "provenance_status": "no_paper_code_statement",
        "stars": 0,
        "framework": "",
        "commit_hash": "",
    }


def verify_github_from_paper(
    arxiv_id: str,
    evidence: dict,
    paper_title: str = "",
    paper_abstract: str = "",
) -> dict:
    discovered = discover_github_from_paper(
        arxiv_id,
        evidence,
        paper_title=paper_title,
        paper_abstract=paper_abstract,
    )
    url = discovered.get("url")
    if not url:
        return discovered
    try:
        result = run(["git", "ls-remote", "--exit-code", url, "HEAD"], timeout=35)
        valid = result.returncode == 0 and bool(result.stdout.strip())
        error = "" if valid else clean_text(result.stderr)[:300]
    except Exception as exc:
        valid, error = False, str(exc)[:300]
    evidence["github_checks"].append({
        "url": url,
        "source": discovered.get("provenance_source", ""),
        "valid": valid,
        "error": error,
        "provenance": discovered.get("provenance"),
        "context": discovered.get("provenance_context", ""),
    })
    if valid:
        discovered["has_code"] = True
        return discovered
    discovered.update({
        "status": "done",
        "has_code": False,
        "url": "",
        "provenance_status": "repository_unavailable",
    })
    return discovered


def revalidate_unprovenanced_repositories(database: list[dict], evidence: dict) -> int:
    """Migrate legacy first-link records to evidence-backed repository links."""
    repaired = 0
    for paper in database:
        status = paper.get("status")
        if not isinstance(status, dict):
            continue
        old = status.get("github")
        if not isinstance(old, dict) or not old.get("url"):
            continue
        if old.get("provenance") in {"paper_code_statement", "paper_identity_match", "manual_verified"}:
            continue
        arxiv_id = str(paper.get("arxiv_id") or "").strip()
        clean_id = re.sub(r"v\d+$", "", arxiv_id)
        if not ID_RE.fullmatch(clean_id) and not ID_RE.fullmatch(arxiv_id):
            evidence.setdefault("page_errors", []).append({
                "arxiv_id": arxiv_id,
                "url": str(old.get("url") or ""),
                "error": f"Invalid or non-arXiv identifier: {arxiv_id!r}",
            })
            continue
        try:
            fresh = discover_github_from_paper(
                arxiv_id,
                evidence,
                paper_title=str(paper.get("title") or ""),
                paper_abstract=str(paper.get("abstract") or paper.get("abstract_summary") or ""),
            )
        except ValueError as exc:
            evidence.setdefault("page_errors", []).append({
                "arxiv_id": arxiv_id,
                "url": str(old.get("url") or ""),
                "error": str(exc),
            })
            continue
        if fresh.get("provenance_status") == "source_unavailable":
            continue

        old_url = str(old.get("url") or "").lower().rstrip("/")
        fresh_url = str(fresh.get("url") or "").lower().rstrip("/")
        if old_url and old_url == fresh_url:
            # Preserve the gread-derived implementation verdict; page
            # provenance and repository implementation are separate facts.
            for key in ("provenance", "provenance_status", "provenance_context", "relation_signal"):
                old[key] = fresh.get(key)
            repaired += 1
            continue

        old_match = GITHUB_RE.fullmatch(str(old.get("url") or "").rstrip("/"))
        paper_title = str(paper.get("title") or "").strip()
        if not fresh_url and old_match and paper_title and _repository_matches_title(old_match.group(2), paper_title):
            old["provenance"] = "paper_identity_match"
            old["provenance_status"] = "verified"
            old["relation_signal"] = "paper_identity_match"
            repaired += 1
            continue

        if fresh_url:
            # Link repair must stay atomic and lightweight.  A changed
            # repository is queued for a later gread pass instead of making a
            # full remote source collection part of this migration transaction.
            fresh["repository_found"] = True
            fresh["repository_kind"] = "unknown"
            fresh["has_code"] = False
            status["github"] = fresh
            status["code_analysis"] = "pending"
            paper["has_code"] = False
            paper["code_analysis"] = {}
            paper["error_reason"] = None
            repaired += 1
            continue

        status["github"] = fresh
        status["code_analysis"] = "skipped"
        paper["has_code"] = False
        paper["code_analysis"] = {}
        if str(paper.get("error_reason") or "").startswith("gread remote analysis failed"):
            paper["error_reason"] = None
        repaired += 1
    return repaired


def sanitize_ignored_repositories(database: list[dict]) -> int:
    """Remove generic arXiv site repositories previously mistaken for paper code."""
    repaired = 0
    for paper in database:
        status = paper.get("status")
        if not isinstance(status, dict):
            continue
        github = status.get("github")
        if not isinstance(github, dict):
            continue
        match = GITHUB_RE.match(str(github.get("url") or ""))
        if not match or (match.group(1).lower(), match.group(2).lower()) not in IGNORED_GITHUB_REPOSITORIES:
            continue
        status["github"] = {
            "status": "done",
            "has_code": False,
            "url": "",
            "analysis_source": "gread",
            "stars": 0,
            "framework": "",
            "commit_hash": "",
        }
        status["code_analysis"] = "skipped"
        paper["has_code"] = False
        paper["code_analysis"] = {}
        if str(paper.get("error_reason") or "").startswith("gread remote analysis failed"):
            paper["error_reason"] = None
        repaired += 1
    return repaired


def remote_code_analysis(github: dict, arxiv_id: str, evidence: dict) -> tuple[dict | None, str | None]:
    if not github.get("has_code") or not github.get("url"):
        return None, None
    clean_id = re.sub(r"v\d+$", "", arxiv_id)
    if not ID_RE.fullmatch(clean_id) and not ID_RE.fullmatch(arxiv_id):
        raise ValueError(f"Unsafe or invalid arXiv identifier: {arxiv_id}")
    results_dir = (PROJECT / "results").resolve()
    output_path = (results_dir / f"{arxiv_id}_gread.json").resolve()
    if not output_path.is_relative_to(results_dir):
        raise ValueError(f"Directory traversal detected in gread results path: {arxiv_id}")
    try:
        data = collect_repository(github["url"])
        atomic_json(output_path, data)
        evidence["gread_analyses"].append({
            "arxiv_id": arxiv_id,
            "repository": data.get("repository"),
            "output": str(output_path),
            "status": "done",
        })
        return {
            "status": "done",
            "source": "gread",
            "analysis_depth": data.get("analysis_depth", "multi_pass_static"),
            "repository": data.get("repository", ""),
            "repository_url": data.get("repository_url", github["url"]),
            "analyzed_at": data.get("collected_at"),
            "architecture": data.get("overview", "")[:6000],
            "project_structure": data.get("tree", "")[:12000],
            "key_files": data.get("key_files", []),
            "source_coverage": data.get("coverage", {}),
            "has_implementation": bool(data.get("coverage", {}).get("has_implementation")),
            "repository_kind": data.get("coverage", {}).get("repository_kind", "unknown"),
            "result_file": str(output_path.relative_to(PROJECT)),
        }, None
    except Exception as exc:
        error = f"gread remote analysis failed: {str(exc)[:500]}"
        evidence["gread_analyses"].append({
            "arxiv_id": arxiv_id,
            "repository_url": github.get("url"),
            "status": "error",
            "error": error,
        })
        return None, error


def make_record(entry: dict, github: dict, now: datetime, code_analysis: dict | None, code_error: str | None) -> dict:
    github = dict(github)
    if code_analysis:
        github["repository_found"] = True
        github["repository_kind"] = code_analysis.get("repository_kind", "unknown")
        # A valid GitHub URL with only README/metadata is not published code.
        github["has_code"] = bool(code_analysis.get("has_implementation"))
    code_status = (
        "done" if code_analysis and github.get("has_code")
        else "error" if code_error
        else "skipped"
    )
    return {
        "arxiv_id": entry["arxiv_id"],
        "title": entry["title"],
        "published_date": parse_date(entry["published"]).date().isoformat(),
        "authors": entry["authors"],
        "categories": entry["categories"],
        "task_type": task_types(entry),
        "relevance": "passed",
        "research_score": None,
        "engineering_score": None,
        "priority": None,
        "bonus": [],
        "status": {
            "discovery": "done",
            "relevance_analysis": "done",
            "github": github,
            "task_analysis": "pending",
            "code_analysis": code_status,
            "algorithm_analysis": "pending",
            "critic_analysis": "pending",
            "reproduction": {"level": "not_started", "blocker": None, "estimated_effort_days": None, "hardware": "", "started_at": None, "elapsed_seconds": None},
            "github_search": "done",
            "html": "done",
        },
        "abstract_summary": entry["abstract"],
        "has_code": bool(github.get("has_code")),
        "code_analysis": code_analysis or {},
        "discovered_at": now.isoformat().replace("+00:00", "Z"),
        "analyzed_at": None,
        "error_reason": code_error,
        "provenance": {
            "source": entry.get("source_url") or f"https://export.arxiv.org/api/query?id_list={entry['base_id']}",
            "verified_at": now.isoformat().replace("+00:00", "Z"),
            "verification": "arxiv_atom_exact_id_and_title",
        },
    }


def atomic_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def render_report(evidence: dict, added: list[dict]) -> str:
    repaired = evidence.get("sanitized_github_links", 0)
    degraded_empty_source = bool(
        evidence.get("source_mode") == "official_rss_fallback"
        and evidence.get("fetched", 0) == 0
        and evidence.get("source_warnings")
    )
    if not added and not repaired and not evidence["errors"] and not degraded_empty_source and not evidence.get("site_updated"):
        return "[SILENT]"
    date = evidence["run_date"]
    if not added:
        lines = [
            f"# Cell AI Research Daily · {date}",
            "- 新增论文：0 篇",
            f"- 修复错误代码链接：{repaired} 条",
            f"- 网页索引：{evidence['index_status']}",
            f"- Cloudflare 发布：{evidence.get('publish_status', '未执行')}",
            f"- 证据文件：{evidence['evidence_path']}",
        ]
        if degraded_empty_source:
            lines.extend([
                "- 数据源降级：Atom API 不可用，官方 RSS 回退返回 0 条",
                "- 待处理：本轮无法确认确实没有新论文，未修改 papers.json 或网页索引",
            ])
        if evidence["errors"]:
            lines.append("- 错误：" + "; ".join(evidence["errors"][:3]))
        return "\n".join(lines)
    lines = [
        f"# Cell AI Research Daily · {date}",
        f"- 新增论文：{len(added)} 篇（均已通过 arXiv 元数据校验）",
        f"- 修复错误代码链接：{repaired} 条",
        f"- gread 远程代码分析：{sum(1 for item in evidence['gread_analyses'] if item['status'] == 'done')} 个仓库",
        f"- 网页索引：{evidence['index_status']}",
        f"- Cloudflare 发布：{evidence.get('publish_status', '未执行')}",
        f"- 证据文件：{evidence['evidence_path']}",
        "",
        "新增论文详情",
    ]
    for index, paper in enumerate(added, 1):
        repo = paper["status"]["github"]["url"] or "未在论文页面发现可验证仓库"
        abstract = paper["abstract_summary"]
        if len(abstract) > 360:
            abstract = abstract[:357].rstrip() + "..."
        lines.extend([
            "",
            f"{index}. arXiv:{paper['arxiv_id']} ({paper['published_date']})",
            f"标题：{paper['title']}",
            f"摘要（arXiv 原文）：{abstract}",
            f"官方代码：{repo}",
        ])
    if evidence["errors"]:
        lines.extend(["", "错误与待处理：" + "; ".join(evidence["errors"][:3])])
    return "\n".join(lines)


def main() -> int:
    now = datetime.now(timezone.utc)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    prune_evidence_snapshots()
    with LOCK_PATH.open("a+", encoding="utf-8") as lock:
        if sys.platform != "win32":
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, OSError):
                print("[SILENT]")
                return 0
        else:
            try:
                lock.seek(0)
                if lock.tell() == 0 and lock.read(1) == "":
                    lock.write(" ")
                    lock.flush()
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                print("[SILENT]")
                return 0

        stamp = now.strftime("%Y%m%dT%H%M%SZ")
        evidence_path = EVIDENCE_DIR / f"run-{stamp}.json"
        evidence = {
            "run_date": now.astimezone().date().isoformat(),
            "started_at": now.isoformat(),
            "query": ARXIV_QUERY,
            "api_url": ARXIV_API,
            "rss_url": ARXIV_RSS,
            "source_mode": "pending",
            "source_warnings": [],
            "window_days": 7,
            "fetched": 0,
            "eligible": [],
            "rejected": [],
            "github_checks": [],
            "gread_analyses": [],
            "page_errors": [],
            "added_ids": [],
            "errors": [],
            "sanitized_github_links": 0,
            "index_status": "未执行",
            "evidence_path": str(evidence_path),
        }
        added: list[dict] = []
        try:
            entries = fetch_recent_entries(evidence)
            evidence["fetched"] = len(entries)
            cutoff = now - timedelta(days=7)
            eligible: list[dict] = []
            for entry in entries:
                try:
                    published = parse_date(entry["published"])
                except Exception:
                    evidence["rejected"].append({"arxiv_id": entry["arxiv_id"], "reason": "invalid published timestamp"})
                    continue
                if published < cutoff or published > now + timedelta(days=1):
                    evidence["rejected"].append({"arxiv_id": entry["arxiv_id"], "reason": "outside 7-day published window"})
                    continue
                accepted, reason = relevant(entry)
                if not accepted:
                    evidence["rejected"].append({"arxiv_id": entry["arxiv_id"], "reason": reason})
                    continue
                eligible.append(entry)
                evidence["eligible"].append(entry["arxiv_id"])

            with DB_PATH.open("r", encoding="utf-8") as handle:
                database_doc = json.load(handle)
            database = database_doc.get("database")
            if not isinstance(database, list):
                raise RuntimeError("papers.json 缺少 database 数组")
            evidence["sanitized_github_links"] = sanitize_ignored_repositories(database)
            evidence["sanitized_github_links"] += revalidate_unprovenanced_repositories(database, evidence)
            existing = {ID_RE.fullmatch(str(item.get("arxiv_id", ""))).group(1) for item in database if ID_RE.fullmatch(str(item.get("arxiv_id", "")))}

            for entry in eligible:
                if entry["base_id"] in existing:
                    continue
                github = verify_github_from_paper(
                    entry["arxiv_id"],
                    evidence,
                    paper_title=entry["title"],
                    paper_abstract=entry["abstract"],
                )
                code_analysis, code_error = remote_code_analysis(github, entry["arxiv_id"], evidence)
                record = make_record(entry, github, now, code_analysis, code_error)
                database.append(record)
                added.append(record)
                existing.add(entry["base_id"])
                evidence["added_ids"].append(entry["arxiv_id"])

            if added or evidence["sanitized_github_links"]:
                backup = EVIDENCE_DIR / f"papers-before-{stamp}.json"
                shutil.copy2(DB_PATH, backup)
                mark_site_pending(EVIDENCE_DIR / ".site-update-pending.json")
                atomic_json(DB_PATH, database_doc)
            # 静默回填：把 results/*.json 里已完成的 task/algorithm/critic 分析
            # 结果合并回 papers.json 状态（不触发 LLM），供索引展示"已完成"。
            before_backfill = hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
            backfill_timeout = False
            backfill = None
            try:
                backfill = run([
                    sys.executable, str(PROJECT / "backfill_analysis.py"),
                    "--silent-only",
                ], timeout=90)
            except subprocess.TimeoutExpired:
                backfill_timeout = True
            finally:
                backfill_changed = before_backfill != hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
                if backfill_changed:
                    mark_site_pending(EVIDENCE_DIR / ".site-update-pending.json")
            if backfill_timeout or backfill is None:
                evidence["errors"].append("backfill_analysis.py: timed out after 90s")
            elif backfill.returncode == 0:
                evidence["analysis_backfilled"] = True
            else:
                evidence["errors"].append("backfill_analysis.py: " + clean_text(backfill.stderr or backfill.stdout)[:500])

            # Jev 增量决策评分
            before_jev = hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
            jev_changed = False
            try:
                jev_res = run([
                    sys.executable, str(PROJECT / "jev_evaluator.py"),
                ], timeout=180)
                if jev_res.returncode == 0:
                    evidence["jev_evaluated"] = True
                else:
                    evidence["errors"].append("jev_evaluator.py: " + clean_text(jev_res.stderr or jev_res.stdout)[:500])
            except subprocess.TimeoutExpired:
                evidence["errors"].append("jev_evaluator.py: timed out after 180s")
            finally:
                jev_changed = before_jev != hashlib.sha256(DB_PATH.read_bytes()).hexdigest()
                if jev_changed:
                    mark_site_pending(EVIDENCE_DIR / ".site-update-pending.json")

            update_site(
                evidence, bool(added or evidence["sanitized_github_links"] or backfill_changed or jev_changed),
                PROJECT, EVIDENCE_DIR / ".site-update-pending.json", run,
                index_build_command(sys.executable),
            )
        except Exception as exc:
            evidence["errors"].append(f"{type(exc).__name__}: {str(exc)[:500]}")
        finally:
            evidence["finished_at"] = datetime.now(timezone.utc).isoformat()
            atomic_json(evidence_path, evidence)

        print(render_report(evidence, added))
        return 1 if evidence["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
