from __future__ import annotations

import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import generate_index
import verified_daily


class CodeReportTests(unittest.TestCase):
    def test_daily_index_build_keeps_incremental_analysis_enabled(self):
        command = verified_daily.index_build_command("/usr/bin/python-test")
        self.assertEqual(command[0], "/usr/bin/python-test")
        self.assertNotIn("--no-images", command)
        self.assertNotIn("--no-code-analysis", command)

    def test_code_summary_parallelism_is_conservative_for_large_source_prompts(self):
        self.assertGreaterEqual(generate_index.CODE_SUMMARY_WORKERS, 1)
        self.assertLessEqual(generate_index.CODE_SUMMARY_WORKERS, 2)
        self.assertGreaterEqual(generate_index.CODE_SUMMARY_MAX_TOKENS, 6000)

    def test_github_candidate_requires_an_explicit_paper_code_statement(self):
        dependency_html = """
        <p>We obtained Xenium slides from HEST-1k
        (<a href="https://github.com/mahmoodlab/HEST">repository</a>).</p>
        <p>The denoiser is publicly available at
        <a href="https://github.com/cszn/DPIR">DPIR</a>.</p>
        """
        official_html = """
        <p>Code is publicly available at
        <a href="https://github.com/UARK-AICV/PolypSteer">our repository</a>.</p>
        """
        self.assertEqual(verified_daily.official_github_candidates(dependency_html), [])
        self.assertEqual(
            [item["url"] for item in verified_daily.official_github_candidates(official_html)],
            ["https://github.com/UARK-AICV/PolypSteer"],
        )
        spaced_url = "The source code is available at https://github.com/ SMLCI/DART-MLCI."
        self.assertEqual(
            [item["url"] for item in verified_daily.official_github_candidates(spaced_url)],
            ["https://github.com/SMLCI/DART-MLCI"],
        )

    def test_bibliography_github_link_is_not_paper_code(self):
        html = """
        <li class="ltx_bibitem"><span class="ltx_bibblock">Ultralytics YOLO.
        Source code is available at https://github.com/ultralytics/ultralytics.</span></li>
        """
        self.assertEqual(verified_daily.official_github_candidates(html), [])

    def test_repository_discovery_uses_verified_abstract_when_html_loses_href(self):
        html = """
        <div class="ltx_abstract">
          Code is publicly available <span class="ltx_ref ltx_ref_self">here</span>.
        </div>
        """
        abstract = (
            "Code is publicly available at "
            "https://github.com/AtlasAnalyticsLab/GatedSRP."
        )
        with patch.object(verified_daily, "fetch", return_value=html):
            github = verified_daily.discover_github_from_paper(
                "2608.08374",
                {"page_errors": []},
                paper_title="Gated Spatial Redundancy Projection for Pathology Transformer Attentions",
                paper_abstract=abstract,
            )
        self.assertEqual(github["url"], "https://github.com/AtlasAnalyticsLab/GatedSRP")
        self.assertEqual(github["provenance"], "paper_code_statement")

    def test_prompt_contains_source_and_static_review_rules(self):
        prompt = generate_index._code_summary_prompt(
            "https://github.com/org/repo",
            {"architecture": "old README summary"},
            {
                "analysis_depth": "multi_pass_static",
                "coverage": {"has_implementation": True},
                "source_files": "## src/core.py\n```\nclass Core: pass\n```",
                "key_files": ["src/core.py"],
            },
        )
        self.assertIn("class Core", prompt)
        self.assertIn("交叉检查", prompt)
        self.assertIn("代码也没有被执行", prompt)
        self.assertIn('"issues"', prompt)
        self.assertNotIn("prior_static_analysis", prompt)
        self.assertNotIn("old README summary", prompt)

    def test_parse_report_requires_evidence_and_enforces_placeholder(self):
        raw = json.dumps({
            "summary": "该仓库目前只有说明文件，没有可以执行的算法实现代码。",
            "repository_kind": "implementation",
            "architecture": "无法确认",
            "call_chain": "无法确认",
            "core_modules": [],
            "dependencies": [],
            "reproduction_readiness": "ready",
            "reproduction_notes": "无法复现",
            "issues": [
                {"severity": "high", "finding": "有证据", "evidence": ["README.md"], "confidence": 2},
                {"severity": "high", "finding": "无证据", "evidence": []},
            ],
            "static_limitations": [],
            "confidence": 1.5,
        }, ensure_ascii=False)
        report = generate_index._parse_code_report(raw, coverage={"has_implementation": False})
        self.assertEqual(report["repository_kind"], "placeholder")
        self.assertEqual(report["reproduction_readiness"], "placeholder")
        self.assertEqual(len(report["issues"]), 1)
        self.assertEqual(report["issues"][0]["confidence"], 1.0)
        self.assertEqual(report["confidence"], 1.0)
        self.assertTrue(report["static_limitations"])
        self.assertEqual(report["version"], generate_index.CODE_REPORT_VERSION)

    def test_source_excerpt_samples_multiple_files(self):
        source = "\n\n".join(
            f"## src/file{index}.py\n```\n" + (str(index) * 100) + "\n```"
            for index in range(4)
        )
        excerpt = generate_index._bounded_source_excerpt(source, max_chars=1000, per_file=180)
        self.assertIn("file0.py", excerpt)
        self.assertIn("file3.py", excerpt)

    def test_source_excerpt_does_not_treat_markdown_headings_as_files(self):
        source = (
            "## README.md\n```markdown\n# Project\n## Installation\nsteps\n```\n\n"
            "## src/core.py\n```python\nclass Core: pass\n```"
        )
        excerpt = generate_index._bounded_source_excerpt(source, max_chars=1000, per_file=500)
        self.assertIn("README.md", excerpt)
        self.assertIn("src/core.py", excerpt)

    def test_report_renderer_escapes_remote_content(self):
        rendered = generate_index._render_code_report({
            "summary": "<script>alert(1)</script> 中文总结",
            "repository_kind": "implementation",
            "reproduction_readiness": "needs_fixes",
            "issues": [],
            "confidence": 1.0,
            "version": generate_index.CODE_REPORT_VERSION,
        })
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

    def test_low_confidence_report_is_not_rendered_as_factual_analysis(self):
        rendered = generate_index._render_code_report({
            "summary": "声称存在完整调用链。",
            "repository_kind": "partial",
            "reproduction_readiness": "blocked",
            "architecture": "input -> invented encoder -> output",
            "confidence": 0.2,
            "version": generate_index.CODE_REPORT_VERSION,
        })
        self.assertEqual(rendered, "")

    def test_page_fails_closed_for_unverified_repository_and_formats_empty_scores(self):
        page = generate_index.generate_html(
            [{
                "arxiv_id": "2608.00001v1",
                "title": "Demo",
                "published_date": "2026-08-08",
                "authors": ["A. Author"],
                "abstract": "cell imaging",
                "task_type": ["segmentation"],
                "priority": None,
                "research_score": None,
                "engineering_score": None,
                "status": {
                    "html": "done",
                    "github": {
                        "url": "https://github.com/dependency/library",
                        "has_code": True,
                    },
                },
            }],
            {},
            "2026-08-12 10:00",
        )
        self.assertNotIn("未评分 (1)", page)
        self.assertNotIn("研究：未评分", page)
        self.assertNotIn("工程：未评分", page)
        self.assertNotIn("D 级 (1)", page)
        self.assertIn("有代码 (0)", page)
        self.assertNotIn("P:None", page)
        self.assertNotIn("R:None", page)
        self.assertNotIn("https://github.com/dependency/library", page)

    def test_display_statuses_preserve_failure_skip_and_hide_research_review(self):
        render = generate_index._status_icons
        self.assertEqual(render({"html": "failed"}), render({"html": "error"}))
        result = render({"html": "completed", "task_analysis": "done",
                         "code_analysis": "skipped", "reproduction": {"status": "done", "level": "A"}}, True, True)
        self.assertIn("全文获取：完成", result)
        self.assertIn("摘要整理：完成", result)
        self.assertNotIn("研究评审", result)
        self.assertIn("代码静态分析：已跳过", result)
        self.assertNotIn("复现评估", result)
        self.assertNotIn("实际运行", result)
        self.assertNotIn("复现通过", result)

    def test_placeholder_repository_is_not_marked_as_published_code(self):
        record = verified_daily.make_record(
            {
                "arxiv_id": "2608.00001v1",
                "title": "Demo",
                "published": "2026-08-08T00:00:00Z",
                "authors": [],
                "categories": ["cs.CV"],
                "abstract": "cell imaging",
                "base_id": "2608.00001",
            },
            {"status": "done", "has_code": True, "url": "https://github.com/org/docs"},
            datetime.now(timezone.utc),
            {"has_implementation": False, "repository_kind": "placeholder_or_docs_only"},
            None,
        )
        self.assertFalse(record["has_code"])
        self.assertFalse(record["status"]["github"]["has_code"])
        self.assertTrue(record["status"]["github"]["repository_found"])
        self.assertEqual(record["status"]["code_analysis"], "skipped")

    def test_repository_matches_title_rejects_empty_or_too_short_title(self):
        self.assertFalse(verified_daily._repository_matches_title("my-repo", ""))
        self.assertFalse(verified_daily._repository_matches_title("my-repo", "AI"))
        self.assertFalse(verified_daily._repository_matches_title("cells", "细胞图像分割模型"))

    def test_bibliography_with_long_author_list_is_rejected(self):
        long_authors = " ".join(f"Author{i} Surname{i}," for i in range(80))
        html = f"""
        <li class="ltx_bibitem"><span class="ltx_bibblock">{long_authors}
        Source code is available at https://github.com/ultralytics/yolov8.</span></li>
        """
        self.assertEqual(verified_daily.official_github_candidates(html), [])

    def test_github_pages_filters_ignored_repos(self):
        html = """
        <p>Project page at https://arxiv.github.io/html_feedback with code available.</p>
        """
        candidates = verified_daily.official_github_candidates(html, paper_title="Feedback Project")
        self.assertEqual(candidates, [])

    def test_path_traversal_arxiv_id_raises_value_error(self):
        with self.assertRaises(ValueError):
            verified_daily.discover_github_from_paper("../../etc/passwd", {"page_errors": []})

        with self.assertRaises(ValueError):
            verified_daily.remote_code_analysis(
                {"has_code": True, "url": "https://github.com/org/repo"},
                "../../escape",
                {"gread_analyses": []},
            )

    def test_rss_corrupt_pubdate_is_skipped(self):
        xml = """<rss version="2.0">
        <channel>
          <item>
            <link>https://arxiv.org/abs/2609.12345</link>
            <title>Valid Paper</title>
            <description>Valid abstract</description>
            <pubDate>not-a-valid-date</pubDate>
          </item>
        </channel>
        </rss>"""
        entries = verified_daily.parse_feed(xml)
        self.assertEqual(entries, [])

    def test_revalidate_does_not_match_repository_to_abstract_words(self):
        paper = {
            "arxiv_id": "2608.00001v1",
            "title": "A Novel Architecture for Segmentation",
            "abstract": "We build an atlas of cell images and benchmark on large collections.",
            "status": {
                "github": {"url": "https://github.com/thirdparty/atlas", "has_code": True}
            },
        }
        with patch.object(verified_daily, "discover_github_from_paper", return_value={"provenance_status": "none"}):
            repaired = verified_daily.revalidate_unprovenanced_repositories([paper], {})
            self.assertEqual(repaired, 1)
            self.assertNotEqual(paper["status"]["github"].get("provenance"), "paper_identity_match")
            self.assertNotEqual(paper["status"]["github"].get("url"), "https://github.com/thirdparty/atlas")

    def test_revalidate_isolates_invalid_arxiv_id_per_paper(self):
        bad_paper = {
            "arxiv_id": "../../etc/passwd",
            "title": "Bad Paper",
            "status": {
                "github": {"url": "https://github.com/foo/bar", "has_code": True}
            },
        }
        good_paper = {
            "arxiv_id": "2608.12345v1",
            "title": "Good Paper",
            "status": {
                "github": {"url": "https://github.com/foo/good", "has_code": True}
            },
        }
        evidence = {"page_errors": []}
        with patch.object(verified_daily, "discover_github_from_paper", return_value={"provenance_status": "source_unavailable"}):
            verified_daily.revalidate_unprovenanced_repositories([bad_paper, good_paper], evidence)
            self.assertEqual(len(evidence["page_errors"]), 1)
            self.assertEqual(evidence["page_errors"][0]["arxiv_id"], "../../etc/passwd")


if __name__ == "__main__":
    unittest.main()
