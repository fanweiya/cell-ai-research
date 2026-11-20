from __future__ import annotations

import unittest
from pathlib import Path

import generate_index

PROJECT = Path(__file__).resolve().parents[1]


class NumericTokenTests(unittest.TestCase):
    def test_percent_range_marks_both_ends(self):
        source = "region-based methods retained ~60 to ~80% of faithfulness"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            {"percent_range:60", "percent_range:80"},
        )

    def test_percent_range_does_not_absorb_bare_number(self):
        # 源文同时含 "60 to 80%" 与裸数字 "60 GPUs"：
        # 范围端点记为 percent_range，裸 60 必须保持 number 语义。
        source = "trained on 60 GPUs, accuracy rose 60 to 80%"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            {"number:60", "percent_range:60", "percent_range:80"},
        )

    def test_translated_percent_range_matches_source_range(self):
        source = "accuracy rose 60 to 80% on 60 GPUs"
        translated = "在 60 块 GPU 上，准确率从 60% 到 80% 不等"
        valid, reason = generate_index._translation_quality(source, translated)
        self.assertTrue(valid, reason)

    def test_percent_symbol_glued_to_following_word(self):
        source = "a melanoma AUC of 97.84%on PH2, and a DSC of 88.92% on ISIC 2018"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            {"percent:97.84", "percent:88.92", "number:2018"},
        )

    def test_bare_numbers_stay_bare(self):
        self.assertEqual(
            generate_index._numeric_tokens("Six species and 60 pollen grains"),
            {"number:60"},
        )

    def test_metric_names_are_not_unit_multipliers(self):
        source = "0.6890 mAP50-95 and 0.9687 macro-F1"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            {"number:0.689", "number:95", "number:0.9687"},
        )


class TranslationQualityTests(unittest.TestCase):
    def test_percent_range_translation_passes(self):
        source = "retained ~60 to ~80% of faithfulness"
        translated = "基于区域的方法在全息成像下保留了约 60%～80% 的忠实性"
        valid, reason = generate_index._translation_quality(source, translated)
        self.assertTrue(valid, reason)

    def test_percent_attached_to_metric_passes(self):
        source = "a melanoma AUC of 97.84%on PH2"
        translated = "在 PH2 上取得了 97.84% 的黑色素瘤 AUC，泛化表现稳定"
        valid, reason = generate_index._translation_quality(source, translated)
        self.assertTrue(valid, reason)

    def test_missing_number_still_fails(self):
        source = "a DSC of 88.92% on the test set"
        translated = "在测试集上取得了 89.92% 的 DSC，指标略高"
        valid, _ = generate_index._translation_quality(source, translated)
        self.assertFalse(valid)

    def test_dropped_percent_still_fails(self):
        source = "retained 80% of faithfulness"
        translated = "在整体实验中保留了 80 的忠实性指标"
        valid, _ = generate_index._translation_quality(source, translated)
        self.assertFalse(valid)

    def test_empty_source_is_rejected(self):
        valid, reason = generate_index._translation_quality(
            "", "输入内容为空。请提供需要翻译的英文摘要文本。"
        )
        self.assertFalse(valid)
        self.assertIn("原文为空", reason)


if __name__ == "__main__":
    unittest.main()
