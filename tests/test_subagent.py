from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import subagent


class SubagentTests(unittest.TestCase):
    def test_extract_article_text_handles_inline_tags(self):
        html = """<article>
        <p>This is a paragraph with <span>inline text</span> and <a href="#">a link</a>.</p>
        <p>Another paragraph that has sufficient length for extraction.</p>
        </article>"""
        extracted = subagent._extract_article_text(html)
        self.assertIn("This is a paragraph with inline text and a link.", extracted)
        self.assertIn("Another paragraph that has sufficient length for extraction.", extracted)

    def test_load_input_with_plain_text_file(self):
        temp_file = PROJECT / "tests" / "_temp_input.txt"
        temp_file.write_text("Sample paper text content for testing purposes.", encoding="utf-8")
        try:
            loaded = subagent.load_input(str(temp_file))
            self.assertEqual(loaded, "Sample paper text content for testing purposes.")
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def test_call_a1_uses_urllib_and_returns_json(self):
        fake_response = io.BytesIO(json.dumps({
            "choices": [{"message": {"content": json.dumps({"summary": "test-ok"})}}]
        }).encode("utf-8"))

        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = fake_response
        mock_resp.read.side_effect = fake_response.read

        with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
            res = subagent.call_a1("prompt", timeout=45, retries=1)
            self.assertEqual(res, {"summary": "test-ok"})
            self.assertEqual(mock_urlopen.call_count, 1)

    def test_arxiv_failure_raises_runtime_error(self):
        with patch("urllib.request.urlopen", side_effect=RuntimeError("connection refused")):
            with self.assertRaises(RuntimeError):
                subagent.load_input("2607.04353")

    def test_subagent_error_does_not_write_output_and_exits_nonzero(self):
        output_file = PROJECT / "tests" / "_temp_result_should_not_exist.json"
        if output_file.exists():
            output_file.unlink()
        try:
            with patch("subagent.call_a1", return_value={"error": "endpoint failure"}), \
                 patch("subagent.load_input", return_value="paper content"), \
                 patch("sys.argv", ["subagent.py", "--task", "task_analysis", "--paper_id", "2607.99999",
                                    "--input", "2607.99999", "--output", str(output_file)]):
                exit_code = subagent.main()
                self.assertEqual(exit_code, 1)
                self.assertFalse(output_file.exists())
        finally:
            if output_file.exists():
                output_file.unlink()


if __name__ == "__main__":
    unittest.main()
