from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Literal

from museum import stats
from museum.database import MuseumDatabase
from museum.models import age_band

PopularityMetric = Literal["views", "dwell", "likes", "engagement"]

POPULARITY_METRICS: tuple[PopularityMetric, ...] = ("views", "dwell", "likes", "engagement")


def _month_key(day: date) -> str:
    return f"{day.year:04d}-{day.month:02d}"


def _sorted_money(values: dict[str, float]) -> dict[str, float]:
    return {key: round(value, 2) for key, value in sorted(values.items(), key=lambda item: (-item[1], item[0]))}


@dataclass(frozen=True, slots=True)
class RevenueSummary:
    """Money taken and given back over a reporting window.

    Attributes:
        start: First visit date in the window, or ``None``.
        end: Last visit date in the window, or ``None``.
        ticket_count: Number of ticket records, refunds included.
        admissions: People admitted, refunds excluded.
        gross_revenue: Revenue before discounts and refunds.
        discount_total: Money given away through discounts.
        refund_total: Money returned on refunded tickets.
        net_revenue: Revenue kept.
        average_price: Net revenue per admitted person.
        member_share: Share of net revenue from members.
        by_exhibition: Net revenue per exhibition.
        by_ticket_type: Net revenue per ticket type.
        by_month: Net revenue per calendar month, keyed ``YYYY-MM``.
    """

    start: date | None
    end: date | None
    ticket_count: int
    admissions: int
    gross_revenue: float
    discount_total: float
    refund_total: float
    net_revenue: float
    average_price: float
    member_share: float
    by_exhibition: dict[str, float] = field(default_factory=dict)
    by_ticket_type: dict[str, float] = field(default_factory=dict)
    by_month: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialises the summary with dates as ISO strings."""
        payload = asdict(self)
        payload["start"] = self.start.isoformat() if self.start else None
        payload["end"] = self.end.isoformat() if self.end else None
        return payload


@dataclass(frozen=True, slots=True)
class AttendanceSummary:
    """Foot traffic over a reporting window.

    Attributes:
        total_visits: Recorded entries.
        unique_visitors: Distinct people behind those entries.
        repeat_visitors: People with more than one entry.
        repeat_visitor_rate: Repeat visitors divided by unique visitors.
        average_dwell_minutes: Mean time inside an exhibition.
        median_dwell_minutes: Median time inside an exhibition.
        by_exhibition: Entries per exhibition.
        by_day: Entries per calendar day, keyed ``YYYY-MM-DD``.
        peak_hours: Up to three ``(hour, entries)`` pairs, busiest first.
        capacity_utilization: Admissions divided by capacity per exhibition.
    """

    total_visits: int
    unique_visitors: int
    repeat_visitors: int
    repeat_visitor_rate: float
    average_dwell_minutes: float
    median_dwell_minutes: float
    by_exhibition: dict[str, int] = field(default_factory=dict)
    by_day: dict[str, int] = field(default_factory=dict)
    peak_hours: list[tuple[int, int]] = field(default_factory=list)
    capacity_utilization: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialises the summary, converting peak hours to lists."""
        payload = asdict(self)
        payload["peak_hours"] = [[hour, count] for hour, count in self.peak_hours]
        return payload


@dataclass(frozen=True, slots=True)
class DemographicSummary:
    """Who visited during a reporting window.

    Attributes:
        unique_visitors: Distinct visitors.
        age_bands: Visitors per reporting band.
        age_band_share: Band counts divided by unique visitors.
        average_age: Mean visitor age.
        median_age: Median visitor age.
        gender: Visitors per gender label.
        top_regions: Up to five ``(region, visitors)`` pairs, largest first.
        member_share: Members divided by unique visitors.
        first_time_share: Visitors whose first recorded visit falls in the window.
    """

    unique_visitors: int
    age_bands: dict[str, int] = field(default_factory=dict)
    age_band_share: dict[str, float] = field(default_factory=dict)
    average_age: float = 0.0
    median_age: float = 0.0
    gender: dict[str, int] = field(default_factory=dict)
    top_regions: list[tuple[str, int]] = field(default_factory=list)
    member_share: float = 0.0
    first_time_share: float = 0.0

    def to_dict(self) -> dict:
        """Serialises the summary, converting region pairs to lists."""
        payload = asdict(self)
        payload["top_regions"] = [[region, count] for region, count in self.top_regions]
        return payload


@dataclass(frozen=True, slots=True)
class ExhibitionPerformance:
    """One exhibition's contribution to the window.

    Attributes:
        exhibition_id: Exhibition identifier.
        title: Exhibition title.
        tickets: Tickets sold for the exhibition.
        admissions: People admitted, refunds excluded.
        net_revenue: Revenue kept.
        revenue_share: Share of the window's net revenue.
        average_dwell_minutes: Mean time inside the exhibition, zero without visits.
        capacity_utilization: Admissions divided by available capacity.
    """

    exhibition_id: str
    title: str
    tickets: int
    admissions: int
    net_revenue: float
    revenue_share: float
    average_dwell_minutes: float
    capacity_utilization: float


@dataclass(frozen=True, slots=True)
class ArtworkPopularity:
    """Aggregated attention for a single artwork.

    Attributes:
        artwork_id: Artwork identifier.
        title: Artwork title.
        artist: Artist name.
        exhibition_id: Exhibition holding the artwork.
        views: Recorded views.
        unique_viewers: Distinct visitors who viewed it.
        mean_dwell_seconds: Mean time spent in front of it.
        like_rate: Likes divided by views.
        metric_value: Value of the ranking metric used for the sort.
    """

    artwork_id: str
    title: str
    artist: str
    exhibition_id: str
    views: int
    unique_viewers: int
    mean_dwell_seconds: float
    like_rate: float
    metric_value: float


@dataclass(frozen=True, slots=True)
class VisitorSpending:
    """Lifetime value of one visitor inside the window.

    Attributes:
        visitor_id: Visitor identifier.
        name: Visitor name.
        visits: Entries recorded in the window.
        net_spend: Net ticket revenue attributed to the visitor.
        age_band: Reporting age band.
        region: Home region.
    """

    visitor_id: str
    name: str
    visits: int
    net_spend: float
    age_band: str
    region: str


@dataclass(frozen=True, slots=True)
class SegmentSpending:
    """Spending aggregated for one visitor segment.

    Attributes:
        label: Segment label, an age band in the current implementation.
        visitors: Distinct visitors in the segment.
        net_spend: Net revenue attributed to the segment.
        average_spend: Net spend per visitor.
    """

    label: str
    visitors: int
    net_spend: float
    average_spend: float


class MuseumAnalytics:
    """Computes revenue, attendance, demographic and collection metrics.

    Every public method accepts an optional closed date window. Tickets are
    filtered by visit date, visits by entry date and artwork views by
    timestamp date, so a single window describes the same period for all
    three sources.
    """

    def __init__(self, database: MuseumDatabase) -> None:
        """Binds the analytics layer to a store.

        Args:
            database: Store to read from.
        """
        self._db = database

    def revenue_summary(self, start: date | None = None, end: date | None = None) -> RevenueSummary:
        """Summarises ticket revenue.

        Args:
            start: First visit date, inclusive.
            end: Last visit date, inclusive.

        Returns:
            Revenue totals, averages and breakdowns.
        """
        self._validate_window(start, end)
        tickets = self._db.tickets_between(start, end)
        kept = [ticket for ticket in tickets if not ticket.refunded]
        gross = sum(ticket.gross_revenue for ticket in tickets)
        discounts = sum(ticket.discount_total for ticket in tickets)
        refunds = sum(ticket.gross_revenue - ticket.discount_total for ticket in tickets if ticket.refunded)
        net = sum(ticket.net_revenue for ticket in kept)
        admissions = sum(ticket.group_size for ticket in kept)

        by_exhibition: dict[str, float] = {}
        by_ticket_type: dict[str, float] = {}
        by_month: dict[str, float] = {}
        member_revenue = 0.0
        for ticket in kept:
            by_exhibition[ticket.exhibition_id] = by_exhibition.get(ticket.exhibition_id, 0.0) + ticket.net_revenue
            by_ticket_type[ticket.ticket_type] = by_ticket_type.get(ticket.ticket_type, 0.0) + ticket.net_revenue
            month = _month_key(ticket.visit_date)
            by_month[month] = by_month.get(month, 0.0) + ticket.net_revenue
            if self._db.visitor(ticket.visitor_id).is_member:
                member_revenue += ticket.net_revenue

        return RevenueSummary(
            start=start,
            end=end,
            ticket_count=len(tickets),
            admissions=admissions,
            gross_revenue=float(round(gross, 2)),
            discount_total=float(round(discounts, 2)),
            refund_total=float(round(refunds, 2)),
            net_revenue=float(round(net, 2)),
            average_price=round(stats.safe_ratio(net, admissions), 2),
            member_share=round(stats.safe_ratio(member_revenue, net), 4),
            by_exhibition=_sorted_money(by_exhibition),
            by_ticket_type=_sorted_money(by_ticket_type),
            by_month={month: round(value, 2) for month, value in sorted(by_month.items())},
        )

    def attendance_summary(self, start: date | None = None, end: date | None = None) -> AttendanceSummary:
        """Summarises foot traffic and dwell time.

        Args:
            start: First entry date, inclusive.
            end: Last entry date, inclusive.

        Returns:
            Visit counts, repeat rate, dwell statistics, peak hours and
            capacity utilisation.
        """
        self._validate_window(start, end)
        visits = self._db.visits_between(start, end)
        durations = [visit.duration_minutes for visit in visits]
        by_visitor: dict[str, int] = {}
        by_exhibition: dict[str, int] = {}
        by_day: dict[str, int] = {}
        by_hour: dict[int, int] = {}
        for visit in visits:
            by_visitor[visit.visitor_id] = by_visitor.get(visit.visitor_id, 0) + 1
            by_exhibition[visit.exhibition_id] = by_exhibition.get(visit.exhibition_id, 0) + 1
            day = visit.entry_time.date().isoformat()
            by_day[day] = by_day.get(day, 0) + 1
            hour = visit.entry_time.hour
            by_hour[hour] = by_hour.get(hour, 0) + 1

        unique = len(by_visitor)
        repeat = sum(1 for count in by_visitor.values() if count > 1)
        peak_hours = sorted(by_hour.items(), key=lambda item: (-item[1], item[0]))[:3]

        return AttendanceSummary(
            total_visits=len(visits),
            unique_visitors=unique,
            repeat_visitors=repeat,
            repeat_visitor_rate=round(stats.safe_ratio(repeat, unique), 4),
            average_dwell_minutes=round(stats.mean(durations), 2) if durations else 0.0,
            median_dwell_minutes=round(stats.median(durations), 2) if durations else 0.0,
            by_exhibition=dict(sorted(by_exhibition.items(), key=lambda item: (-item[1], item[0]))),
            by_day=dict(sorted(by_day.items())),
            peak_hours=peak_hours,
            capacity_utilization=self._capacity_utilization(start, end),
        )

    def demographic_summary(self, start: date | None = None, end: date | None = None) -> DemographicSummary:
        """Summarises the visitor population behind a window.

        Args:
            start: First entry date, inclusive.
            end: Last entry date, inclusive.

        Returns:
            Age, gender, region, membership and first-visit breakdowns.
        """
        self._validate_window(start, end)
        visitor_ids = {visit.visitor_id for visit in self._db.visits_between(start, end)}
        visitors = [self._db.visitor(visitor_id) for visitor_id in sorted(visitor_ids)]
        ages = [visitor.age for visitor in visitors]
        bands: dict[str, int] = {}
        for visitor in visitors:
            bands[visitor.age_band] = bands.get(visitor.age_band, 0) + 1
        ordered_bands = {label: bands[label] for label in sorted(bands, key=_band_order)}
        total = len(visitors)
        members = sum(1 for visitor in visitors if visitor.is_member)
        first_time = sum(1 for visitor in visitors if _in_window(visitor.first_visit_date, start, end))

        return DemographicSummary(
            unique_visitors=total,
            age_bands=ordered_bands,
            age_band_share={label: round(stats.safe_ratio(count, total), 4) for label, count in ordered_bands.items()},
            average_age=round(stats.mean(ages), 2) if ages else 0.0,
            median_age=round(stats.median(ages), 2) if ages else 0.0,
            gender=dict(sorted(Counter(visitor.gender for visitor in visitors).items())),
            top_regions=stats.top_labels((visitor.region for visitor in visitors), 5),
            member_share=round(stats.safe_ratio(members, total), 4),
            first_time_share=round(stats.safe_ratio(first_time, total), 4),
        )

    def exhibition_performance(self, start: date | None = None, end: date | None = None) -> list[ExhibitionPerformance]:
        """Ranks exhibitions by net revenue.

        Args:
            start: First visit date, inclusive.
            end: Last visit date, inclusive.

        Returns:
            One record per exhibition, highest revenue first.
        """
        self._validate_window(start, end)
        revenue = self.revenue_summary(start, end)
        visits = self._db.visits_between(start, end)
        dwell: dict[str, list[float]] = {}
        for visit in visits:
            dwell.setdefault(visit.exhibition_id, []).append(visit.duration_minutes)
        capacity = self._capacity_utilization(start, end)
        tickets = self._db.tickets_between(start, end)
        rows: list[ExhibitionPerformance] = []
        for exhibition in self._db.exhibitions:
            own = [ticket for ticket in tickets if ticket.exhibition_id == exhibition.exhibition_id]
            kept = [ticket for ticket in own if not ticket.refunded]
            net = float(round(sum(ticket.net_revenue for ticket in kept), 2))
            rows.append(
                ExhibitionPerformance(
                    exhibition_id=exhibition.exhibition_id,
                    title=exhibition.title,
                    tickets=len(own),
                    admissions=sum(ticket.group_size for ticket in kept),
                    net_revenue=net,
                    revenue_share=round(stats.safe_ratio(net, revenue.net_revenue), 4),
                    average_dwell_minutes=round(stats.mean(dwell.get(exhibition.exhibition_id, [])), 2)
                    if dwell.get(exhibition.exhibition_id)
                    else 0.0,
                    capacity_utilization=capacity.get(exhibition.exhibition_id, 0.0),
                )
            )
        rows.sort(key=lambda row: (-row.net_revenue, row.exhibition_id))
        return rows

    def popular_artworks(
        self,
        start: date | None = None,
        end: date | None = None,
        top_n: int = 10,
        metric: PopularityMetric = "views",
        min_views: int = 1,
    ) -> list[ArtworkPopularity]:
        """Ranks artworks by attention.

        Args:
            start: First view date, inclusive.
            end: Last view date, inclusive.
            top_n: Number of artworks to return.
            metric: Ranking metric; one of :data:`POPULARITY_METRICS`.
            min_views: Artworks with fewer views are skipped.

        Returns:
            Artworks sorted by the chosen metric, then by views, then by id.

        Raises:
            ValueError: If ``metric`` is unknown, ``top_n`` is not positive or
                ``min_views`` is negative.
        """
        self._validate_window(start, end)
        if metric not in POPULARITY_METRICS:
            raise ValueError(f"metric must be one of {POPULARITY_METRICS}, got {metric!r}")
        if top_n < 1:
            raise ValueError("top_n must be positive")
        if min_views < 0:
            raise ValueError("min_views must not be negative")

        grouped: dict[str, list] = {}
        for view in self._db.views_between(start, end):
            grouped.setdefault(view.artwork_id, []).append(view)

        rows: list[ArtworkPopularity] = []
        for artwork_id, views in grouped.items():
            if len(views) < min_views:
                continue
            artwork = self._db.artwork(artwork_id)
            likes = sum(1 for view in views if view.liked)
            dwell = [view.dwell_seconds for view in views]
            like_rate = stats.safe_ratio(likes, len(views))
            mean_dwell = stats.mean(dwell)
            values = {
                "views": float(len(views)),
                "dwell": mean_dwell,
                "likes": float(likes),
                "engagement": like_rate,
            }
            rows.append(
                ArtworkPopularity(
                    artwork_id=artwork_id,
                    title=artwork.title,
                    artist=artwork.artist,
                    exhibition_id=artwork.exhibition_id,
                    views=len(views),
                    unique_viewers=len({view.visitor_id for view in views}),
                    mean_dwell_seconds=round(mean_dwell, 2),
                    like_rate=round(like_rate, 4),
                    metric_value=round(values[metric], 4),
                )
            )
        rows.sort(key=lambda row: (-row.metric_value, -row.views, row.artwork_id))
        return rows[:top_n]

    def top_visitors(self, start: date | None = None, end: date | None = None, limit: int = 10) -> list[VisitorSpending]:
        """Ranks visitors by net spend inside the window.

        Args:
            start: First visit date, inclusive.
            end: Last visit date, inclusive.
            limit: Number of visitors to return.

        Returns:
            Visitors sorted by net spend, then by visit count, then by id.

        Raises:
            ValueError: If ``limit`` is not positive.
        """
        self._validate_window(start, end)
        if limit < 1:
            raise ValueError("limit must be positive")
        spend: dict[str, float] = {}
        for ticket in self._db.tickets_between(start, end):
            if ticket.refunded:
                continue
            spend[ticket.visitor_id] = spend.get(ticket.visitor_id, 0.0) + ticket.net_revenue
        visits: dict[str, int] = {}
        for visit in self._db.visits_between(start, end):
            visits[visit.visitor_id] = visits.get(visit.visitor_id, 0) + 1
        rows = [
            VisitorSpending(
                visitor_id=visitor_id,
                name=self._db.visitor(visitor_id).name,
                visits=visits.get(visitor_id, 0),
                net_spend=float(round(amount, 2)),
                age_band=age_band(self._db.visitor(visitor_id).age),
                region=self._db.visitor(visitor_id).region,
            )
            for visitor_id, amount in spend.items()
        ]
        rows.sort(key=lambda row: (-row.net_spend, -row.visits, row.visitor_id))
        return rows[:limit]

    def spending_by_age_band(self, start: date | None = None, end: date | None = None) -> list[SegmentSpending]:
        """Aggregates net spend per age band.

        Args:
            start: First visit date, inclusive.
            end: Last visit date, inclusive.

        Returns:
            Segments sorted by net spend, highest first.
        """
        self._validate_window(start, end)
        spend: dict[str, float] = {}
        visitors: dict[str, set[str]] = {}
        for ticket in self._db.tickets_between(start, end):
            if ticket.refunded:
                continue
            band = age_band(self._db.visitor(ticket.visitor_id).age)
            spend[band] = spend.get(band, 0.0) + ticket.net_revenue
            visitors.setdefault(band, set()).add(ticket.visitor_id)
        rows = [
            SegmentSpending(
                label=band,
                visitors=len(visitors[band]),
                net_spend=float(round(amount, 2)),
                average_spend=float(round(stats.safe_ratio(amount, len(visitors[band])), 2)),
            )
            for band, amount in spend.items()
        ]
        rows.sort(key=lambda row: (-row.net_spend, row.label))
        return rows

    def full_report(self, start: date | None = None, end: date | None = None) -> dict:
        """Collects every summary into one JSON-ready mapping.

        Args:
            start: First date in the window, inclusive.
            end: Last date in the window, inclusive.

        Returns:
            A mapping with revenue, attendance, demographics, exhibitions,
            popular artworks and spending segments.
        """
        self._validate_window(start, end)
        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "window": {
                "start": start.isoformat() if start else None,
                "end": end.isoformat() if end else None,
            },
            "revenue": self.revenue_summary(start, end).to_dict(),
            "attendance": self.attendance_summary(start, end).to_dict(),
            "demographics": self.demographic_summary(start, end).to_dict(),
            "exhibitions": [asdict(row) for row in self.exhibition_performance(start, end)],
            "popular_artworks": [asdict(row) for row in self.popular_artworks(start, end, top_n=10)],
            "age_band_spending": [asdict(row) for row in self.spending_by_age_band(start, end)],
        }

    def _capacity_utilization(self, start: date | None, end: date | None) -> dict[str, float]:
        tickets = self._db.tickets_between(start, end)
        admitted: dict[str, int] = {}
        for ticket in tickets:
            if ticket.refunded:
                continue
            admitted[ticket.exhibition_id] = admitted.get(ticket.exhibition_id, 0) + ticket.group_size
        utilization: dict[str, float] = {}
        for exhibition in self._db.exhibitions:
            first = max(start, exhibition.start_date) if start else exhibition.start_date
            last = min(end, exhibition.end_date) if end else exhibition.end_date
            open_days = max((last - first).days + 1, 0)
            capacity = exhibition.daily_capacity * open_days
            utilization[exhibition.exhibition_id] = round(stats.safe_ratio(admitted.get(exhibition.exhibition_id, 0), capacity), 4)
        return utilization

    @staticmethod
    def _validate_window(start: date | None, end: date | None) -> None:
        for value in (start, end):
            if value is not None and not isinstance(value, date):
                raise ValueError("window bounds must be dates or None")
        if start is not None and end is not None and end < start:
            raise ValueError("end must not be earlier than start")


def _in_window(day: date, start: date | None, end: date | None) -> bool:
    if start is not None and day < start:
        return False
    if end is not None and day > end:
        return False
    return True


def _band_order(label: str) -> int:
    order = ["0-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    return order.index(label)
