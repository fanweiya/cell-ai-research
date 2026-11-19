import unittest

from museum import stats


class MeanMedianTest(unittest.TestCase):
    def test_mean(self) -> None:
        self.assertEqual(stats.mean([1, 2, 3, 4]), 2.5)
        self.assertEqual(stats.mean([7]), 7.0)
        with self.assertRaises(ValueError):
            stats.mean([])

    def test_median_odd_and_even(self) -> None:
        self.assertEqual(stats.median([5, 1, 3]), 3.0)
        self.assertEqual(stats.median([4, 1, 3, 2]), 2.5)
        with self.assertRaises(ValueError):
            stats.median([])


class PercentileTest(unittest.TestCase):
    def test_interpolates_between_ranks(self) -> None:
        values = [0, 10, 20, 30, 40]
        self.assertEqual(stats.percentile(values, 0.0), 0.0)
        self.assertEqual(stats.percentile(values, 0.5), 20.0)
        self.assertEqual(stats.percentile(values, 0.9), 36.0)
        self.assertEqual(stats.percentile(values, 1.0), 40.0)

    def test_single_value(self) -> None:
        self.assertEqual(stats.percentile([7], 0.25), 7.0)

    def test_rejects_bad_fraction_and_empty_input(self) -> None:
        with self.assertRaises(ValueError):
            stats.percentile([1, 2], 1.5)
        with self.assertRaises(ValueError):
            stats.percentile([], 0.5)


class StdevTest(unittest.TestCase):
    def test_sample_stdev(self) -> None:
        self.assertAlmostEqual(stats.stdev([2, 4, 4, 4, 5, 5, 7, 9]), 2.13809, places=4)

    def test_single_value_has_zero_spread(self) -> None:
        self.assertEqual(stats.stdev([3]), 0.0)

    def test_empty_input_raises(self) -> None:
        with self.assertRaises(ValueError):
            stats.stdev([])


class ModeTest(unittest.TestCase):
    def test_mode_breaks_ties_alphabetically(self) -> None:
        self.assertEqual(stats.mode(["b", "a", "a", "b"]), "a")
        self.assertEqual(stats.mode(["x", "y", "y"]), "y")

    def test_empty_input_raises(self) -> None:
        with self.assertRaises(ValueError):
            stats.mode([])


class TopLabelsTest(unittest.TestCase):
    def test_counts_and_orders(self) -> None:
        self.assertEqual(stats.top_labels(["NY", "CA", "NY", "TX", "CA"], 2), [("CA", 2), ("NY", 2)])
        self.assertEqual(stats.top_labels([], 3), [])

    def test_rejects_non_positive_limit(self) -> None:
        with self.assertRaises(ValueError):
            stats.top_labels(["NY"], 0)


class SafeRatioTest(unittest.TestCase):
    def test_zero_denominator_returns_zero(self) -> None:
        self.assertEqual(stats.safe_ratio(5, 0), 0.0)
        self.assertEqual(stats.safe_ratio(5, 10), 0.5)


if __name__ == "__main__":
    unittest.main()
