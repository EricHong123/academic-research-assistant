"""Metrics collection for monitoring."""
import time
from typing import Any, Callable
from functools import wraps
from collections import defaultdict
from dataclasses import dataclass, field
import threading


@dataclass
class Counter:
    """Simple counter metric."""

    name: str
    value: int = 0
    labels: dict[str, str] = field(default_factory=dict)

    def inc(self, amount: int = 1):
        """Increment counter."""
        self.value += amount

    def reset(self):
        """Reset counter."""
        self.value = 0


@dataclass
class Histogram:
    """Simple histogram metric."""

    name: str
    buckets: list[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
    values: list[float] = field(default_factory=list)
    labels: dict[str, str] = field(default_factory=dict)

    def observe(self, value: float):
        """Observe a value."""
        self.values.append(value)

    def get_percentile(self, percentile: float) -> float:
        """Get percentile value."""
        if not self.values:
            return 0.0
        sorted_values = sorted(self.values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def reset(self):
        """Reset histogram."""
        self.values = []


class MetricsRegistry:
    """Simple metrics registry."""

    def __init__(self):
        self._counters: dict[str, Counter] = {}
        self._histograms: dict[str, Histogram] = {}
        self._lock = threading.Lock()

    def counter(self, name: str, labels: dict[str, str] | None = None) -> Counter:
        """Get or create a counter."""
        key = f"{name}:{json_dumps(labels or {})}"

        with self._lock:
            if key not in self._counters:
                self._counters[key] = Counter(name=name, labels=labels or {})
            return self._counters[key]

    def histogram(self, name: str, labels: dict[str, str] | None = None) -> Histogram:
        """Get or create a histogram."""
        key = f"{name}:{json_dumps(labels or {})}"

        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = Histogram(name=name, labels=labels or {})
            return self._histograms[key]

    def get_all(self) -> dict[str, Any]:
        """Get all metrics in Prometheus format."""
        lines = []

        # Counters
        for counter in self._counters.values():
            lines.append(f"# TYPE {counter.name} counter")
            label_str = format_labels(counter.labels)
            lines.append(f"{counter.name}{label_str} {counter.value}")

        # Histograms
        for histogram in self._histograms.values():
            lines.append(f"# TYPE {histogram.name} histogram")
            label_str = format_labels(histogram.labels)

            # Count
            lines.append(f"{histogram.name}_count{label_str} {len(histogram.values)}")

            # Sum
            lines.append(
                f"{histogram.name}_sum{label_str} {sum(histogram.values)}"
            )

            # Buckets
            for bucket in histogram.buckets:
                bucket_count = len([v for v in histogram.values if v <= bucket])
                bucket_label = f"{histogram.name}_bucket{{le=\"{bucket}\"}}"
                lines.append(f"{bucket_label}{label_str} {bucket_count}")

        return {"metrics": "\n".join(lines)}


def json_dumps(obj: Any) -> str:
    """Simple JSON dumps."""
    import json

    return json.dumps(obj, sort_keys=True)


def format_labels(labels: dict[str, str]) -> str:
    """Format labels for Prometheus."""
    if not labels:
        return ""
    label_parts = [f'{k}="{v}"' for k, v in labels.items()]
    return "{" + ",".join(label_parts) + "}"


# Global metrics registry
registry = MetricsRegistry()


def track_request_duration(method: str, path: str):
    """Decorator to track request duration."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start
                # Track in histogram
                histogram = registry.histogram(
                    "http_request_duration_seconds",
                    {"method": method, "path": path},
                )
                histogram.observe(duration)

                # Track in counter
                counter = registry.counter(
                    "http_requests_total",
                    {"method": method, "path": path, "status": "200"},
                )
                counter.inc()

        return wrapper

    return decorator


# Default metrics
request_counter = lambda: registry.counter("http_requests_total")
request_duration = lambda: registry.histogram("http_request_duration_seconds")
search_counter = lambda: registry.counter("search_requests_total")
parse_counter = lambda: registry.counter("parse_requests_total")
chat_counter = lambda: registry.counter("chat_requests_total")
