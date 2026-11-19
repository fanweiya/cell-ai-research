from datetime import date

from museum.models import Artwork, ArtworkView, Exhibition, Ticket, Visit, Visitor


def _in_window(day: date, start: date | None, end: date | None) -> bool:
    if start is not None and day < start:
        return False
    if end is not None and day > end:
        return False
    return True


class MuseumDatabase:
    """In-memory store for the museum's records.

    Every insert validates its foreign keys against the records already
    loaded, so a broken reference fails at the point of insertion instead of
    surfacing later as a wrong number in a report.
    """

    def __init__(self) -> None:
        """Creates an empty store."""
        self._visitors: dict[str, Visitor] = {}
        self._exhibitions: dict[str, Exhibition] = {}
        self._artworks: dict[str, Artwork] = {}
        self._tickets: dict[str, Ticket] = {}
        self._visits: dict[str, Visit] = {}
        self._views: dict[str, ArtworkView] = {}

    @property
    def visitors(self) -> tuple[Visitor, ...]:
        """All visitors in insertion order."""
        return tuple(self._visitors.values())

    @property
    def exhibitions(self) -> tuple[Exhibition, ...]:
        """All exhibitions in insertion order."""
        return tuple(self._exhibitions.values())

    @property
    def artworks(self) -> tuple[Artwork, ...]:
        """All artworks in insertion order."""
        return tuple(self._artworks.values())

    @property
    def tickets(self) -> tuple[Ticket, ...]:
        """All tickets in insertion order."""
        return tuple(self._tickets.values())

    @property
    def visits(self) -> tuple[Visit, ...]:
        """All visits in insertion order."""
        return tuple(self._visits.values())

    @property
    def views(self) -> tuple[ArtworkView, ...]:
        """All artwork views in insertion order."""
        return tuple(self._views.values())

    def visitor(self, visitor_id: str) -> Visitor:
        """Looks up one visitor.

        Args:
            visitor_id: Identifier to resolve.

        Returns:
            The stored visitor.

        Raises:
            KeyError: If the identifier is unknown.
        """
        return self._visitors[self._require(self._visitors, visitor_id, "visitor")]

    def exhibition(self, exhibition_id: str) -> Exhibition:
        """Looks up one exhibition.

        Args:
            exhibition_id: Identifier to resolve.

        Returns:
            The stored exhibition.

        Raises:
            KeyError: If the identifier is unknown.
        """
        return self._exhibitions[self._require(self._exhibitions, exhibition_id, "exhibition")]

    def artwork(self, artwork_id: str) -> Artwork:
        """Looks up one artwork.

        Args:
            artwork_id: Identifier to resolve.

        Returns:
            The stored artwork.

        Raises:
            KeyError: If the identifier is unknown.
        """
        return self._artworks[self._require(self._artworks, artwork_id, "artwork")]

    def ticket(self, ticket_id: str) -> Ticket:
        """Looks up one ticket.

        Args:
            ticket_id: Identifier to resolve.

        Returns:
            The stored ticket.

        Raises:
            KeyError: If the identifier is unknown.
        """
        return self._tickets[self._require(self._tickets, ticket_id, "ticket")]

    def add_visitor(self, visitor: Visitor) -> None:
        """Stores a visitor.

        Args:
            visitor: Record to store.

        Raises:
            ValueError: If the identifier is already present.
        """
        self._insert(self._visitors, visitor.visitor_id, visitor, "visitor")

    def add_exhibition(self, exhibition: Exhibition) -> None:
        """Stores an exhibition.

        Args:
            exhibition: Record to store.

        Raises:
            ValueError: If the identifier is already present.
        """
        self._insert(self._exhibitions, exhibition.exhibition_id, exhibition, "exhibition")

    def add_artwork(self, artwork: Artwork) -> None:
        """Stores an artwork after checking its exhibition.

        Args:
            artwork: Record to store.

        Raises:
            ValueError: If the identifier is already present.
            KeyError: If the referenced exhibition is unknown.
        """
        if artwork.exhibition_id not in self._exhibitions:
            raise KeyError(f"unknown exhibition {artwork.exhibition_id!r} for artwork {artwork.artwork_id!r}")
        self._insert(self._artworks, artwork.artwork_id, artwork, "artwork")

    def add_ticket(self, ticket: Ticket) -> None:
        """Stores a ticket after checking its visitor and exhibition.

        Args:
            ticket: Record to store.

        Raises:
            ValueError: If the identifier is already present.
            KeyError: If a referenced record is unknown.
        """
        if ticket.visitor_id not in self._visitors:
            raise KeyError(f"unknown visitor {ticket.visitor_id!r} for ticket {ticket.ticket_id!r}")
        if ticket.exhibition_id not in self._exhibitions:
            raise KeyError(f"unknown exhibition {ticket.exhibition_id!r} for ticket {ticket.ticket_id!r}")
        self._insert(self._tickets, ticket.ticket_id, ticket, "ticket")

    def add_visit(self, visit: Visit) -> None:
        """Stores a visit after checking its visitor, exhibition and ticket.

        Args:
            visit: Record to store.

        Raises:
            ValueError: If the identifier is already present.
            KeyError: If a referenced record is unknown.
        """
        if visit.visitor_id not in self._visitors:
            raise KeyError(f"unknown visitor {visit.visitor_id!r} for visit {visit.visit_id!r}")
        if visit.exhibition_id not in self._exhibitions:
            raise KeyError(f"unknown exhibition {visit.exhibition_id!r} for visit {visit.visit_id!r}")
        if visit.ticket_id not in self._tickets:
            raise KeyError(f"unknown ticket {visit.ticket_id!r} for visit {visit.visit_id!r}")
        self._insert(self._visits, visit.visit_id, visit, "visit")

    def add_view(self, view: ArtworkView) -> None:
        """Stores an artwork view after checking its visitor and artwork.

        Args:
            view: Record to store.

        Raises:
            ValueError: If the identifier is already present.
            KeyError: If a referenced record is unknown.
        """
        if view.visitor_id not in self._visitors:
            raise KeyError(f"unknown visitor {view.visitor_id!r} for view {view.view_id!r}")
        if view.artwork_id not in self._artworks:
            raise KeyError(f"unknown artwork {view.artwork_id!r} for view {view.view_id!r}")
        self._insert(self._views, view.view_id, view, "view")

    def tickets_between(self, start: date | None = None, end: date | None = None) -> tuple[Ticket, ...]:
        """Tickets whose visit date falls inside a closed interval.

        Args:
            start: Earliest visit date, inclusive; ``None`` means no lower bound.
            end: Latest visit date, inclusive; ``None`` means no upper bound.

        Returns:
            Matching tickets in insertion order.
        """
        return tuple(t for t in self._tickets.values() if _in_window(t.visit_date, start, end))

    def visits_between(self, start: date | None = None, end: date | None = None) -> tuple[Visit, ...]:
        """Visits whose entry date falls inside a closed interval.

        Args:
            start: Earliest entry date, inclusive; ``None`` means no lower bound.
            end: Latest entry date, inclusive; ``None`` means no upper bound.

        Returns:
            Matching visits in insertion order.
        """
        return tuple(v for v in self._visits.values() if _in_window(v.entry_time.date(), start, end))

    def views_between(self, start: date | None = None, end: date | None = None) -> tuple[ArtworkView, ...]:
        """Artwork views whose timestamp date falls inside a closed interval.

        Args:
            start: Earliest date, inclusive; ``None`` means no lower bound.
            end: Latest date, inclusive; ``None`` means no upper bound.

        Returns:
            Matching views in insertion order.
        """
        return tuple(v for v in self._views.values() if _in_window(v.timestamp.date(), start, end))

    def artworks_in(self, exhibition_id: str) -> tuple[Artwork, ...]:
        """Artworks displayed in one exhibition.

        Args:
            exhibition_id: Exhibition to filter by.

        Returns:
            Matching artworks in insertion order.
        """
        self.exhibition(exhibition_id)
        return tuple(a for a in self._artworks.values() if a.exhibition_id == exhibition_id)

    def _insert(self, store: dict, key: str, record: object, kind: str) -> None:
        if key in store:
            raise ValueError(f"duplicate {kind} id {key!r}")
        store[key] = record

    def _require(self, store: dict, key: str, kind: str) -> str:
        if key not in store:
            raise KeyError(f"unknown {kind} {key!r}")
        return key
