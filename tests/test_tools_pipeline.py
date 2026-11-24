from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import agent_explainers  # noqa: E402  # pyright: ignore[reportMissingImports]
import build_explainers as B  # noqa: E402  # pyright: ignore[reportMissingImports]

PID = "2607.07651v1"


def _valid_page_source(pid: str = PID) -> str:
    """构造一份满足 gate_page 全部结构要求的最小页面源。"""
    body_text = "细胞分割模型通过编码器提取图像特征，再由解码器恢复实例掩码。" * 8
    figures = "".join(
        f"<figure><svg viewBox=\"0 0 100 100\" aria-label=\"图{i}\"></svg>"
        f"<figcaption>图{i}说明</figcaption></figure>"
        for i in range(1, 4)
    )
    return f"""<!doctype html>
<html lang="zh-CN" data-register="paper">
<head><link rel="stylesheet" href="kit.css" data-ve-kit></head>
<body>
<h1>测试图解页</h1>
<p>{body_text}</p>
<section id="problem"><p>{body_text}</p></section>
<section id="mechanism"><p>{body_text}</p>{figures}</section>
<section id="results"><p>{body_text}</p></section>
<section id="limits"><p>{body_text}</p></section>
<section id="remember"><p>{body_text}</p></section>
<section id="design"><p>{body_text}</p></section>
<a href="https://arxiv.org/abs/{pid}">arXiv</a>
<a href="index.html#paper-{pid}">返回索引</a>
</body>
</html>"""


class ResultIndexTests(unittest.TestCase):
    def test_result_index_groups_suffixes_by_pid(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = Path(tmp)
            (results / f"{PID}_task_analysis.json").write_text("{}", encoding="utf-8")
            (results / f"{PID}_gread.json").write_text("{}", encoding="utf-8")
            (results / "2608.00001v2_algorithm_analysis.json").write_text("{}", encoding="utf-8")
            (results / "notes.txt").write_text("ignored", encoding="utf-8")
            with patch.object(B, "RESULTS", results):
                index = B.result_index()
        self.assertEqual(sorted(index), [PID, "2608.00001v2"])
        self.assertEqual(sorted(index[PID]), ["gread", "task_analysis"])
        self.assertEqual(index["2608.00001v2"]["algorithm_analysis"].name,
                         "2608.00001v2_algorithm_analysis.json")

    def test_result_index_missing_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(B, "RESULTS", Path(tmp) / "nope"):
                self.assertEqual(B.result_index(), {})


class GatePageTests(unittest.TestCase):
    def test_valid_page_has_no_problems(self):
        problems = B.gate_page(_valid_page_source(), PID, {})
        self.assertEqual(problems, [])

    def test_empty_source_reports_structure_problems(self):
        problems = B.gate_page("not a page", PID, {})
        self.assertTrue(any("doctype" in p for p in problems))
        self.assertTrue(any("</html>" in p for p in problems))
        self.assertTrue(any("data-ve-kit" in p for p in problems))
        self.assertTrue(any("data-register" in p for p in problems))
        self.assertTrue(any("至少三张图" in p for p in problems))
        self.assertTrue(any("版块" in p for p in problems))
        self.assertTrue(any("h1" in p for p in problems))
        self.assertTrue(any("arXiv" in p for p in problems))
        self.assertTrue(any("返回索引" in p for p in problems))

    def test_script_tag_is_rejected(self):
        source = _valid_page_source().replace("</body>", "<script>alert(1)</script></body>")
        problems = B.gate_page(source, PID, {})
        self.assertIn("页面源不能包含 <script>", problems)

    def test_missing_section_id_is_reported(self):
        source = _valid_page_source().replace('id="limits"', 'id="other"')
        problems = B.gate_page(source, PID, {})
        self.assertIn('缺少版块 id="limits"', problems)


class WriteManifestTests(unittest.TestCase):
    def test_write_manifest_updates_entries_and_failures_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            manifest_path.write_text(json.dumps({
                "entries": {"old_pid": {"generator": "agent"}},
                "failures": {"old_pid": {"at": "t", "error": "old"}},
            }, ensure_ascii=False), encoding="utf-8")
            with patch.object(B, "MANIFEST", manifest_path):
                agent_explainers.write_manifest(PID, {"generator": "agent"}, None)
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertIn(PID, data["entries"])
                self.assertIn("old_pid", data["entries"])
                self.assertNotIn(PID, data["failures"])
                self.assertIn("old_pid", data["failures"])
                self.assertFalse(manifest_path.with_name(manifest_path.name + ".tmp").exists())

                agent_explainers.write_manifest("2608.00001", None, "boom")
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(data["failures"]["2608.00001"]["error"], "boom")
                self.assertIn(PID, data["entries"])

    def test_write_manifest_creates_file_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "manifest.json"
            with patch.object(B, "MANIFEST", manifest_path):
                agent_explainers.write_manifest(PID, {"generator": "agent"}, "first failure")
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertIn(PID, data["entries"])
            self.assertIn(PID, data["failures"])


class PrepareTests(unittest.TestCase):
    def _setup_dirs(self, tmp):
        prompts = Path(tmp) / "prompts"
        prompts.mkdir()
        (prompts / "agent.md").write_text("<编号> {{ROOT}}", encoding="utf-8")
        agent_dir = Path(tmp) / "agent"
        patches = [
            patch.object(agent_explainers, "AGENT_DIR", agent_dir),
            patch.object(agent_explainers, "PROMPTS", prompts),
            patch.object(agent_explainers.B, "build_pack", return_value="pack"),
        ]
        for p in patches:
            p.start()
        self.addCleanup(lambda: [p.stop() for p in patches])
        return agent_dir

    def test_prepare_clean_returns_no_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._setup_dirs(tmp)
            work, prompt, warning = agent_explainers.prepare(PID, {}, {}, {}, {})
            self.assertTrue(prompt.startswith(PID))
            self.assertIsNone(warning)
            self.assertFalse((work / "repo").exists())

    def test_prepare_cleanup_failure_moves_residual_aside(self):
        # 回归 #406：清理失败留下半删残留时，改名移 aside 再 clone，
        # 并把经过返回给调用方写进 manifest，而不是只打印 stderr 就继续。
        with tempfile.TemporaryDirectory() as tmp:
            agent_dir = self._setup_dirs(tmp)
            repo = agent_dir / PID / "repo"
            repo.mkdir(parents=True)
            (repo / "keep.txt").write_text("stale", encoding="utf-8")
            with patch.object(
                agent_explainers, "remove_path_force",
                side_effect=OSError("permission denied"),
            ):
                work, _prompt, warning = agent_explainers.prepare(PID, {}, {}, {}, {})
            self.assertIsNotNone(warning)
            self.assertIn("清理", warning)
            self.assertFalse(repo.exists())
            stale = sorted((agent_dir / PID).glob("repo.stale-*"))
            self.assertEqual(len(stale), 1)
            self.assertEqual((stale[0] / "keep.txt").read_text(encoding="utf-8"), "stale")

    def test_prepare_cleanup_and_rename_failure_raises(self):
        # 回归 #406：残留移 aside 也失败时抛错，由调用方记进 manifest 的 failures。
        with tempfile.TemporaryDirectory() as tmp:
            self._setup_dirs(tmp)
            repo = Path(tmp) / "agent" / PID / "repo"
            repo.mkdir(parents=True)
            with (
                patch.object(
                    agent_explainers, "remove_path_force",
                    side_effect=OSError("permission denied"),
                ),
                patch("os.rename", side_effect=OSError("busy")),
            ):
                with self.assertRaises(RuntimeError):
                    agent_explainers.prepare(PID, {}, {}, {}, {})


if __name__ == "__main__":
    unittest.main()
