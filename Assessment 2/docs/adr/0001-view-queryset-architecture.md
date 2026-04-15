# ADR 0001:

## Decision
1. Introduce custom QuerySets and managers in `blog_app.models`.
2. Keep query composition close to model concerns (`with_related`, `high_confidence`, `flagged_or_anomalous`, `with_quality_metrics`, `with_recording_stats`).
3. Implement API-style with reusable mixins in `blog_app.views`:
   - `JSONResponseMixin` for consistent JSON responses.
   - `RecordingQuerysetMixin` for shared base queryset composition.
4. Prefer ORM optimizations:
   - `select_related` for FK joins (`user`, `species`, `location`).
   - `prefetch_related` for reverse relations (`anomaly_flags`, `anomaly_flags__flagged_by`).

## Consequences
- Positive:
  - Reusable and testable query building.
  - Reduced N+1 query risk on detail/list views.
  - CBV decomposition encourages extension without duplicating logic.
- Tradeoffs:
  - Slightly more indirection than simple function-based views.
  - Analytics responses rely on ORM-generated SQL that should be profiled if dataset grows significantly.
