from dataclasses import dataclass
from datetime import date, datetime

GENDERS = ("female", "male", "nonbinary", "unknown")
TICKET_TYPES = ("adult", "child", "senior", "student", "member", "group", "comp")
AGE_BANDS = (
    (0, 17, "0-17"),
    (18, 24, "18-24"),
    (25, 34, "25-34"),
    (35, 44, "35-44"),
    (45, 54, "45-54"),
    (55, 64, "55-64"),
    (65, 120, "65+"),
)


def age_band(age: int) -> str:
    """Maps an age to its reporting band.

    Args:
        age: Visitor age in years.

    Returns:
        Band label such as ``"25-34"``.
    """
    for low, high, label in AGE_BANDS:
        if low <= age <= high:
            return label
    raise ValueError(f"age {age} does not fall into any reporting band")


def _require_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _require_date(value: date, field: str) -> None:
    if not isinstance(value, date) or isinstance(value, datetime):
        raise ValueError(f"{field} must be a date")


@dataclass(frozen=True, slots=True)
class Visitor:
    """A person on record at the museum.

    Attributes:
        visitor_id: Stable identifier used by tickets and artwork views.
        name: Display name.
        age: Age in years at the time of the record.
        gender: One of :data:`GENDERS`.
        region: Home region, usually a state or city code.
        is_member: Whether the visitor holds an annual membership.
        first_visit_date: Date of the earliest recorded visit.
    """

    visitor_id: str
    name: str
    age: int
    gender: str
    region: str
    is_member: bool
    first_visit_date: date

    def __post_init__(self) -> None:
        _require_text(self.visitor_id, "visitor_id")
        _require_text(self.name, "name")
        if not isinstance(self.age, int) or not 0 <= self.age <= 120:
            raise ValueError(f"age must be an int between 0 and 120, got {self.age!r}")
        if self.gender not in GENDERS:
            raise ValueError(f"gender must be one of {GENDERS}, got {self.gender!r}")
        _require_text(self.region, "region")
        _require_date(self.first_visit_date, "first_visit_date")

    @property
    def age_band(self) -> str:
        """Reporting band for this visitor's age."""
        return age_band(self.age)


@dataclass(frozen=True, slots=True)
class Exhibition:
    """A temporary or permanent exhibition with limited daily capacity.

    Attributes:
        exhibition_id: Stable identifier used by tickets, visits and artworks.
        title: Public title.
        curator: Curator name.
        theme: Short theme label used for grouping.
        start_date: First day the exhibition is open.
        end_date: Last day the exhibition is open.
        daily_capacity: Maximum number of visitors admitted per open day.
    """

    exhibition_id: str
    title: str
    curator: str
    theme: str
    start_date: date
    end_date: date
    daily_capacity: int

    def __post_init__(self) -> None:
        _require_text(self.exhibition_id, "exhibition_id")
        _require_text(self.title, "title")
        _require_text(self.curator, "curator")
        _require_text(self.theme, "theme")
        _require_date(self.start_date, "start_date")
        _require_date(self.end_date, "end_date")
        if self.end_date < self.start_date:
            raise ValueError("end_date must not be earlier than start_date")
        if not isinstance(self.daily_capacity, int) or self.daily_capacity <= 0:
            raise ValueError("daily_capacity must be a positive integer")

    @property
    def duration_days(self) -> int:
        """Number of calendar days the exhibition is open."""
        return (self.end_date - self.start_date).days + 1


@dataclass(frozen=True, slots=True)
class Artwork:
    """A catalogued object shown inside an exhibition.

    Attributes:
        artwork_id: Stable identifier used by artwork views.
        title: Public title.
        artist: Artist or culture of origin.
        year: Year of creation; use a negative value for BCE.
        medium: Material label such as ``"oil on canvas"``.
        exhibition_id: Exhibition the object is displayed in.
    """

    artwork_id: str
    title: str
    artist: str
    year: int
    medium: str
    exhibition_id: str

    def __post_init__(self) -> None:
        _require_text(self.artwork_id, "artwork_id")
        _require_text(self.title, "title")
        _require_text(self.artist, "artist")
        _require_text(self.medium, "medium")
        _require_text(self.exhibition_id, "exhibition_id")
        if not isinstance(self.year, int) or not -5000 <= self.year <= 2100:
            raise ValueError(f"year must be an int between -5000 and 2100, got {self.year!r}")


@dataclass(frozen=True, slots=True)
class Ticket:
    """A ticket sale, possibly covering several people.

    Attributes:
        ticket_id: Stable identifier used by visits.
        visitor_id: Purchasing visitor.
        exhibition_id: Exhibition the ticket admits to.
        purchase_date: Date the ticket was bought.
        visit_date: Date the ticket is valid for.
        ticket_type: One of :data:`TICKET_TYPES`.
        list_price: Undiscounted price per person.
        discount: Discount per person, in currency units.
        group_size: Number of people admitted by this ticket.
        refunded: Whether the sale was refunded.
    """

    ticket_id: str
    visitor_id: str
    exhibition_id: str
    purchase_date: date
    visit_date: date
    ticket_type: str
    list_price: float
    discount: float = 0.0
    group_size: int = 1
    refunded: bool = False

    def __post_init__(self) -> None:
        _require_text(self.ticket_id, "ticket_id")
        _require_text(self.visitor_id, "visitor_id")
        _require_text(self.exhibition_id, "exhibition_id")
        _require_date(self.purchase_date, "purchase_date")
        _require_date(self.visit_date, "visit_date")
        if self.visit_date < self.purchase_date:
            raise ValueError("visit_date must not be earlier than purchase_date")
        if self.ticket_type not in TICKET_TYPES:
            raise ValueError(f"ticket_type must be one of {TICKET_TYPES}, got {self.ticket_type!r}")
        if not isinstance(self.list_price, (int, float)) or self.list_price < 0:
            raise ValueError("list_price must be a non-negative number")
        if not isinstance(self.discount, (int, float)) or not 0 <= self.discount <= self.list_price:
            raise ValueError("discount must be between 0 and list_price")
        if not isinstance(self.group_size, int) or self.group_size < 1:
            raise ValueError("group_size must be a positive integer")
        if not isinstance(self.refunded, bool):
            raise ValueError("refunded must be a bool")

    @property
    def gross_revenue(self) -> float:
        """Revenue before discounts and refunds."""
        return round(self.list_price * self.group_size, 2)

    @property
    def discount_total(self) -> float:
        """Total discount granted on this ticket."""
        return round(self.discount * self.group_size, 2)

    @property
    def net_revenue(self) -> float:
        """Revenue actually kept, zero for refunded tickets."""
        if self.refunded:
            return 0.0
        return round((self.list_price - self.discount) * self.group_size, 2)


@dataclass(frozen=True, slots=True)
class Visit:
    """One entry and exit record for a visitor inside an exhibition.

    Attributes:
        visit_id: Stable identifier.
        visitor_id: Visitor who entered.
        exhibition_id: Exhibition entered.
        ticket_id: Ticket used for entry.
        entry_time: Entry timestamp.
        exit_time: Exit timestamp.
    """

    visit_id: str
    visitor_id: str
    exhibition_id: str
    ticket_id: str
    entry_time: datetime
    exit_time: datetime

    def __post_init__(self) -> None:
        _require_text(self.visit_id, "visit_id")
        _require_text(self.visitor_id, "visitor_id")
        _require_text(self.exhibition_id, "exhibition_id")
        _require_text(self.ticket_id, "ticket_id")
        if not isinstance(self.entry_time, datetime) or not isinstance(self.exit_time, datetime):
            raise ValueError("entry_time and exit_time must be datetimes")
        if self.exit_time <= self.entry_time:
            raise ValueError("exit_time must be later than entry_time")

    @property
    def duration_minutes(self) -> float:
        """Time spent inside the exhibition, in minutes."""
        return (self.exit_time - self.entry_time).total_seconds() / 60.0


@dataclass(frozen=True, slots=True)
class ArtworkView:
    """A visitor standing in front of one artwork.

    Attributes:
        view_id: Stable identifier.
        visitor_id: Visitor who viewed the artwork.
        artwork_id: Artwork viewed.
        timestamp: Moment the visitor left the artwork.
        dwell_seconds: Seconds spent in front of the artwork.
        liked: Whether the visitor pressed the like button.
    """

    view_id: str
    visitor_id: str
    artwork_id: str
    timestamp: datetime
    dwell_seconds: int
    liked: bool = False

    def __post_init__(self) -> None:
        _require_text(self.view_id, "view_id")
        _require_text(self.visitor_id, "visitor_id")
        _require_text(self.artwork_id, "artwork_id")
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime")
        if not isinstance(self.dwell_seconds, int) or self.dwell_seconds < 0:
            raise ValueError("dwell_seconds must be a non-negative integer")
        if not isinstance(self.liked, bool):
            raise ValueError("liked must be a bool")
