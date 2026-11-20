"""用 claude 这类会调工具的编码代理，逐篇生成 visual-explainer 图解页。

与 build_explainers.py 的分工：材料包只拼一次，剩下的读技能、clone 仓库、写页面、
跑渲染器、按 ✗ 逐条修都交给代理自己做；页面结构与数字来源仍由 gate_page 与
render.mjs 把关，代理交不出合格页面就记进 manifest 的 failures。
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import shutil
import stat
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import add_paper_figures as F  # noqa: E402
import build_explainers as B  # noqa: E402

ROOT = B.ROOT
PROMPTS = HERE / "prompts"
AGENT_DIR = ROOT / "data" / "explainers" / "agent"
LOG_DIR = ROOT / "logs"
LOCK_PATH = ROOT / "data" / "explainers" / ".agent.lock"
CLAUDE = (
    shutil.which("claude")
    or ("/home/fanweiya/.nvm/versions/node/v24.15.0/bin/claude" if Path("/home/fanweiya/.nvm/versions/node/v24.15.0/bin/claude").exists() else "claude")
)
AGENT_TIMEOUT = 3000
TOOLS = "Bash,Read,Write,Edit,Glob,Grep,WebFetch"


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def remove_dir_force(path: Path) -> None:
    """强制彻底删除目录，包括 Windows 下只读属性的文件。"""
    if not path.exists():
        return
    def on_err(func, p, exc_info):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass
    shutil.rmtree(path, onerror=on_err)


def cleanup_dangling_repos() -> int:
    """清理历史遗留或中断残存的仓库克隆目录。"""
    cleaned = 0
    if not AGENT_DIR.exists():
        return 0
    for repo_path in AGENT_DIR.glob("*/repo"):
        if repo_path.is_dir():
            remove_dir_force(repo_path)
            cleaned += 1
    return cleaned


def write_manifest(pid: str, entry: dict | None, error: str | None) -> None:
    """每次先读盘再写，别的进程刚写进去的条目不会被覆盖掉。"""
    fresh = B.load_json(B.MANIFEST) if B.MANIFEST.exists() else {"entries": {}, "failures": {}}
    fresh.setdefault("entries", {})
    fresh.setdefault("failures", {})
    if entry is not None:
        fresh["entries"][pid] = entry
    if error is not None:
        fresh["failures"][pid] = {"at": now(), "error": error}
    else:
        fresh["failures"].pop(pid, None)
    fresh["updated_at"] = now()
    B.MANIFEST.write_text(json.dumps(fresh, ensure_ascii=False, indent=1), encoding="utf-8")


def acquire_lock():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    handle = LOCK_PATH.open("a+")
    try:
        if sys.platform == "win32":
            import msvcrt
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    return handle


def prepare(pid: str, paper: dict, trans: dict, code_sum: dict, index: dict) -> tuple[Path, str]:
    """把材料摆到工作目录，代理在它自己的目录里干活。"""
    work = AGENT_DIR / pid
    (work / "out").mkdir(parents=True, exist_ok=True)
    pack = B.build_pack(pid, paper, trans, code_sum, index)
    repo = ((paper.get("status") or {}).get("github") or {}).get("url") or ""
    (work / "paper.md").write_text(pack, encoding="utf-8")
    (work / "repo.txt").write_text(repo or "（无公开仓库）", encoding="utf-8")
    prompt = (PROMPTS / "agent.md").read_text(encoding="utf-8").replace("<编号>", pid)
    return work, prompt


def run_agent(work: Path, prompt: str, log_path: Path) -> tuple[int, str]:
    command = [
        CLAUDE,
        "-p",
        "--output-format",
        "text",
        "--permission-mode",
        "bypassPermissions",
        "--dangerously-skip-permissions",
        "--allowedTools",
        TOOLS,
    ]
    deadline = time.time() + AGENT_TIMEOUT
    tail: list[str] = []
    agent_env = dict(os.environ)
    nvm_bin = "/home/fanweiya/.nvm/versions/node/v24.15.0/bin"
    if nvm_bin not in agent_env.get("PATH", ""):
        agent_env["PATH"] = f"{nvm_bin}:{agent_env.get('PATH', '')}"
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=agent_env,
        )
        assert process.stdout is not None
        assert process.stdin is not None
        process.stdin.write(prompt)
        process.stdin.close()
        while True:
            line = process.stdout.readline()
            if line:
                tail.append(line)
                del tail[:-400]
                log.write(line)
                log.flush()
                continue
            if process.poll() is not None:
                break
            if time.time() > deadline:
                process.kill()
                log.write(f"\n超时 {AGENT_TIMEOUT}s，已终止\n")
                return 124, "".join(tail)
    return process.returncode or 0, "".join(tail)


def find_source(work: Path, pid: str) -> Path:
    exact = work / "out" / f"{pid}.src.html"
    if exact.exists():
        return exact
    candidates = sorted(work.rglob("*.src.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    if candidates:
        return candidates[0]
    raise RuntimeError(f"{pid} 代理没有产出 .src.html")


def repair(work: Path, pid: str, problems: list[str]) -> int:
    """只改校验没过的地方，比重写整页便宜得多。"""
    prompt = (
        f"页面 data/explainers/agent/{pid}/out/{pid}.src.html 没过校验，问题如下：\n"
        + "\n".join(f"- {problem}" for problem in problems)
        + "\n\n请直接编辑这个文件，只改这些问题，其余内容与结构保持原样，不要重写整页。"
        "改完用 agent.md 里的渲染命令重新渲染，直到输出不再出现 ✗ 行。"
        f"如果确实改不动，把原因写进 data/explainers/agent/{pid}/notes.md。"
    )
    code, _ = run_agent(work, prompt, LOG_DIR / f"agent-{pid}-fix.log")
    return code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--missing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--upgrade", action="store_true", help="只重做早先流水线生成的旧版页面")
    parser.add_argument("--concurrency", type=int, default=2)
    args = parser.parse_args()

    lock = acquire_lock()
    if lock is None:
        print("另一个代理生成进程正在运行，本次跳过", flush=True)
        return 0

    papers = B.load_json(B.PAPERS)["database"]
    translations = B.load_json(B.TRANSLATIONS)
    code_summaries = B.load_json(B.CODE_SUMMARIES)
    index = B.result_index()
    B.EXPLAINERS.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    manifest = B.load_json(B.MANIFEST) if B.MANIFEST.exists() else {"entries": {}, "failures": {}}
    manifest.setdefault("entries", {})
    manifest.setdefault("failures", {})

    by_id = {p["arxiv_id"]: p for p in papers}
    if args.pid:
        chosen = [by_id[pid] for pid in args.pid if pid in by_id]
        missing = [pid for pid in args.pid if pid not in by_id]
        if missing:
            raise SystemExit(f"papers.json 里没有：{', '.join(missing)}")
    else:
        chosen = [p for p in papers if p.get("relevance") == "passed"]
        chosen.sort(key=lambda p: p.get("published_date", ""), reverse=True)

    if args.upgrade:
        chosen = [
            paper for paper in chosen
            if (B.EXPLAINERS / f"{paper['arxiv_id']}.html").exists()
            and (manifest["entries"].get(paper["arxiv_id"]) or {}).get("generator") != "agent"
        ]
        print(f"旧版页面 {len(chosen)} 篇待重做", flush=True)

    tasks = []
    for paper in chosen:
        pid = paper["arxiv_id"]
        if args.missing and (B.EXPLAINERS / f"{pid}.html").exists() and not args.force:
            continue
        tasks.append(paper)
    if args.limit:
        tasks = tasks[:args.limit]

    cleaned_repos = cleanup_dangling_repos()
    if cleaned_repos:
        print(f"已清理 {cleaned_repos} 个历史遗留的克隆代码仓库", flush=True)

    print(f"待生成 {len(tasks)} 篇，引擎 claude（会调工具）", flush=True)
    failures = 0
    lock_manifest = threading.Lock()
    counter = itertools.count(1)

    def run_one(paper: dict) -> bool:
        nonlocal failures
        pid = paper["arxiv_id"]
        number = next(counter)
        began = time.time()
        print(f"[{number}/{len(tasks)} {time.strftime('%H:%M:%S')}] {pid} {paper.get('title', '')[:40]}", flush=True)
        work = None
        try:
            work, prompt = prepare(pid, paper, translations.get(pid, {}), code_summaries.get(pid, {}), index)
            code, output = run_agent(work, prompt, LOG_DIR / f"agent-{pid}.log")
            if code != 0:
                raise RuntimeError(f"代理退出码 {code}，日志 logs/agent-{pid}.log")
            src_path = find_source(work, pid)
            fixes = 0
            while True:
                source = B.cut_to_document(src_path.read_text(encoding="utf-8"))
                problems = B.gate_page(source, pid, None)
                if not problems:
                    src_path.write_text(source, encoding="utf-8")
                    ok, rendered = B.render(src_path, B.EXPLAINERS / f"{pid}.html")
                    if ok:
                        break
                    problems = [
                        line.strip().lstrip("✗").strip()
                        for line in rendered.splitlines()
                        if line.strip().startswith("✗")
                    ] or [rendered.strip()[-600:]]
                if fixes >= 2:
                    raise RuntimeError("页面结构问题：" + "；".join(problems[:5]))
                fixes += 1
                print(f"    {pid} 修补第 {fixes} 轮：{problems[0][:90]}", flush=True)
                repair(work, pid, problems)
            words = B.cjk_count(source)
            write_manifest(pid, {
                "title_zh": translations.get(pid, {}).get("title_zh", ""),
                "one_line": paper.get("title", "")[:40],
                "structure": "agent",
                "generated_at": now(),
                "model": "claude-code",
                "generator": "agent",
                "cjk": words,
                "repairs": fixes,
                "bytes": (B.EXPLAINERS / f"{pid}.html").stat().st_size,
            }, None)
            try:
                F.insert_for(pid)
            except Exception as figure_error:
                print(f"    {pid} 原文图未插入：{figure_error}", flush=True)
            print(f"    {pid} 完成 {time.time() - began:.0f}s  {words} 字", flush=True)
            return True
        except Exception as error:
            with lock_manifest:
                failures += 1
                write_manifest(pid, None, f"{type(error).__name__}: {error}"[:800])
            print(f"    {pid} 失败：{type(error).__name__}: {error}", file=sys.stderr, flush=True)
            return False
        finally:
            if work:
                remove_dir_force(work / "repo")

    from concurrent.futures import ThreadPoolExecutor

    workers = max(1, args.concurrency)
    if workers == 1:
        for paper in tasks:
            run_one(paper)
    else:
        print(f"并发 {workers} 路", flush=True)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            list(pool.map(run_one, tasks))
    print(f"总计 {len(tasks)} 篇，失败 {failures} 篇", flush=True)
    lock.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
