# Museum visitor analytics

A dependency-free Python package for answering the operational questions a museum asks after a season: how much money came in, who came, what they looked at, and which exhibition earned its keep.

Everything runs on the standard library. There is no database server, no pandas, and no plotting dependency; a store lives in memory, and reports come out as plain text or JSON.

## Layout

```
museum_analytics/
├── museum/
│   ├── models.py       # frozen dataclasses for visitors, exhibitions, artworks, tickets, visits, views
│   ├── database.py     # in-memory store with foreign-key and duplicate checks
│   ├── stats.py        # mean, median, percentile, stdev, mode, top_labels, safe_ratio
│   ├── analytics.py    # summaries and rankings over a date window
│   ├── sample_data.py  # deterministic demo dataset
│   └── cli.py          # command line report
└── tests/              # unittest suite, 54 cases
```

## Quick start

```bash
cd museum_analytics
python -m museum.cli                     # text report over the demo season
python -m museum.cli --top 5             # shorter artwork table
python -m museum.cli --json              # same report as JSON
python -m museum.cli --start 2026-04-01 --end 2026-04-30
python -m museum.cli --visitors 5000 --seed 99
```

Building a store from your own records:

```python
from datetime import date
from museum import Exhibition, MuseumAnalytics, MuseumDatabase, Ticket, Visitor

store = MuseumDatabase()
store.add_exhibition(Exhibition("exh-light", "Light", "Curator", "theme", date(2026, 3, 1), date(2026, 5, 31), 60))
store.add_visitor(Visitor("v1", "Ada Bauer", 34, "female", "NY", False, date(2026, 3, 2)))
store.add_ticket(Ticket("t1", "v1", "exh-light", date(2026, 3, 1), date(2026, 3, 2), "adult", 28.0))

analytics = MuseumAnalytics(store)
print(analytics.revenue_summary(date(2026, 3, 1), date(2026, 3, 31)).to_dict())
```

`MuseumDatabase` validates on insert: unknown visitor, exhibition or artwork ids raise `KeyError`, repeated ids and malformed field values raise `ValueError`. Nothing is silently dropped.

## Report sections

The text report prints six blocks; the JSON report carries the same numbers plus the visitor demographic block.

| Block | Question it answers |
| --- | --- |
| Revenue | Net, gross, discounts, refunds, admissions, average price, member share, split by ticket type, exhibition and month |
| Attendance | Visits, unique and repeat visitors, dwell time mean and median, peak entry hours, busiest days, per-exhibition counts, capacity utilisation |
| Visitors | Age bands and shares, mean and median age, gender split, top regions, member and first-time shares |
| Exhibitions | Tickets, admissions, net revenue, revenue share, average dwell, capacity utilisation, ranked by revenue |
| Top artworks | Views, unique viewers, mean dwell, like rate, engagement, ranked by a chosen metric |
| Spending by age band | Net spend and spend per visitor for each band |

## Analytics API

All window arguments are inclusive `date` pairs. Omitting them uses the full range of stored records. An end date before the start date raises `ValueError`.

| Method | Returns |
| --- | --- |
| `revenue_summary(start, end)` | `RevenueSummary` |
| `attendance_summary(start, end)` | `AttendanceSummary` |
| `demographic_summary(start, end)` | `DemographicSummary` |
| `exhibition_performance(start, end)` | `list[ExhibitionPerformance]` |
| `popular_artworks(start, end, top_n=10, metric="views", min_views=1)` | `list[ArtworkPopularity]` |
| `top_visitors(start, end, limit=10)` | `list[VisitorSpending]` |
| `spending_by_age_band(start, end)` | `list[SegmentSpending]` |
| `full_report(start, end)` | `dict` ready for `json.dumps` |

`popular_artworks` accepts `views`, `dwell`, `likes` or `engagement`; engagement is likes divided by views. Ties break on view count, then artwork id, so repeated runs agree.

## Metric definitions

- **Net revenue** sums `list_price * group_size - discount` over tickets whose visit date falls in the window and that were not refunded. Refunded tickets still count toward gross revenue and toward the refund total, so the three figures reconcile.
- **Admissions** sums `group_size` over the same non-refunded tickets, not the number of tickets sold to groups.
- **Dwell time** is exit time minus entry time, in minutes, averaged over visits.
- **Repeat visitors** are visitors with two or more visits inside the window; the rate divides by unique visitors.
- **Capacity utilisation** divides admissions by daily capacity times the number of days the exhibition was open inside the window, so partially overlapping windows stay honest.
- **Revenue share** divides an exhibition's net revenue by the window's total net revenue, and is zero when the window has no revenue.

## Design notes

- Records are frozen dataclasses with `slots=True`: a ticket cannot mutate after it is filed, and money fields are computed properties rather than stored duplicates.
- The store keeps insertion-ordered dictionaries, so output order is stable across runs without sorting every structure.
- Derived money is rounded to two decimals at the summary boundary. Percentages and shares keep four decimals because they are reported as rates, not currency.
- Date filters compare calendar dates. `Visit` uses the entry timestamp, `ArtworkView` the view timestamp, `Ticket` the visit date; a ticket bought in March for an April visit belongs to April.
- `stats.safe_ratio` returns `0.0` instead of raising on a zero denominator, which keeps empty windows printable. `stats.mean`, `median`, `stdev` and `mode` do raise on empty input, because those cases signal a caller mistake.

## Sample dataset

`build_demo_database(visitor_count=2500, seed=20260301)` generates a season from 2026-03-01 to 2026-05-31 with three exhibitions, thirty artworks, seven ticket types (one of them complimentary) and a fixed random seed. The same seed always produces the same store, so tests and demos are reproducible. Visitor ages, regions, membership, visit timing and dwell time follow fixed distributions; about three tickets in a hundred are refunded.

## Extending

- **A new summary**: add a dataclass beside the existing ones, then a method on `MuseumAnalytics` that reads through the store's `*_between` helpers and rounds at the boundary. Wire it into `full_report` and, if it belongs in the text report, into `render_report` in `museum/cli.py`.
- **A new source of records**: implement the same `add_*` methods on a store class and pass it to `MuseumAnalytics`. The analytics layer only depends on the store's query methods.
- **A new ticket type or age band**: extend `TICKET_TYPES` or `AGE_BANDS` in `museum/models.py`. Age bands must cover 0 to 120 without gaps or overlaps; validation rejects anything else.

## Tests

```bash
cd museum_analytics
python -m unittest discover -s tests -v
```

The suite builds one hand-computed fixture (four visitors, two exhibitions, five tickets including one refund, four visits, four artwork views) and asserts every published figure against arithmetic done by hand, then repeats the summaries over an empty store and over badly ordered windows.
