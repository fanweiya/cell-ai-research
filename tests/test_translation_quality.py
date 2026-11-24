from __future__ import annotations

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import generate_index

PROJECT = Path(__file__).resolve().parents[1]


class NumericTokenTests(unittest.TestCase):
    def test_percent_range_marks_both_ends(self):
        source = "region-based methods retained ~60 to ~80% of faithfulness"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            Counter({"percent_range:60": 1, "percent_range:80": 1}),
        )

    def test_percent_range_does_not_absorb_bare_number(self):
        # 源文同时含 "60 to 80%" 与裸数字 "60 GPUs"：
        # 范围端点记为 percent_range，裸 60 必须保持 number 语义。
        source = "trained on 60 GPUs, accuracy rose 60 to 80%"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            Counter({"number:60": 1, "percent_range:60": 1, "percent_range:80": 1}),
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
            Counter({"percent:97.84": 1, "percent:88.92": 1, "number:2018": 1}),
        )

    def test_bare_numbers_stay_bare(self):
        self.assertEqual(
            generate_index._numeric_tokens("Six species and 60 pollen grains"),
            Counter({"number:60": 1}),
        )

    def test_metric_names_are_not_unit_multipliers(self):
        source = "0.6890 mAP50-95 and 0.9687 macro-F1"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            Counter({"number:0.689": 1, "number:95": 1, "number:0.9687": 1}),
        )

    def test_repeated_value_keeps_multiplicity(self):
        # 回归 #405：同一数值既作范围端点又独立出现时，计数必须保留。
        source = "accuracy rose from 60% to 80%, with 60% dropout in training"
        self.assertEqual(
            generate_index._numeric_tokens(source),
            Counter({"percent_range:60": 1, "percent_range:80": 1, "percent:60": 1}),
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

    def test_percent_range_verb_breaks_range_still_passes(self):
        # 回归 #5：源文 "from 60% to 80%" 译作 "从 60% 提升到 80%"，
        # "提升到" 隔断范围写法，译文只产出 percent:60/80，
        # 与源文 percent_range:60/80 按数值等价，不应判遗漏数字。
        source = "accuracy improved from 60% to 80% with the new method"
        translated = "新方法将准确率从 60% 提升到 80%，效果显著提升"
        valid, reason = generate_index._translation_quality(source, translated)
        self.assertTrue(valid, reason)

    def test_empty_source_is_rejected(self):
        valid, reason = generate_index._translation_quality(
            "", "输入内容为空。请提供需要翻译的英文摘要文本。"
        )
        self.assertFalse(valid)
        self.assertIn("原文为空", reason)

    def test_dropped_independent_percent_fails(self):
        # 回归 #405：源文 60% 出现两次（范围端点 + 独立 dropout），
        # 译文只保留一次时必须判遗漏。
        source = "accuracy rose from 60% to 80%, with 60% dropout in training"
        translated = "新方法将准确率从 60% 提升到 80%，训练效果显著"
        valid, reason = generate_index._translation_quality(source, translated)
        self.assertFalse(valid, reason)
        self.assertIn("percent:60", reason)

    def test_all_percents_kept_passes(self):
        source = "accuracy rose from 60% to 80%, with 60% dropout in training"
        translated = "准确率从 60% 提升到 80%，训练时 dropout 为 60%，效果显著"
        valid, reason = generate_index._translation_quality(source, translated)
        self.assertTrue(valid, reason)


class ProviderErrorTextTests(unittest.TestCase):
    QUOTA_TEXT = (
        "近 7 天免费额度已用完，预计11月28日 08:31 恢复。开通订阅畅享更多额度。\n\n"
        "[开通豆包订阅](https://www.doubao.com/member/subscription"
        "?com_quota_cost_fk_id=1153121480141652732&custom_tracing_extra=%7B%7D)"
    )

    def test_quota_text_is_provider_error(self):
        self.assertTrue(generate_index._looks_like_provider_error(self.QUOTA_TEXT))

    def test_english_quota_text_is_provider_error(self):
        self.assertTrue(generate_index._looks_like_provider_error(
            "Quota exceeded. Please upgrade your plan or try again later."))

    def test_project_url_is_not_provider_error(self):
        # 回归：正常译文常带项目链接（GitHub/HuggingFace），不得误判。
        text = "我们开源了代码，详见 https://github.com/example/repo，实验效果显著提升"
        self.assertFalse(generate_index._looks_like_provider_error(text))

    def test_quota_text_fails_quality_gate(self):
        # 回归 #399/#403：额度耗尽提示有足量中文，旧门直接放行。
        source = "We propose a new method for cryo-EM reconstruction from noisy images."
        valid, reason = generate_index._translation_quality(source, self.QUOTA_TEXT)
        self.assertFalse(valid)
        self.assertIn("供应商错误提示", reason)

    def test_load_translations_clears_provider_error(self):
        # 回归 #403：缓存读取侧不得裸信，错误文本读入即清空待重译。
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "translations.json"
            cache.write_text(json.dumps({
                "2611.25525v1": {
                    "title_zh": "基于去噪图像矩的从头 cryo-EM 重建",
                    "abstract_zh": self.QUOTA_TEXT,
                    "translation_version": 2,
                },
                "2611.23765v1": {
                    "title_zh": "正常标题翻译内容测试",
                    "abstract_zh": "这是一段正常的中文摘要翻译内容，用于测试缓存加载逻辑是否正常工作。",
                    "translation_version": 2,
                },
            }, ensure_ascii=False), encoding="utf-8")
            with patch.object(generate_index, "TRANSLATIONS_CACHE", cache):
                data = generate_index._load_translations()
        self.assertEqual(data["2611.25525v1"]["abstract_zh"], "")
        self.assertEqual(data["2611.25525v1"]["title_zh"], "基于去噪图像矩的从头 cryo-EM 重建")
        self.assertTrue(data["2611.23765v1"]["abstract_zh"].startswith("这是一段正常"))


if __name__ == "__main__":
    unittest.main()
