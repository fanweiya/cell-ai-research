import unittest
from datetime import date, datetime

from museum.analytics import MuseumAnalytics
from museum.database import MuseumDatabase
from museum.models import Artwork, ArtworkView, Exhibition, Ticket, Visit, Visitor

MARCH_START = date(2026, 3, 1)
MARCH_END = date(2026, 3, 31)


def build_fixture() -> MuseumDatabase:
    db = MuseumDatabase()
    db.add_visitor(Visitor("v1", "Ada Bauer", 30, "female", "NY", False, date(2026, 3, 2)))
    db.add_visitor(Visitor("v2", "Omar Haddad", 70, "male", "CA", True, date(2025, 6, 1)))
    db.add_visitor(Visitor("v3", "Kim Ito", 12, "unknown", "NY", False, date(2026, 3, 10)))
    db.add_visitor(Visitor("v4", "Bea Lopez", 30, "female", "TX", False, date(2026, 3, 11)))
    db.add_exhibition(Exhibition("e1", "Show", "Curator", "theme", MARCH_START, MARCH_END, 10))
    db.add_exhibition(Exhibition("e2", "Other", "Curator", "theme", date(2026, 3, 5), date(2026, 4, 15), 4))
    db.add_artwork(Artwork("a1", "Mask", "Unknown", -600, "bronze", "e1"))
    db.add_artwork(Artwork("a2", "Boat", "Unknown", -1900, "wood", "e1"))
    db.add_ticket(Ticket("t1", "v1", "e1", date(2026, 3, 1), date(2026, 3, 2), "adult", 20.0, 0.0, 2))
    db.add_ticket(Ticket("t2", "v2", "e1", date(2026, 3, 1), date(2026, 3, 3), "member", 16.0))
    db.add_ticket(Ticket("t3", "v3", "e2", date(2026, 3, 8), date(2026, 3, 10), "comp", 0.0))
    db.add_ticket(Ticket("t4", "v4", "e2", date(2026, 3, 9), date(2026, 3, 11), "adult", 20.0, 0.0, 1, True))
    db.add_ticket(Ticket("t5", "v1", "e1", date(2026, 3, 18), date(2026, 3, 20), "adult", 20.0, 5.0))
    db.add_visit(Visit("x1", "v1", "e1", "t1", datetime(2026, 3, 2, 10, 0), datetime(2026, 3, 2, 11, 0)))
    db.add_visit(Visit("x2", "v1", "e1", "t5", datetime(2026, 3, 20, 14, 0), datetime(2026, 3, 20, 15, 30)))
    db.add_visit(Visit("x3", "v2", "e1", "t2", datetime(2026, 3, 3, 11, 0), datetime(2026, 3, 3, 12, 0)))
    db.add_visit(Visit("x4", "v3", "e2", "t3", datetime(2026, 3, 10, 10, 0), datetime(2026, 3, 10, 10, 30)))
    db.add_view(ArtworkView("w1", "v1", "a1", datetime(2026, 3, 2, 10, 20), 30, True))
    db.add_view(ArtworkView("w2", "v2", "a1", datetime(2026, 3, 3, 11, 10), 70, False))
    db.add_view(ArtworkView("w3", "v1", "a1", datetime(2026, 3, 20, 14, 10), 50, False))
    db.add_view(ArtworkView("w4", "v3", "a2", datetime(2026, 3, 10, 10, 10), 10, False))
    return db


class RevenueTest(unittest.TestCase):
    def setUp(self) -> None:
        self.analytics = MuseumAnalytics(build_fixture())

    def test_totals(self) -> None:
        summary = self.analytics.revenue_summary(MARCH_START, MARCH_END)
        self.assertEqual(summary.ticket_count, 5)
        self.assertEqual(summary.admissions, 5)
        self.assertEqual(summary.gross_revenue, 96.0)
        self.assertEqual(summary.discount_total, 5.0)
        self.assertEqual(summary.refund_total, 20.0)
        self.assertEqual(summary.net_revenue, 71.0)
        self.assertEqual(summary.average_price, 14.2)
        self.assertAlmostEqual(summary.member_share, 16.0 / 71.0, places=4)

    def test_breakdowns(self) -> None:
        summary = self.analytics.revenue_summary(MARCH_START, MARCH_END)
        self.assertEqual(summary.by_exhibition, {"e1": 71.0, "e2": 0.0})
        self.assertEqual(summary.by_ticket_type, {"adult": 55.0, "member": 16.0, "comp": 0.0})
        self.assertEqual(summary.by_month, {"2026-03": 71.0})

    def test_window_is_inclusive(self) -> None:
        summary = self.analytics.revenue_summary(date(2026, 3, 3), date(2026, 3, 10))
        self.assertEqual(summary.ticket_count, 2)
        self.assertEqual(summary.net_revenue, 16.0)
        self.assertEqual(summary.admissions, 2)

    def test_empty_window(self) -> None:
        summary = self.analytics.revenue_summary(date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(summary.ticket_count, 0)
        self.assertEqual(summary.net_revenue, 0.0)
        self.assertEqual(summary.average_price, 0.0)
        self.assertEqual(summary.by_exhibition, {})


class AttendanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.analytics = MuseumAnalytics(build_fixture())

    def test_counts_and_dwell(self) -> None:
        summary = self.analytics.attendance_summary(MARCH_START, MARCH_END)
        self.assertEqual(summary.total_visits, 4)
        self.assertEqual(summary.unique_visitors, 3)
        self.assertEqual(summary.repeat_visitors, 1)
        self.assertAlmostEqual(summary.repeat_visitor_rate, 1 / 3, places=4)
        self.assertEqual(summary.average_dwell_minutes, 60.0)
        self.assertEqual(summary.median_dwell_minutes, 60.0)
        self.assertEqual(summary.by_exhibition, {"e1": 3, "e2": 1})

    def test_peak_hours(self) -> None:
        summary = self.analytics.attendance_summary(MARCH_START, MARCH_END)
        self.assertEqual(summary.peak_hours, [(10, 2), (11, 1), (14, 1)])

    def test_capacity_utilization_uses_open_days(self) -> None:
        summary = self.analytics.attendance_summary(MARCH_START, MARCH_END)
        self.assertAlmostEqual(summary.capacity_utilization["e1"], 4 / 310, places=4)
        self.assertAlmostEqual(summary.capacity_utilization["e2"], 1 / 108, places=4)

    def test_empty_window(self) -> None:
        summary = self.analytics.attendance_summary(date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(summary.total_visits, 0)
        self.assertEqual(summary.average_dwell_minutes, 0.0)
        self.assertEqual(summary.peak_hours, [])


class DemographicsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.analytics = MuseumAnalytics(build_fixture())

    def test_age_and_gender(self) -> None:
        summary = self.analytics.demographic_summary(MARCH_START, MARCH_END)
        self.assertEqual(summary.unique_visitors, 3)
        self.assertEqual(summary.age_bands, {"0-17": 1, "25-34": 1, "65+": 1})
        self.assertAlmostEqual(summary.age_band_share["0-17"], 1 / 3, places=4)
        self.assertAlmostEqual(summary.average_age, 37.33, places=2)
        self.assertEqual(summary.median_age, 30.0)
        self.assertEqual(summary.gender, {"female": 1, "male": 1, "unknown": 1})

    def test_regions_members_and_first_time(self) -> None:
        summary = self.analytics.demographic_summary(MARCH_START, MARCH_END)
        self.assertEqual(summary.top_regions, [("NY", 2), ("CA", 1)])
        self.assertAlmostEqual(summary.member_share, 1 / 3, places=4)
        self.assertAlmostEqual(summary.first_time_share, 2 / 3, places=4)

    def test_empty_window(self) -> None:
        summary = self.analytics.demographic_summary(date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(summary.unique_visitors, 0)
        self.assertEqual(summary.age_bands, {})
        self.assertEqual(summary.average_age, 0.0)


class ExhibitionTest(unittest.TestCase):
    def test_performance_ranks_by_revenue(self) -> None:
        analytics = MuseumAnalytics(build_fixture())
        rows = analytics.exhibition_performance(MARCH_START, MARCH_END)
        self.assertEqual([row.exhibition_id for row in rows], ["e1", "e2"])
        first, second = rows
        self.assertEqual(first.tickets, 3)
        self.assertEqual(first.admissions, 4)
        self.assertEqual(first.net_revenue, 71.0)
        self.assertEqual(first.revenue_share, 1.0)
        self.assertEqual(first.average_dwell_minutes, 70.0)
        self.assertEqual(second.tickets, 2)
        self.assertEqual(second.admissions, 1)
        self.assertEqual(second.net_revenue, 0.0)
        self.assertEqual(second.revenue_share, 0.0)
        self.assertEqual(second.average_dwell_minutes, 30.0)


class ArtworkPopularityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.analytics = MuseumAnalytics(build_fixture())

    def test_default_metric_is_views(self) -> None:
        rows = self.analytics.popular_artworks(MARCH_START, MARCH_END)
        self.assertEqual([row.artwork_id for row in rows], ["a1", "a2"])
        self.assertEqual(rows[0].views, 3)
        self.assertEqual(rows[0].unique_viewers, 2)
        self.assertEqual(rows[0].like_rate, 0.3333)
        self.assertEqual(rows[0].mean_dwell_seconds, 50.0)

    def test_metric_changes_ranking(self) -> None:
        by_dwell = self.analytics.popular_artworks(MARCH_START, MARCH_END, metric="dwell", min_views=2)
        self.assertEqual([row.artwork_id for row in by_dwell], ["a1"])
        self.assertEqual(by_dwell[0].metric_value, 50.0)
        by_likes = self.analytics.popular_artworks(MARCH_START, MARCH_END, metric="likes")
        self.assertEqual(by_likes[0].metric_value, 1.0)
        by_engagement = self.analytics.popular_artworks(MARCH_START, MARCH_END, metric="engagement")
        self.assertEqual(by_engagement[0].metric_value, 0.3333)

    def test_rejects_unknown_metric_and_bad_limits(self) -> None:
        with self.assertRaises(ValueError):
            self.analytics.popular_artworks(MARCH_START, MARCH_END, metric="clicks")
        with self.assertRaises(ValueError):
            self.analytics.popular_artworks(MARCH_START, MARCH_END, top_n=0)
        with self.assertRaises(ValueError):
            self.analytics.popular_artworks(MARCH_START, MARCH_END, min_views=-1)


class VisitorSpendingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.analytics = MuseumAnalytics(build_fixture())

    def test_top_visitors_excludes_refunds(self) -> None:
        rows = self.analytics.top_visitors(MARCH_START, MARCH_END)
        self.assertEqual([row.visitor_id for row in rows], ["v1", "v2", "v3"])
        self.assertEqual(rows[0].net_spend, 55.0)
        self.assertEqual(rows[0].visits, 2)
        self.assertEqual(rows[0].age_band, "25-34")
        self.assertEqual(rows[0].region, "NY")

    def test_top_visitors_respects_limit(self) -> None:
        rows = self.analytics.top_visitors(MARCH_START, MARCH_END, limit=1)
        self.assertEqual(len(rows), 1)
        with self.assertRaises(ValueError):
            self.analytics.top_visitors(MARCH_START, MARCH_END, limit=0)

    def test_spending_by_age_band(self) -> None:
        rows = self.analytics.spending_by_age_band(MARCH_START, MARCH_END)
        self.assertEqual([row.label for row in rows], ["25-34", "65+", "0-17"])
        self.assertEqual(rows[0].net_spend, 55.0)
        self.assertEqual(rows[0].average_spend, 55.0)


class ReportTest(unittest.TestCase):
    def test_full_report_shape(self) -> None:
        analytics = MuseumAnalytics(build_fixture())
        report = analytics.full_report(MARCH_START, MARCH_END)
        self.assertEqual(report["window"], {"start": "2026-03-01", "end": "2026-03-31"})
        self.assertEqual(report["revenue"]["net_revenue"], 71.0)
        self.assertEqual(report["attendance"]["total_visits"], 4)
        self.assertEqual(len(report["exhibitions"]), 2)
        self.assertEqual(report["popular_artworks"][0]["artwork_id"], "a1")
        self.assertIn("generated_at", report)

    def test_rejects_reversed_window(self) -> None:
        analytics = MuseumAnalytics(build_fixture())
        with self.assertRaises(ValueError):
            analytics.revenue_summary(MARCH_END, MARCH_START)
        with self.assertRaises(ValueError):
            analytics.full_report(MARCH_END, MARCH_START)


class EmptyDatabaseTest(unittest.TestCase):
    def test_summaries_are_zero_without_records(self) -> None:
        analytics = MuseumAnalytics(MuseumDatabase())
        revenue = analytics.revenue_summary()
        attendance = analytics.attendance_summary()
        demographics = analytics.demographic_summary()
        self.assertEqual(revenue.net_revenue, 0.0)
        self.assertEqual(attendance.total_visits, 0)
        self.assertEqual(demographics.unique_visitors, 0)
        self.assertEqual(analytics.popular_artworks(), [])
        self.assertEqual(analytics.top_visitors(), [])
        self.assertEqual(analytics.spending_by_age_band(), [])


if __name__ == "__main__":
    unittest.main()
