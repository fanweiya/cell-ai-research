import argparse
import json
from datetime import date

from museum.analytics import MuseumAnalytics
from museum.sample_data import WINDOW_END, WINDOW_START, build_demo_database


def _money(value: float) -> str:
    return f"{value:,.2f}"


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _rule(title: str) -> str:
    return f"\n{title}\n" + "-" * len(title)


def render_report(analytics: MuseumAnalytics, start: date | None, end: date | None, top: int) -> str:
    """Renders a plain text report.

    Args:
        analytics: Analytics bound to a store.
        start: First date in the window.
        end: Last date in the window.
        top: Number of artworks to list.

    Returns:
        The report as one string.
    """
    revenue = analytics.revenue_summary(start, end)
    attendance = analytics.attendance_summary(start, end)
    demographics = analytics.demographic_summary(start, end)
    exhibitions = analytics.exhibition_performance(start, end)
    artworks = analytics.popular_artworks(start, end, top_n=top)
    segments = analytics.spending_by_age_band(start, end)

    lines = [
        "Museum analytics report",
        f"Window: {start.isoformat() if start else 'first record'} to {end.isoformat() if end else 'last record'}",
        _rule("Revenue"),
        f"Net revenue:        {_money(revenue.net_revenue)}",
        f"Gross revenue:      {_money(revenue.gross_revenue)}",
        f"Discounts:          {_money(revenue.discount_total)}",
        f"Refunds:            {_money(revenue.refund_total)}",
        f"Tickets:            {revenue.ticket_count}",
        f"Admissions:         {revenue.admissions}",
        f"Average price:      {_money(revenue.average_price)}",
        f"Member share:       {_percent(revenue.member_share)}",
        "",
        "Revenue by ticket type:",
    ]
    for ticket_type, amount in revenue.by_ticket_type.items():
        lines.append(f"  {ticket_type:<10} {_money(amount):>12}")
    lines.append("")
    lines.append("Revenue by month:")
    for month, amount in revenue.by_month.items():
        lines.append(f"  {month:<10} {_money(amount):>12}")

    lines.append(_rule("Attendance"))
    lines.append(f"Visits:             {attendance.total_visits}")
    lines.append(f"Unique visitors:    {attendance.unique_visitors}")
    lines.append(f"Repeat visitors:    {attendance.repeat_visitors} ({_percent(attendance.repeat_visitor_rate)})")
    lines.append(f"Average dwell:      {attendance.average_dwell_minutes:.1f} min")
    lines.append(f"Median dwell:       {attendance.median_dwell_minutes:.1f} min")
    peak = ", ".join(f"{hour:02d}:00 ({count})" for hour, count in attendance.peak_hours) or "no data"
    lines.append(f"Peak entry hours:   {peak}")
    lines.append("")
    lines.append("Busiest days:")
    for day, count in sorted(attendance.by_day.items(), key=lambda item: (-item[1], item[0]))[:5]:
        lines.append(f"  {day}  {count:>5}")

    lines.append(_rule("Visitors"))
    lines.append(f"Unique visitors:    {demographics.unique_visitors}")
    lines.append(f"Average age:        {demographics.average_age:.1f}")
    lines.append(f"Median age:         {demographics.median_age:.1f}")
    lines.append(f"Members:            {_percent(demographics.member_share)}")
    lines.append(f"First-time:         {_percent(demographics.first_time_share)}")
    lines.append("")
    lines.append("Age bands:")
    for band, count in demographics.age_bands.items():
        lines.append(f"  {band:<8} {count:>5}  {_percent(demographics.age_band_share[band]):>7}")
    lines.append("")
    lines.append("Top regions:")
    for region, count in demographics.top_regions:
        lines.append(f"  {region:<8} {count:>5}")

    lines.append(_rule("Exhibitions"))
    lines.append(f"  {'ID':<12}{'Tickets':>8}{'Admissions':>12}{'Net':>12}{'Share':>8}{'Dwell':>8}{'Capacity':>10}")
    for row in exhibitions:
        lines.append(
            f"  {row.exhibition_id:<12}{row.tickets:>8}{row.admissions:>12}{_money(row.net_revenue):>12}"
            f"{_percent(row.revenue_share):>8}{row.average_dwell_minutes:>8.1f}{_percent(row.capacity_utilization):>10}"
        )

    lines.append(_rule(f"Top {len(artworks)} artworks by views"))
    lines.append(f"  {'ID':<10}{'Views':>7}{'Viewers':>9}{'Dwell s':>9}{'Likes':>8}  Title")
    for row in artworks:
        lines.append(
            f"  {row.artwork_id:<10}{row.views:>7}{row.unique_viewers:>9}{row.mean_dwell_seconds:>9.1f}"
            f"{_percent(row.like_rate):>8}  {row.title} — {row.artist}"
        )

    lines.append(_rule("Spending by age band"))
    lines.append(f"  {'Band':<8}{'Visitors':>9}{'Net':>12}{'Per visitor':>13}")
    for row in segments:
        lines.append(f"  {row.label:<8}{row.visitors:>9}{_money(row.net_spend):>12}{_money(row.average_spend):>13}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Builds the command line parser.

    Returns:
        A parser with report options.
    """
    parser = argparse.ArgumentParser(prog="museum-report", description="Print a museum analytics report.")
    parser.add_argument("--start", type=date.fromisoformat, default=WINDOW_START, help="first date, YYYY-MM-DD")
    parser.add_argument("--end", type=date.fromisoformat, default=WINDOW_END, help="last date, YYYY-MM-DD")
    parser.add_argument("--top", type=int, default=10, help="number of artworks to list")
    parser.add_argument("--visitors", type=int, default=2500, help="size of the generated sample dataset")
    parser.add_argument("--seed", type=int, default=20260301, help="seed for the generated sample dataset")
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Runs the command line interface.

    Args:
        argv: Arguments to parse; defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code.
    """
    args = build_parser().parse_args(argv)
    database = build_demo_database(visitor_count=args.visitors, seed=args.seed)
    analytics = MuseumAnalytics(database)
    if args.json:
        print(json.dumps(analytics.full_report(args.start, args.end), ensure_ascii=False, indent=2))
        return 0
    print(render_report(analytics, args.start, args.end, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
