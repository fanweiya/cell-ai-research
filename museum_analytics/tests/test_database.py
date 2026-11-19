import unittest
from datetime import date, datetime

from museum.database import MuseumDatabase
from museum.models import Artwork, ArtworkView, Exhibition, Ticket, Visit, Visitor


def build_database() -> MuseumDatabase:
    db = MuseumDatabase()
    db.add_visitor(Visitor("v1", "Ada Bauer", 34, "female", "NY", False, date(2026, 3, 1)))
    db.add_visitor(Visitor("v2", "Omar Haddad", 70, "male", "CA", True, date(2025, 6, 1)))
    db.add_exhibition(Exhibition("e1", "Show", "Curator", "theme", date(2026, 3, 1), date(2026, 3, 31), 10))
    db.add_exhibition(Exhibition("e2", "Other", "Curator", "theme", date(2026, 4, 1), date(2026, 4, 30), 5))
    db.add_artwork(Artwork("a1", "Mask", "Unknown", -600, "bronze", "e1"))
    db.add_artwork(Artwork("a2", "Boat", "Unknown", -1900, "wood", "e2"))
    db.add_ticket(Ticket("t1", "v1", "e1", date(2026, 2, 28), date(2026, 3, 2), "adult", 20.0))
    db.add_ticket(Ticket("t2", "v2", "e2", date(2026, 3, 30), date(2026, 4, 1), "senior", 15.0))
    db.add_visit(Visit("x1", "v1", "e1", "t1", datetime(2026, 3, 2, 10, 0), datetime(2026, 3, 2, 11, 0)))
    db.add_visit(Visit("x2", "v2", "e2", "t2", datetime(2026, 4, 1, 12, 0), datetime(2026, 4, 1, 12, 30)))
    db.add_view(ArtworkView("w1", "v1", "a1", datetime(2026, 3, 2, 10, 30), 40, True))
    db.add_view(ArtworkView("w2", "v2", "a2", datetime(2026, 4, 1, 12, 10), 20, False))
    return db


class MuseumDatabaseTest(unittest.TestCase):
    def test_counts_and_lookups(self) -> None:
        db = build_database()
        self.assertEqual(len(db.visitors), 2)
        self.assertEqual(len(db.exhibitions), 2)
        self.assertEqual(len(db.artworks), 2)
        self.assertEqual(len(db.tickets), 2)
        self.assertEqual(len(db.visits), 2)
        self.assertEqual(len(db.views), 2)
        self.assertEqual(db.visitor("v1").name, "Ada Bauer")
        self.assertEqual(db.exhibition("e1").title, "Show")
        self.assertEqual(db.artwork("a1").title, "Mask")
        self.assertEqual(db.ticket("t1").ticket_type, "adult")

    def test_unknown_lookups_raise(self) -> None:
        db = build_database()
        with self.assertRaises(KeyError):
            db.visitor("missing")
        with self.assertRaises(KeyError):
            db.exhibition("missing")
        with self.assertRaises(KeyError):
            db.artwork("missing")
        with self.assertRaises(KeyError):
            db.ticket("missing")

    def test_duplicate_ids_are_rejected(self) -> None:
        db = build_database()
        visitor = Visitor("v1", "Ada Bauer", 34, "female", "NY", False, date(2026, 3, 1))
        with self.assertRaises(ValueError):
            db.add_visitor(visitor)

    def test_foreign_keys_are_checked(self) -> None:
        db = build_database()
        with self.assertRaises(KeyError):
            db.add_artwork(Artwork("a3", "Vase", "Unknown", 100, "clay", "missing"))
        with self.assertRaises(KeyError):
            db.add_ticket(Ticket("t3", "missing", "e1", date(2026, 3, 1), date(2026, 3, 2), "adult", 20.0))
        with self.assertRaises(KeyError):
            db.add_visit(
                Visit("x3", "v1", "e1", "missing", datetime(2026, 3, 2, 10, 0), datetime(2026, 3, 2, 11, 0))
            )
        with self.assertRaises(KeyError):
            db.add_view(ArtworkView("w3", "v1", "missing", datetime(2026, 3, 2, 10, 0), 10, False))

    def test_date_filters_are_inclusive(self) -> None:
        db = build_database()
        self.assertEqual([ticket.ticket_id for ticket in db.tickets_between(date(2026, 3, 2), date(2026, 3, 2))], ["t1"])
        self.assertEqual([visit.visit_id for visit in db.visits_between(date(2026, 4, 1), None)], ["x2"])
        self.assertEqual([view.view_id for view in db.views_between(None, date(2026, 3, 5))], ["w1"])
        self.assertEqual(db.tickets_between(date(2026, 3, 3), date(2026, 3, 31)), ())

    def test_artworks_in_exhibition(self) -> None:
        db = build_database()
        self.assertEqual([artwork.artwork_id for artwork in db.artworks_in("e1")], ["a1"])
        with self.assertRaises(KeyError):
            db.artworks_in("missing")

    def test_empty_database_filters_return_nothing(self) -> None:
        db = MuseumDatabase()
        self.assertEqual(db.tickets_between(), ())
        self.assertEqual(db.visits_between(), ())
        self.assertEqual(db.views_between(), ())


if __name__ == "__main__":
    unittest.main()
