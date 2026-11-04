import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from daily_site_update import update_site


class SiteUpdateTests(unittest.TestCase):
    def exercise(self, changed, runner, root, evidence=None):
        evidence = evidence or {'errors': [], 'index_status': '未执行'}
        update_site(evidence, changed, root, root / 'pending.json', runner, ['python', 'generate_index.py'])
        return evidence

    def test_unchanged_run_does_not_build_or_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            runner = Mock()
            self.exercise(False, runner, Path(tmp))
            runner.assert_not_called()

    def test_build_failure_cannot_publish_and_retries_on_unchanged_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = Mock(return_value=subprocess.CompletedProcess([], 1, '', 'build failed'))
            evidence = self.exercise(True, runner, root)
            self.assertEqual(runner.call_count, 1)
            self.assertTrue(evidence['errors'])
            self.assertTrue((root / 'pending.json').exists())
            runner = Mock(return_value=subprocess.CompletedProcess([], 0, '', ''))
            evidence = self.exercise(False, runner, root)
            self.assertEqual(runner.call_count, 2)
            self.assertEqual(runner.call_args_list[1].args[0], ['bash', str(root / 'publish_cf_pages.sh')])
            self.assertTrue(evidence['site_updated'])
            self.assertFalse((root / 'pending.json').exists())

    def test_publish_failure_only_retries_publish_and_preserves_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            database = root / 'papers.json'
            database.write_text('original data')
            runner = Mock(side_effect=[subprocess.CompletedProcess([], 0, '', ''), subprocess.CompletedProcess([], 1, '', 'publish failed')])
            evidence = self.exercise(True, runner, root)
            self.assertTrue(evidence['errors'])
            self.assertEqual(database.read_text(), 'original data')
            runner = Mock(return_value=subprocess.CompletedProcess([], 0, '', ''))
            evidence = self.exercise(False, runner, root)
            self.assertEqual(runner.call_count, 1)
            self.assertEqual(runner.call_args.args[0][0], 'bash')
            self.assertEqual(evidence['publish_status'], '已发布')

    def test_corrupt_pending_file_recovers_to_rebuild(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pending = root / 'pending.json'
            pending.write_text('not valid json {[[')
            runner = Mock(return_value=subprocess.CompletedProcess([], 0, '', ''))
            evidence = self.exercise(False, runner, root)
            self.assertEqual(runner.call_count, 2)
            self.assertEqual(evidence['publish_status'], '已发布')

    def test_build_assertion_failure_stops_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'index.html').write_text('<html><body>No dvh here</body></html>', encoding='utf-8')
            runner = Mock(return_value=subprocess.CompletedProcess([], 0, '', ''))
            evidence = self.exercise(True, runner, root)
            self.assertEqual(runner.call_count, 1)
            self.assertTrue(any('100dvh' in str(e) for e in evidence['errors']))
            self.assertEqual(evidence['index_status'], '失败')

    def test_timeout_is_recorded_and_pending_is_retained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = Mock(side_effect=subprocess.TimeoutExpired('build', 900))
            evidence = self.exercise(True, runner, root)
            self.assertTrue(evidence['errors'])
            self.assertTrue((root / 'pending.json').exists())
