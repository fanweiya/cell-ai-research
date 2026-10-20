import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

import gread_remote


TREE = """## Directory Tree
```
README.md
pyproject.toml
src
src/Main.java
src/core/model.cpp
src/core/kernel.cu
src/run.py
notebooks/demo.ipynb
config/train.yaml
tests/test_model.py
images/result.png
```
"""


class GreadRemoteTests(unittest.TestCase):
    def test_candidate_selection_is_language_agnostic_and_keeps_core(self):
        search = """## Search
```
HEAD:src/core/model.cpp:12:class Model
HEAD:src/Main.java:8:public class Main
HEAD:src/run.py:3:def main():
```
"""
        paths = gread_remote._candidate_paths(TREE, [search], repository="org/model")
        self.assertIn("src/Main.java", paths)
        self.assertIn("src/core/model.cpp", paths)
        self.assertIn("src/core/kernel.cu", paths)
        self.assertIn("notebooks/demo.ipynb", paths)
        self.assertIn("tests/test_model.py", paths)
        self.assertNotIn("images/result.png", paths)

    def test_collect_repository_performs_multi_pass_source_read(self):
        def fake_get(path, params, timeout=90):
            del timeout
            if path == "/repo":
                return "# Demo\nA source repository"
            if path == "/tree":
                self.assertEqual(params["depth"], 8)
                return TREE
            if path == "/grep":
                return "HEAD:src/core/model.cpp:12:class Model"
            if path == "/read":
                return "\n\n".join(
                    f"## {item}\n```\nsource for {item}\n```"
                    for item in params["paths"].split(",")
                )
            self.fail(f"unexpected endpoint {path}")

        with patch.object(gread_remote, "_get", side_effect=fake_get):
            data = gread_remote.collect_repository("https://github.com/org/model")

        self.assertEqual(data["analysis_depth"], "multi_pass_static")
        self.assertTrue(data["coverage"]["has_implementation"])
        self.assertTrue(data["coverage"]["tests_present"])
        self.assertIn("java", data["coverage"]["languages_by_extension"])
        self.assertIn("cu", data["coverage"]["languages_by_extension"])
        self.assertIn("src/core/model.cpp", data["source_files"])
        self.assertIn("src/core/model.cpp", data["key_files"])

    def test_analysis_context_prioritizes_source_before_grep(self):
        rendered = gread_remote.as_analysis_context({
            "source": "gread",
            "repository": "org/repo",
            "source_files": "CORE_SOURCE_TOKEN",
            "search_results": ["GREP_TOKEN"],
        })
        parsed = json.loads(rendered)
        self.assertEqual(parsed["source_files"], "CORE_SOURCE_TOKEN")
        self.assertLess(rendered.index("CORE_SOURCE_TOKEN"), rendered.index("GREP_TOKEN"))

    def test_docs_only_repository_is_not_marked_as_code(self):
        coverage = gread_remote._coverage({"README.md", "LICENSE"}, ["README.md"], [])
        self.assertFalse(coverage["has_implementation"])
        self.assertEqual(coverage["repository_kind"], "placeholder_or_docs_only")


if __name__ == "__main__":
    unittest.main()
