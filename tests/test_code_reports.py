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
        good_result = {
            "url": "https://github.com/foo/good",
            "provenance": "paper_code_statement",
            "provenance_status": "verified",
            "provenance_context": "code available at https://github.com/foo/good",
            "relation_signal": "matched",
        }
        with patch.object(verified_daily, "discover_github_from_paper", return_value=good_result) as mock_discover:
            verified_daily.revalidate_unprovenanced_repositories([bad_paper, good_paper], evidence)
            self.assertEqual(len(evidence["page_errors"]), 1)
            self.assertEqual(evidence["page_errors"][0]["arxiv_id"], "../../etc/passwd")
            mock_discover.assert_called_once()
            call_args, call_kwargs = mock_discover.call_args
            self.assertEqual(call_args[0], "2608.12345v1")
            self.assertEqual(call_kwargs.get("paper_title"), "Good Paper")
            self.assertEqual(good_paper["status"]["github"]["provenance"], "paper_code_statement")

    def test_backfill_scan_matches_both_versioned_and_unversioned_pids(self):
        import backfill_analysis
        import tempfile
        import shutil

        temp_results = Path(tempfile.mkdtemp(prefix="cell_results_"))
        try:
            (temp_results / "2607.11754_task_analysis.json").write_text(
                json.dumps({"status": "done"}), encoding="utf-8"
            )
            (temp_results / "2608.12345v2_task_analysis.json").write_text(
                json.dumps({"status": "done"}), encoding="utf-8"
            )
            with patch.object(backfill_analysis, "RESULTS_DIR", temp_results):
                scanned = backfill_analysis.scan_existing_results()
                self.assertIn("2607.11754", scanned)
                self.assertIn("2608.12345v2", scanned)
                self.assertIn("task_analysis", scanned["2607.11754"])
                self.assertIn("task_analysis", scanned["2608.12345v2"])
        finally:
            shutil.rmtree(temp_results, ignore_errors=True)

    def test_filter_figures_preserves_fallback_and_avoids_empty_wipeout(self):
        import tempfile
        import shutil

        temp_dir = Path(tempfile.mkdtemp(prefix="cell_figs_"))
        try:
            # 模拟 3 张原图，其中第 1 张不相关、第 2、3 张相关
            figs = [
                {"data": "img0", "src": "data/figures/fig0.jpg"},
                {"data": "img1", "src": "data/figures/fig1.jpg"},
                {"data": "img2", "src": "data/figures/fig2.jpg"},
            ]

            def mock_analyze(b64_data, title):
                return (b64_data != "img0", 8 if b64_data != "img0" else 0, "cap")

            pid = "2607.11754"
            with patch.object(generate_index, "FIGURES_DIR", temp_dir), \
                 patch.object(generate_index, "_analyze_image", side_effect=mock_analyze):
                # 首次过滤：保留第 2、3 张
                filtered = generate_index._filter_figures_by_relevance(figs, "Title", pid)
                self.assertEqual(len(filtered), 2)

                # 模拟 extract_all_figures 将过滤结果写回 cache
                cache_file = temp_dir / "2607.11754.json"
                with open(cache_file, "w") as f:
                    json.dump(filtered, f)

                # 读路径：_load_figures_filtered 不应二次误杀
                loaded = generate_index._load_figures_filtered(pid)
                self.assertEqual(len(loaded), 2)

            # 全不相关场景
            figs_all_bad = [{"data": "bad", "src": "data/figures/bad.jpg"}]
            pid2 = "2607.99999"
            with patch.object(generate_index, "FIGURES_DIR", temp_dir), \
                 patch.object(generate_index, "_analyze_image", return_value=(False, 0, "irrelevant")):
                filtered2 = generate_index._filter_figures_by_relevance(figs_all_bad, "Title", pid2)
                self.assertEqual(len(filtered2), 1)
                self.assertEqual(filtered2[0]["score"], 5)

                cache_file2 = temp_dir / "2607.99999.json"
                with open(cache_file2, "w") as f:
                    json.dump(filtered2, f)

                loaded2 = generate_index._load_figures_filtered(pid2)
                self.assertEqual(len(loaded2), 1)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_verified_daily_survives_backfill_timeout_and_proceeds_to_update_site(self):
        import subprocess

        evidence: dict = {"errors": []}
        update_site_called = []

        def mock_update_site(ev, changed, project, pending_file, runner, cmd):
            update_site_called.append(True)

        def mock_run(cmd, timeout=90):
            if "backfill_analysis.py" in str(cmd):
                raise subprocess.TimeoutExpired(cmd, timeout)
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        with patch.object(verified_daily, "run", side_effect=mock_run), \
             patch.object(verified_daily, "update_site", side_effect=mock_update_site), \
             patch.object(verified_daily, "mark_site_pending"):
            # Execute the core block under simulated timeout
            before_backfill = "hash"
            backfill_timeout = False
            backfill = None
            try:
                backfill = verified_daily.run(["python3", "backfill_analysis.py"], timeout=90)
            except subprocess.TimeoutExpired:
                backfill_timeout = True
            if backfill_timeout or backfill is None:
                evidence["errors"].append("backfill_analysis.py: timed out after 90s")
            elif backfill.returncode == 0:
                evidence["analysis_backfilled"] = True
            mock_update_site(evidence, False, verified_daily.PROJECT, Path(".pending"), verified_daily.run, [])

            self.assertTrue(backfill_timeout)
            self.assertEqual(evidence["errors"], ["backfill_analysis.py: timed out after 90s"])
            self.assertEqual(len(update_site_called), 1)

    def test_generate_index_clean_id_handles_high_version_numbers(self):
        import re

        test_pids = [
            ("2410.12345v10", "2410.12345"),
            ("2410.12345v1", "2410.12345"),
            ("2410.12345v2", "2410.12345"),
            ("2410.12345v3", "2410.12345"),
            ("2410.12345", "2410.12345"),
        ]
        for pid, expected in test_pids:
            clean_id = re.sub(r"v\d+$", "", pid)
            self.assertEqual(clean_id, expected)

    def test_backfill_analysis_tie_breaker_sorts_by_paper_id(self):
        import backfill_analysis

        papers_data = {
            "database": [
                {
                    "arxiv_id": "2410.00003",
                    "relevance": "passed",
                    "status": {"task_analysis": "pending"},
                    "jev_evaluation": {"composite_priority": 8.0},
                },
                {
                    "arxiv_id": "2410.00001",
                    "relevance": "passed",
                    "status": {"task_analysis": "pending"},
                    "jev_evaluation": {"composite_priority": 8.0},
                },
                {
                    "arxiv_id": "2410.00002",
                    "relevance": "passed",
                    "status": {"task_analysis": "pending"},
                    "jev_evaluation": {"composite_priority": 8.0},
                },
            ]
        }
        todo = backfill_analysis.build_todo_tasks(papers_data, {})
        ordered_pids = [item[0] for item in todo]
        self.assertEqual(ordered_pids, ["2410.00001", "2410.00002", "2410.00003"])

    def test_jev_evaluator_paradigm_confidence_bounds_validation(self):
        import jev_evaluator

        base_answers = {
            "methodological_novelty": {"score": 5.0, "confidence": 0.8},
            "technical_soundness": {"score": 6.0, "confidence": 0.8},
            "biological_utility": {"score": 7.0, "confidence": 0.8},
            "reproducibility_readiness": {"score": 4.0, "confidence": 0.8},
            "primary_paradigm": {"choice": "multimodal_foundation", "confidence": 0.9},
        }
        asked_dims = [
            "methodological_novelty",
            "technical_soundness",
            "biological_utility",
            "reproducibility_readiness",
        ]
        evidence_info = {"evidence_hash": "dummy_hash", "evidence_sources": []}

        for valid_conf in (0.0, 1.0, 0.5):
            answers = json.loads(json.dumps(base_answers))
            answers["primary_paradigm"]["confidence"] = valid_conf
            res = jev_evaluator.format_evaluation_result(answers, asked_dims, evidence_info)
            self.assertEqual(res["paradigm_confidence"], valid_conf)

        for invalid_conf in (-0.01, 1.01, -1.0, 2.0):
            answers = json.loads(json.dumps(base_answers))
            answers["primary_paradigm"]["confidence"] = invalid_conf
            with self.assertRaises(ValueError):
                jev_evaluator.format_evaluation_result(answers, asked_dims, evidence_info)

    def test_jev_evaluator_channel_resolution(self):
        import jev_evaluator

        # 验证 4 个默认通道配置解析与优先级顺序 (typesafe -> codiv -> subq -> cloudflare)
        channel_names = [ch["name"] for ch in jev_evaluator.EVAL_CHANNELS]
        self.assertEqual(channel_names, ["typesafe", "codiv", "subq", "cloudflare"])

        typesafe_key, typesafe_model, typesafe_url, typesafe_headers = jev_evaluator.resolve_channel_config(jev_evaluator.EVAL_CHANNELS[0])
        self.assertIsNotNone(typesafe_key)
        self.assertTrue(str(typesafe_key).startswith("apikey_"))
        self.assertEqual(typesafe_model, "jev-preview")
        self.assertEqual(typesafe_headers.get("TypeSafe-Danger-Zone-Images"), "true")

        codiv_key, codiv_model, codiv_url, codiv_headers = jev_evaluator.resolve_channel_config(jev_evaluator.EVAL_CHANNELS[1])
        self.assertIsNotNone(codiv_key)
        self.assertTrue(str(codiv_key).startswith("sk-codiv-"))
        self.assertEqual(codiv_model, "openjev-latest")
        self.assertIn("User-Agent", codiv_headers)

        subq_key, subq_model, subq_url, subq_headers = jev_evaluator.resolve_channel_config(jev_evaluator.EVAL_CHANNELS[2])
        self.assertIsNotNone(subq_key)
        self.assertTrue(str(subq_key).startswith("sk-proj-"))
        self.assertEqual(subq_model, "subq-snap-1.1")
        self.assertEqual(subq_url, "https://api.subq.ai/v1/systemone")

        cf_key, cf_model, cf_url, cf_headers = jev_evaluator.resolve_channel_config(jev_evaluator.EVAL_CHANNELS[3])
        self.assertIsNotNone(cf_key)
        self.assertTrue(str(cf_key).startswith("cfut_"))
        self.assertEqual(cf_model, "clef-flash")
        self.assertIn("/ai/run/@cf/cloudflare/clef-flash", cf_url)

    def test_jev_evaluator_channel_fallback_mechanism(self):
        import urllib.error
        import jev_evaluator

        paper = {
            "arxiv_id": "2410.99999",
            "title": "Fallback test paper",
            "abstract": "Testing multi-channel fallback",
        }
        evidence_info = {
            "code_status": "none",
            "code_desc": "",
            "evidence_snippets": {},
            "evidence_sources": [],
            "evidence_sufficiency": {
                "methodological_novelty": True,
                "technical_soundness": True,
                "biological_utility": True,
                "reproducibility_readiness": True,
            },
            "evidence_text": "Sample text",
            "evidence_hash": "testhash",
        }

        success_response = {
            "model": "codiv-model",
            "answers": {
                "methodological_novelty": {"score": 6.0, "confidence": 0.8},
                "technical_soundness": {"score": 7.0, "confidence": 0.8},
                "biological_utility": {"score": 8.0, "confidence": 0.8},
                "reproducibility_readiness": {"score": 5.0, "confidence": 0.8},
                "primary_paradigm": {"choice": "multimodal_foundation", "confidence": 0.9},
            },
        }

        call_records = []

        class DummyResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return json.dumps(success_response).encode("utf-8")

        def fake_urlopen(req, timeout=45):
            call_records.append(req.full_url)
            if "typesafe" in req.full_url:
                raise urllib.error.URLError("Simulated connection timeout")
            return DummyResponse()

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            res = jev_evaluator.evaluate_single_paper(paper, evidence_info=evidence_info, retries=1)
            self.assertEqual(res["primary_paradigm"], "multimodal_foundation")
            self.assertEqual(len(call_records), 2)
            self.assertIn("api.typesafe.ai", call_records[0])
            self.assertIn("api.codiv.ai", call_records[1])

    def test_jev_evaluator_single_channel_does_not_override_non_typesafe_key(self):
        import jev_evaluator

        paper = {"arxiv_id": "2410.99991", "title": "Single channel key test"}
        evidence_info = {
            "code_status": "none",
            "code_desc": "",
            "evidence_snippets": {},
            "evidence_sources": [],
            "evidence_sufficiency": {
                "methodological_novelty": True,
                "technical_soundness": True,
                "biological_utility": True,
                "reproducibility_readiness": True,
            },
            "evidence_text": "Sample text",
            "evidence_hash": "testhash",
        }
        captured_auth = []

        class DummyResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return json.dumps({
                    "model": "codiv-model",
                    "answers": {
                        "methodological_novelty": {"score": 6.0, "confidence": 0.8},
                        "technical_soundness": {"score": 7.0, "confidence": 0.8},
                        "biological_utility": {"score": 8.0, "confidence": 0.8},
                        "reproducibility_readiness": {"score": 5.0, "confidence": 0.8},
                        "primary_paradigm": {"choice": "multimodal_foundation", "confidence": 0.9},
                    },
                }).encode("utf-8")

        def fake_urlopen(req, timeout=45):
            captured_auth.append(req.headers.get("Authorization"))
            return DummyResponse()

        single_channel = [{
            "name": "codiv",
            "endpoint": "https://api.codiv.ai/v1/systemone",
            "default_model": "openjev-latest",
            "default_key": "channel-native-key",
            "extra_headers": {},
        }]

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            jev_evaluator.evaluate_single_paper(
                paper,
                api_key="caller-custom-key",
                evidence_info=evidence_info,
                channels=single_channel,
                retries=1
            )
            self.assertEqual(len(captured_auth), 1)
            self.assertEqual(captured_auth[0], "Bearer channel-native-key")

    def test_jev_evaluator_validation_failure_fast_fails_without_fallback(self):
        import jev_evaluator

        paper = {"arxiv_id": "2410.99992", "title": "Validation fail-fast test"}
        evidence_info = {
            "code_status": "none",
            "code_desc": "",
            "evidence_snippets": {},
            "evidence_sources": [],
            "evidence_sufficiency": {
                "methodological_novelty": True,
                "technical_soundness": True,
                "biological_utility": True,
                "reproducibility_readiness": True,
            },
            "evidence_text": "Sample text",
            "evidence_hash": "testhash",
        }

        class InvalidResponse:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return json.dumps({
                    "model": "model-1",
                    "answers": {
                        "methodological_novelty": {"score": 6.0, "confidence": 0.8},
                    },
                }).encode("utf-8")

        call_count = 0
        def fake_urlopen(req, timeout=45):
            nonlocal call_count
            call_count += 1
            return InvalidResponse()

        two_channels = [
            {"name": "typesafe", "endpoint": "https://api.typesafe.ai/v1/systemone", "default_key": "k1", "default_model": "m1", "extra_headers": {}},
            {"name": "codiv", "endpoint": "https://api.codiv.ai/v1/systemone", "default_key": "k2", "default_model": "m2", "extra_headers": {}},
        ]

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            with self.assertRaises(ValueError) as ctx:
                jev_evaluator.evaluate_single_paper(
                    paper,
                    evidence_info=evidence_info,
                    channels=two_channels,
                    retries=2
                )
            self.assertIn("Missing required response field", str(ctx.exception))
            self.assertEqual(call_count, 1)

    def test_jev_evaluator_all_channels_without_credentials_reports_detail(self):
        import jev_evaluator

        paper = {"arxiv_id": "2410.99993", "title": "No credentials test"}
        evidence_info = {
            "code_status": "none",
            "code_desc": "",
            "evidence_snippets": {},
            "evidence_sources": [],
            "evidence_sufficiency": {
                "methodological_novelty": True,
                "technical_soundness": True,
                "biological_utility": True,
                "reproducibility_readiness": True,
            },
            "evidence_text": "Sample text",
            "evidence_hash": "testhash",
        }

        channels_without_keys = [
            {"name": "custom_ch_1", "endpoint": "https://api.example.com", "extra_headers": {}},
            {"name": "custom_ch_2", "endpoint": "https://api.example.com", "extra_headers": {}},
        ]

        with self.assertRaises(RuntimeError) as ctx:
            jev_evaluator.evaluate_single_paper(
                paper,
                evidence_info=evidence_info,
                channels=channels_without_keys,
                retries=1
            )
        err_msg = str(ctx.exception)
        self.assertIn("[custom_ch_1] missing credentials", err_msg)
        self.assertIn("[custom_ch_2] missing credentials", err_msg)


if __name__ == "__main__":
    unittest.main()
