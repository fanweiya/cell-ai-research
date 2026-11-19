from datetime import date, datetime, time, timedelta
from random import Random

from museum.database import MuseumDatabase
from museum.models import Artwork, ArtworkView, Exhibition, Ticket, Visit, Visitor

WINDOW_START = date(2026, 3, 1)
WINDOW_END = date(2026, 5, 31)

GIVEN_NAMES = (
    "Ada", "Bruno", "Clara", "Diego", "Elena", "Farid", "Greta", "Hana", "Ivan", "Jonas",
    "Keiko", "Lena", "Mateo", "Nadia", "Omar", "Priya", "Quinn", "Rosa", "Samir", "Tara",
)
FAMILY_NAMES = (
    "Alvarez", "Bauer", "Chen", "Dubois", "Eriksen", "Fischer", "Gupta", "Hoffmann", "Ito",
    "Jansen", "Keller", "Lopez", "Moreau", "Novak", "Okafor", "Petrov", "Rossi", "Silva",
    "Tanaka", "Weber",
)
REGIONS = ("NY", "CA", "TX", "MA", "IL", "PA", "FL", "WA")

EXHIBITIONS = (
    {
        "exhibition_id": "exh-light",
        "title": "Light on Canvas",
        "curator": "Marta Klein",
        "theme": "impressionism",
        "start_date": date(2026, 1, 15),
        "end_date": date(2026, 6, 30),
        "daily_capacity": 60,
    },
    {
        "exhibition_id": "exh-nile",
        "title": "Along the Nile",
        "curator": "Yusuf Haddad",
        "theme": "ancient",
        "start_date": date(2026, 2, 1),
        "end_date": date(2026, 5, 15),
        "daily_capacity": 55,
    },
    {
        "exhibition_id": "exh-now",
        "title": "Now and Then",
        "curator": "Ines Duarte",
        "theme": "contemporary",
        "start_date": date(2026, 3, 1),
        "end_date": date(2026, 8, 31),
        "daily_capacity": 50,
    },
)

ARTWORKS = (
    ("exh-light", "Morning on the River", "Camille Bernard", 1874, "oil on canvas"),
    ("exh-light", "Two Women at a Window", "Camille Bernard", 1878, "oil on canvas"),
    ("exh-light", "Garden in June", "Edith Marlow", 1881, "oil on canvas"),
    ("exh-light", "The Red Umbrella", "Edith Marlow", 1883, "pastel on paper"),
    ("exh-light", "Boats at Low Tide", "Paul Vasseur", 1876, "oil on canvas"),
    ("exh-light", "Winter Field", "Paul Vasseur", 1880, "oil on canvas"),
    ("exh-light", "Portrait of a Reader", "Anna Lindqvist", 1885, "oil on canvas"),
    ("exh-light", "Terrace at Dusk", "Anna Lindqvist", 1887, "oil on canvas"),
    ("exh-light", "Study of Hands", "Henri Roux", 1879, "charcoal on paper"),
    ("exh-light", "Market Day", "Henri Roux", 1882, "oil on canvas"),
    ("exh-nile", "Funerary Mask", "Unknown, Dynasty XVIII", -1350, "gilded wood"),
    ("exh-nile", "Painted Coffin Panel", "Unknown, Dynasty XXI", -950, "painted wood"),
    ("exh-nile", "Bronze Cat", "Unknown, Late Period", -600, "bronze"),
    ("exh-nile", "Limestone Relief", "Unknown, Dynasty V", -2400, "limestone"),
    ("exh-nile", "Scarab Seal", "Unknown, Middle Kingdom", -1800, "steatite"),
    ("exh-nile", "Canopic Jar", "Unknown, New Kingdom", -1300, "alabaster"),
    ("exh-nile", "Model Boat", "Unknown, Middle Kingdom", -1900, "wood"),
    ("exh-nile", "Faience Amulet", "Unknown, Late Period", -550, "faience"),
    ("exh-nile", "Papyrus Fragment", "Unknown, Ptolemaic", -200, "papyrus"),
    ("exh-nile", "Painted Vessel", "Unknown, Predynastic", -3500, "terracotta"),
    ("exh-now", "Grid Study No. 4", "Rina Okafor", 2019, "acrylic on linen"),
    ("exh-now", "Quiet Room", "Rina Okafor", 2021, "mixed media"),
    ("exh-now", "Signal", "Tomas Vega", 2018, "video, 12 min"),
    ("exh-now", "Blue Interval", "Tomas Vega", 2020, "oil on canvas"),
    ("exh-now", "Folded City", "Mei Lin", 2022, "paper and steel"),
    ("exh-now", "Night Shift", "Mei Lin", 2023, "photographic print"),
    ("exh-now", "Counterweight", "Jonas Brandt", 2017, "steel"),
    ("exh-now", "Soft Machine", "Jonas Brandt", 2021, "textile and motors"),
    ("exh-now", "Everyday Noise", "Sara Haddad", 2020, "sound installation"),
    ("exh-now", "After the Rain", "Sara Haddad", 2024, "oil on canvas"),
)

TICKET_PRICES = {
    "adult": 28.0,
    "child": 0.0,
    "senior": 20.0,
    "student": 15.0,
    "member": 16.0,
    "group": 22.0,
    "comp": 0.0,
}


def _ticket_type(age: int, is_member: bool, group_size: int, rng: Random) -> str:
    if is_member:
        return "member"
    if age < 18:
        return "child"
    if age >= 65:
        return "senior"
    if group_size > 1:
        return "group"
    if 18 <= age <= 26 and rng.random() < 0.6:
        return "student"
    return "adult"


def _active_exhibitions(day: date) -> list[dict]:
    return [row for row in EXHIBITIONS if row["start_date"] <= day <= row["end_date"]]


def build_demo_database(visitor_count: int = 2500, seed: int = 20260301) -> MuseumDatabase:
    """Builds a deterministic sample dataset covering March to May 2026.

    The dataset is generated for demonstrations and tests: 2500 visitors by
    default, three exhibitions, thirty catalogued works, repeated visits,
    occasional refunds and a few group tickets.

    Args:
        visitor_count: Number of visitors to generate.
        seed: Seed for the pseudo random generator.

    Returns:
        A store holding the generated records.

    Raises:
        ValueError: If ``visitor_count`` is not positive.
    """
    if visitor_count < 1:
        raise ValueError("visitor_count must be positive")
    rng = Random(seed)
    db = MuseumDatabase()
    for row in EXHIBITIONS:
        db.add_exhibition(Exhibition(**row))
    artwork_ids: dict[str, list[str]] = {row["exhibition_id"]: [] for row in EXHIBITIONS}
    for index, (exhibition_id, title, artist, year, medium) in enumerate(ARTWORKS, start=1):
        artwork_id = f"art-{index:03d}"
        db.add_artwork(Artwork(artwork_id, title, artist, year, medium, exhibition_id))
        artwork_ids[exhibition_id].append(artwork_id)

    window_days = (WINDOW_END - WINDOW_START).days + 1
    for number in range(1, visitor_count + 1):
        visitor_id = f"v{number:04d}"
        name = f"{rng.choice(GIVEN_NAMES)} {rng.choice(FAMILY_NAMES)}"
        age = min(88, max(6, int(rng.gauss(42, 18))))
        gender = rng.choices(("female", "male", "nonbinary"), weights=(0.52, 0.45, 0.03))[0]
        region = rng.choices(REGIONS, weights=(0.28, 0.18, 0.12, 0.1, 0.09, 0.08, 0.08, 0.07))[0]
        is_member = rng.random() < 0.18

        visit_count = rng.choices((1, 2, 3, 4), weights=(0.55, 0.25, 0.13, 0.07))[0]
        days = sorted(rng.sample(range(window_days), visit_count))
        schedule = []
        for offset in days:
            day = WINDOW_START + timedelta(days=offset)
            exhibition = rng.choice(_active_exhibitions(day))
            group_size = 1
            if rng.random() < 0.06:
                group_size = rng.randint(2, 4)
            schedule.append((day, exhibition, group_size))

        first_visit = schedule[0][0] if rng.random() < 0.7 else date(2025, rng.randint(2, 11), rng.randint(1, 27))
        db.add_visitor(Visitor(visitor_id, name, age, gender, region, is_member, first_visit))

        for visit_number, (day, exhibition, group_size) in enumerate(schedule, start=1):
            ticket_id = f"t{number:04d}-{visit_number}"
            ticket_type = _ticket_type(age, is_member, group_size, rng)
            price = TICKET_PRICES[ticket_type]
            discount = 0.0
            if ticket_type in ("adult", "senior", "student") and rng.random() < 0.12:
                discount = round(price * rng.choice((0.1, 0.15, 0.25)), 2)
            refunded = rng.random() < 0.03
            purchase_date = day - timedelta(days=rng.randint(0, 21))
            db.add_ticket(
                Ticket(
                    ticket_id=ticket_id,
                    visitor_id=visitor_id,
                    exhibition_id=exhibition["exhibition_id"],
                    purchase_date=purchase_date,
                    visit_date=day,
                    ticket_type=ticket_type,
                    list_price=price,
                    discount=discount,
                    group_size=group_size,
                    refunded=refunded,
                )
            )
            if refunded:
                continue
            entry_hour = rng.choices(range(10, 18), weights=(6, 8, 10, 12, 11, 8, 5, 3))[0]
            entry = datetime.combine(day, time(entry_hour, rng.randint(0, 59)))
            exit_ = entry + timedelta(minutes=rng.randint(20, 120))
            visit_id = f"visit-{ticket_id}"
            db.add_visit(Visit(visit_id, visitor_id, exhibition["exhibition_id"], ticket_id, entry, exit_))
            for view_number in range(rng.randint(3, 8)):
                artwork_id = rng.choice(artwork_ids[exhibition["exhibition_id"]])
                dwell = rng.randint(5, 150)
                moment = entry + timedelta(seconds=rng.randint(60, max(120, int((exit_ - entry).total_seconds()) - 60)))
                liked = rng.random() < (0.28 if dwell >= 60 else 0.08)
                db.add_view(
                    ArtworkView(
                        view_id=f"view-{visit_id}-{view_number}",
                        visitor_id=visitor_id,
                        artwork_id=artwork_id,
                        timestamp=moment,
                        dwell_seconds=dwell,
                        liked=liked,
                    )
                )
    return db
