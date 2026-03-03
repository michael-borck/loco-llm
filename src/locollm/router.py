"""Keyword-based query router.

Scores each adapter by counting keyword hits in the query, then returns
the adapter with the most hits. Returns None when no keywords match,
meaning the base model should handle the query.

This is a deliberately simple PoC — students upgrade to an ML classifier later.
"""

from locollm import adapter_manager


class KeywordRouter:
    """Routes queries to adapters based on keyword matching."""

    def __init__(self):
        self._adapter_keywords = {}
        registry = adapter_manager.load_registry()
        adapters = registry.get("adapters") or {}
        for name, config in adapters.items():
            keywords = config.get("router_keywords", [])
            if keywords:
                self._adapter_keywords[name] = [kw.lower() for kw in keywords]

    def route(self, query: str) -> str | None:
        """Return the best adapter name for a query, or None for base model.

        Scoring: count how many keywords appear (case-insensitive) in the query.
        Ties are broken by alphabetical order (deterministic).
        """
        query_lower = query.lower()
        best_adapter = None
        best_score = 0

        for adapter_name in sorted(self._adapter_keywords):
            keywords = self._adapter_keywords[adapter_name]
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > best_score:
                best_score = score
                best_adapter = adapter_name

        return best_adapter
