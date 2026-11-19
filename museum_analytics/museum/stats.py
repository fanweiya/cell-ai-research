from collections import Counter
from collections.abc import Iterable, Sequence


def mean(values: Sequence[float]) -> float:
    """Arithmetic mean of a non-empty sequence.

    Args:
        values: Numbers to average.

    Returns:
        The mean as a float.

    Raises:
        ValueError: If ``values`` is empty.
    """
    if not values:
        raise ValueError("mean requires at least one value")
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    """Median of a non-empty sequence.

    Args:
        values: Numbers to summarise.

    Returns:
        The middle value, or the mean of the two middle values.

    Raises:
        ValueError: If ``values`` is empty.
    """
    if not values:
        raise ValueError("median requires at least one value")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def percentile(values: Sequence[float], fraction: float) -> float:
    """Percentile with linear interpolation between closest ranks.

    Args:
        values: Numbers to summarise.
        fraction: Position in ``[0, 1]``, where ``0.9`` is the 90th percentile.

    Returns:
        The interpolated percentile.

    Raises:
        ValueError: If ``values`` is empty or ``fraction`` is outside ``[0, 1]``.
    """
    if not values:
        raise ValueError("percentile requires at least one value")
    if not 0.0 <= fraction <= 1.0:
        raise ValueError("fraction must be between 0 and 1")
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return float(ordered[lower] + (ordered[upper] - ordered[lower]) * weight)


def stdev(values: Sequence[float]) -> float:
    """Sample standard deviation.

    Args:
        values: Numbers to summarise.

    Returns:
        The sample standard deviation, zero for a single value.

    Raises:
        ValueError: If ``values`` is empty.
    """
    if not values:
        raise ValueError("stdev requires at least one value")
    if len(values) == 1:
        return 0.0
    average = mean(values)
    variance = sum((value - average) ** 2 for value in values) / (len(values) - 1)
    return variance ** 0.5


def mode(values: Iterable[str]) -> str:
    """Most common label, with deterministic tie-breaking.

    Args:
        values: Labels to count.

    Returns:
        The label with the highest count; ties go to alphabetical order.

    Raises:
        ValueError: If ``values`` is empty.
    """
    counts = Counter(values)
    if not counts:
        raise ValueError("mode requires at least one value")
    return min(counts, key=lambda label: (-counts[label], label))


def top_labels(values: Iterable[str], limit: int) -> list[tuple[str, int]]:
    """Most common labels with counts.

    Args:
        values: Labels to count.
        limit: Maximum number of pairs to return.

    Returns:
        Pairs sorted by count descending, then label ascending.
    """
    if limit < 1:
        raise ValueError("limit must be positive")
    counts = Counter(values)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]


def safe_ratio(numerator: float, denominator: float) -> float:
    """Division that returns ``0.0`` when the denominator is zero.

    Args:
        numerator: Dividend.
        denominator: Divisor.

    Returns:
        The quotient, or ``0.0`` when ``denominator`` is zero.
    """
    if denominator == 0:
        return 0.0
    return numerator / denominator
