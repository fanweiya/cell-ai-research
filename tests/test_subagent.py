from __future__ import annotations

import http.server
import io
import json
import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import subagent


class _LocalPaperServer:
    """真实本地 HTTP 服务：任何 GET 都返回固定正文，供 load_input 走抓取链路。"""

    def __init__(self, body: str):
        payload = body.encode("utf-8")

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format, *args):
                pass

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    def __exit__(self, *exc):
        self._server.shutdown()
        self._server.server_close()



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


class SubagentInputSourceTests(unittest.TestCase):
    """四位 arXiv 编号与 bioRxiv 编号都是数据源，不能当成普通文本内容分析。"""

    def test_classify_routes_github_arxiv_biorxiv_and_content(self):
        self.assertEqual(
            subagent.classify_input_source("https://github.com/org/repo"),
            ("github", "https://github.com/org/repo"),
        )
        # 五位序号 arXiv
        self.assertEqual(subagent.classify_input_source("2509.12596"), ("arxiv", "2509.12596"))
        self.assertEqual(subagent.classify_input_source("2509.12596v3"), ("arxiv", "2509.12596v3"))
        # 合法的四位序号 arXiv 仍要识别为论文，而非内容
        self.assertEqual(subagent.classify_input_source("2411.1788"), ("arxiv", "2411.1788"))
        self.assertEqual(subagent.classify_input_source("2411.1788v2"), ("arxiv", "2411.1788v2"))
        self.assertEqual(
            subagent.classify_input_source("biorxiv:10.1101/2024.05.01.591234"),
            ("biorxiv", "10.1101/2024.05.01.591234"),
        )
        # 普通文本保持内容分类，且不会被误判为 arXiv 或 bioRxiv
        self.assertEqual(
            subagent.classify_input_source("一段关于细胞图像分割的中文描述"),
            ("content", "一段关于细胞图像分割的中文描述"),
        )

    def test_four_digit_arxiv_fetches_remote_not_content(self):
        body = "<article><p>" + ("细胞图像分割模型用于单细胞分辨率的空间转录组分析。 " * 60) + "</p></article>"
        saved = subagent.ARXIV_HTML_BASE
        try:
            with _LocalPaperServer(body) as base:
                subagent.ARXIV_HTML_BASE = base
                result = subagent.load_input("2411.1788")
        finally:
            subagent.ARXIV_HTML_BASE = saved
        self.assertNotEqual(result, "2411.1788")
        self.assertIn("细胞图像分割", result)
        self.assertGreater(len(result), 1000)

    def test_biorxiv_fetches_remote_not_content(self):
        body = "<article><p>" + ("bioRxiv 预印本全文抓取链路验证正文段落内容。 " * 60) + "</p></article>"
        saved = subagent.BIORXIV_CONTENT_BASE
        try:
            with _LocalPaperServer(body) as base:
                subagent.BIORXIV_CONTENT_BASE = base
                result = subagent.load_input("biorxiv:10.1101/2024.05.01.591234")
        finally:
            subagent.BIORXIV_CONTENT_BASE = saved
        self.assertNotEqual(result, "biorxiv:10.1101/2024.05.01.591234"[:3000])
        self.assertIn("预印本", result)
        self.assertGreater(len(result), 10)


if __name__ == "__main__":
    unittest.main()
