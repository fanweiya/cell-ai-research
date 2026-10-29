import json
import tempfile
import unittest
from pathlib import Path

from jev_evaluator import _atomic_json


class JevPersistenceTests(unittest.TestCase):
    def setUp(self):
        work_root = Path(__file__).resolve().parents[1] / "tmp"
        work_root.mkdir(exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix="jev-persistence-", dir=work_root)
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def test_string_path_saves_checkpoints_and_final_scores(self):
        path = self.root / "papers.json"
        data = {"database": [{"arxiv_id": "test-paper", "title": "细胞研究", "research_score": 1}]}
        _atomic_json(str(path), data)
        for score in range(2, 12):
            data["database"][0]["research_score"] = score
            data["database"][0]["jev_evaluation"] = {"composite_priority": score, "code_status": "verified"}
            _atomic_json(str(path), data)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), data)
        self.assertEqual(list(self.root.glob("*.tmp")), [])

    def test_path_object_creates_parent_directory(self):
        path = self.root / "nested" / "论文评分.json"
        data = {"database": [{"title": "结果已写入", "research_score": 8.5}]}
        _atomic_json(path, data)
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), data)
        self.assertEqual(list(path.parent.glob("*.tmp")), [])

    def test_invalid_json_preserves_the_existing_database(self):
        path = self.root / "papers.json"
        data = {"database": [{"research_score": 8.5}]}
        _atomic_json(str(path), data)
        original = path.read_bytes()
        with self.assertRaises(TypeError):
            _atomic_json(str(path), {"database": [object()]})
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(self.root.glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
