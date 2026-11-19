import unittest
from datetime import date, datetime

from museum.models import Artwork, ArtworkView, Exhibition, Ticket, Visit, Visitor, age_band


class VisitorTest(unittest.TestCase):
    def test_age_band_edges(self) -> None:
        self.assertEqual(age_band(0), "0-17")
        self.assertEqual(age_band(17), "0-17")
        self.assertEqual(age_band(18), "18-24")
        self.assertEqual(age_band(24), "18-24")
        self.assertEqual(age_band(25), "25-34")
        self.assertEqual(age_band(64), "55-64")
        self.assertEqual(age_band(65), "65+")
        self.assertEqual(age_band(120), "65+")

    def test_age_band_rejects_unknown_age(self) -> None:
        with self.assertRaises(ValueError):
            age_band(-1)
        with self.assertRaises(ValueError):
            age_band(121)

    def test_valid_visitor(self) -> None:
        visitor = Visitor("v1", "Ada Bauer", 34, "female", "NY", False, date(2026, 3, 1))
        self.assertEqual(visitor.age_band, "25-34")

    def test_rejects_bad_fields(self) -> None:
        with self.assertRaises(ValueError):
            Visitor("", "Ada", 34, "female", "NY", False, date(2026, 3, 1))
        with self.assertRaises(ValueError):
            Visitor("v1", "  ", 34, "female", "NY", False, date(2026, 3, 1))
        with self.assertRaises(ValueError):
            Visitor("v1", "Ada", -1, "female", "NY", False, date(2026, 3, 1))
        with self.assertRaises(ValueError):
            Visitor("v1", "Ada", 121, "female", "NY", False, date(2026, 3, 1))
        with self.assertRaises(ValueError):
            Visitor("v1", "Ada", 34, "robot", "NY", False, date(2026, 3, 1))
        with self.assertRaises(ValueError):
            Visitor("v1", "Ada", 34, "female", "NY", False, datetime(2026, 3, 1, 9, 0))


class ExhibitionTest(unittest.TestCase):
    def test_duration_counts_both_ends(self) -> None:
        exhibition = Exhibition("e1", "Show", "Curator", "theme", date(2026, 3, 1), date(2026, 3, 31), 10)
        self.assertEqual(exhibition.duration_days, 31)

    def test_rejects_reversed_dates_and_empty_capacity(self) -> None:
        with self.assertRaises(ValueError):
            Exhibition("e1", "Show", "Curator", "theme", date(2026, 3, 31), date(2026, 3, 1), 10)
        with self.assertRaises(ValueError):
            Exhibition("e1", "Show", "Curator", "theme", date(2026, 3, 1), date(2026, 3, 31), 0)


class ArtworkTest(unittest.TestCase):
    def test_rejects_year_outside_catalogue_range(self) -> None:
        with self.assertRaises(ValueError):
            Artwork("a1", "Mask", "Unknown", -6000, "bronze", "e1")
        with self.assertRaises(ValueError):
            Artwork("a1", "Mask", "Unknown", 2200, "bronze", "e1")


class TicketTest(unittest.TestCase):
    def test_revenue_math(self) -> None:
        ticket = Ticket("t1", "v1", "e1", date(2026, 3, 1), date(2026, 3, 2), "adult", 20.0, 5.0, 3)
        self.assertEqual(ticket.gross_revenue, 60.0)
        self.assertEqual(ticket.discount_total, 15.0)
        self.assertEqual(ticket.net_revenue, 45.0)

    def test_refund_removes_net_revenue(self) -> None:
        ticket = Ticket("t1", "v1", "e1", date(2026, 3, 1), date(2026, 3, 2), "adult", 20.0, 0.0, 1, True)
        self.assertEqual(ticket.net_revenue, 0.0)
        self.assertEqual(ticket.gross_revenue, 20.0)

    def test_rejects_invalid_values(self) -> None:
        with self.assertRaises(ValueError):
            Ticket("t1", "v1", "e1", date(2026, 3, 2), date(2026, 3, 1), "adult", 20.0)
        with self.assertRaises(ValueError):
            Ticket("t1", "v1", "e1", date(2026, 3, 1), date(2026, 3, 2), "vip", 20.0)
        with self.assertRaises(ValueError):
            Ticket("t1", "v1", "e1", date(2026, 3, 1), date(2026, 3, 2), "adult", 20.0, 21.0)
        with self.assertRaises(ValueError):
            Ticket("t1", "v1", "e1", date(2026, 3, 1), date(2026, 3, 2), "adult", 20.0, 0.0, 0)


class VisitTest(unittest.TestCase):
    def test_duration_minutes(self) -> None:
        visit = Visit("x", "v1", "e1", "t1", datetime(2026, 3, 2, 10, 0), datetime(2026, 3, 2, 11, 30))
        self.assertEqual(visit.duration_minutes, 90.0)

    def test_rejects_empty_interval(self) -> None:
        with self.assertRaises(ValueError):
            Visit("x", "v1", "e1", "t1", datetime(2026, 3, 2, 10, 0), datetime(2026, 3, 2, 10, 0))


class ArtworkViewTest(unittest.TestCase):
    def test_rejects_negative_dwell(self) -> None:
        with self.assertRaises(ValueError):
            ArtworkView("w1", "v1", "a1", datetime(2026, 3, 2, 10, 0), -5, False)


if __name__ == "__main__":
    unittest.main()
