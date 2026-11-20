from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import verified_daily

PROJECT = Path(__file__).resolve().parents[1]


class CronEntrypointTests(unittest.TestCase):
    def test_new_paper_build_failure_is_nonzero_and_next_empty_day_retries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'papers.json'
            db.write_text(json.dumps({'database': []}))
            entry = {'arxiv_id': '2609.99999v1', 'base_id': '2609.99999', 'published': datetime.now(timezone.utc).isoformat(), 'title': 'Test paper', 'abstract': 'Test evidence'}
            fetch = Mock(return_value=[entry])
            runner = Mock(side_effect=[
                subprocess.CompletedProcess([], 0, '', ''), # backfill_analysis.py
                subprocess.CompletedProcess([], 0, '', ''), # jev_evaluator.py
                subprocess.CompletedProcess([], 0, '', ''), # build_explainers.py
                subprocess.CompletedProcess([], 1, '', 'injected build error') # generate_index.py
            ])
            with patch.multiple(verified_daily, PROJECT=root, DB_PATH=db, EVIDENCE_DIR=root,
                                LOCK_PATH=root/'lock', fetch_recent_entries=fetch,
                                relevant=Mock(return_value=(True, '')), sanitize_ignored_repositories=Mock(return_value=0),
                                revalidate_unprovenanced_repositories=Mock(return_value=0),
                                verify_github_from_paper=Mock(return_value={}), remote_code_analysis=Mock(return_value=({}, None)),
                                make_record=Mock(return_value={'arxiv_id': entry['arxiv_id']}),
                                render_report=Mock(return_value='report'), run=runner), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(verified_daily.main(), 1)
                self.assertEqual(runner.call_count, 4, verified_daily.render_report.call_args.args[0]['errors'])
                self.assertEqual(len(json.loads(db.read_text())['database']), 1)
                self.assertTrue((root/'.site-update-pending.json').exists())
                fetch.return_value = []
                runner.reset_mock()
                runner.side_effect = None
                runner.return_value = subprocess.CompletedProcess([], 0, '', '')
                self.assertEqual(verified_daily.main(), 0)
                self.assertEqual(runner.call_count, 5)
                self.assertEqual(runner.call_args_list[-1].args[0], ['bash', str(root/'publish_cf_pages.sh')])
                self.assertFalse((root/'.site-update-pending.json').exists())
                runner.reset_mock()
                self.assertEqual(verified_daily.main(), 0)
                self.assertEqual(runner.call_count, 2)

    def test_successful_retry_is_reported_but_unchanged_day_stays_silent(self):
        evidence = {'errors': [], 'run_date': '2026-09-09', 'index_status': '复用上次已生成页面',
                    'publish_status': '已发布', 'evidence_path': 'test.json', 'site_updated': True}
        self.assertIn('Cloudflare 发布：已发布', verified_daily.render_report(evidence, []))
        evidence['site_updated'] = False
        self.assertEqual(verified_daily.render_report(evidence, []), '[SILENT]')

    def test_scan_existing_results_ignores_error_and_corrupt_files(self):
        import backfill_analysis
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            valid = tmp_dir / "2609.00001v1_task_analysis.json"
            valid.write_text(json.dumps({"status": "done", "task": "task_analysis"}))
            err_file = tmp_dir / "2609.00002v1_task_analysis.json"
            err_file.write_text(json.dumps({"error": "network failure", "task": "task_analysis"}))
            corrupt = tmp_dir / "2609.00003v1_task_analysis.json"
            corrupt.write_text("{corrupt json")

            with patch.object(backfill_analysis, "RESULTS_DIR", tmp_dir):
                res = backfill_analysis.scan_existing_results()
                self.assertIn("2609.00001v1", res)
                self.assertNotIn("2609.00002v1", res)
                self.assertNotIn("2609.00003v1", res)


if __name__ == "__main__":
    unittest.main()
