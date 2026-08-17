from __future__ import annotations

from typing import Any

from .config import settings
from .context_budget import ContextBudgetManager
from .utils import cap_query, join_nonempty
from .zep_common import prime_eval_thread, render_graph_search

# Retrieval widths. Kept as named constants so the trade-off (recall vs. tokens)
# is explicit instead of buried as magic numbers in the calls below.
LONG_TERM_FACT_LIMIT = 25  # a small limit drops deadline / open-loop edges (E03)
EPISODIC_LIMIT = 8
EPISODIC_CHAR_CAP = 600  # keep verbose session episodes from crowding out reflections
SEMANTIC_LIMIT = 8


class StudentMemory:
    """Only this file needs to be edited by students."""

    def __init__(self, client: Any):
        self.client = client
        self.budget = ContextBudgetManager(settings.context_tokens)

    # NOTE: Zep rejects graph.search queries longer than 400 characters. Some
    # eval queries are longer than that, so wrap every query with
    # `cap_query(query)` (see src/utils.py) before passing it to graph.search.

    def _search(self, **kwargs: Any) -> Any:
        """graph.search that degrades to None instead of raising.

        A single unsupported scope must not zero out a whole case, so callers
        can try a preferred scope and fall back.
        """
        try:
            return self.client.graph.search(**kwargs)
        except Exception:
            return None

    def retrieve_long_term(self, user_id: str, thread_id: str, query: str) -> str:
        # LAB TODO 1/4 -- done.
        # Zep builds the Context Block from the *user graph* using the newest
        # thread messages as the relevance signal, so the eval query is primed
        # into a throwaway thread first.
        prime_eval_thread(self.client, user_id, thread_id, query)
        context = self.client.thread.get_user_context(thread_id=thread_id)
        context_text = getattr(context, "context", "") or ""

        # The Context Block is relevance-summarised and can leave out a dated
        # open loop (E03) or the newer half of a conflicting preference (E08).
        # A user-scoped edge search adds the raw facts plus their validity
        # range, which is what makes "recency wins" auditable.
        facts = self._search(
            user_id=user_id,
            query=cap_query(query),
            scope="edges",
            limit=LONG_TERM_FACT_LIMIT,
        )
        fact_text = render_graph_search(facts) if facts is not None else ""

        # user_id scoping is the whole isolation guarantee (E09): never widen
        # this to a shared graph_id.
        return join_nonempty([context_text, fact_text])

    def retrieve_episodic(self, user_id: str, query: str) -> str:
        # LAB TODO 2/4 -- done.
        # Episodes are the raw ingested sources, so they preserve the literal
        # trajectory markers (ASYNC-FIX-20) that extracted facts drop.
        results = self._search(
            user_id=user_id,
            query=cap_query(query),
            scope="episodes",
            limit=EPISODIC_LIMIT,
        )
        if results is None:
            return ""
        return render_graph_search(results, episode_char_cap=EPISODIC_CHAR_CAP)

    def retrieve_semantic(self, graph_id: str, query: str) -> str:
        # LAB TODO 3/4 -- done.
        # Standalone domain graph: scoped by graph_id, never by user_id, so the
        # answer is shared knowledge and cannot leak a user's preferences.
        # scope="episodes" returns raw document text and keeps literal markers
        # (PAYMENT-RULE-3, CONN-POOL-FIRST); scope="auto" returns extracted
        # facts that drop them.
        results = self._search(
            graph_id=graph_id,
            query=cap_query(query),
            scope="episodes",
            limit=SEMANTIC_LIMIT,
        )
        text = render_graph_search(results) if results is not None else ""
        if text.strip():
            return text

        # Fallback for a graph whose episodes are not searchable yet.
        results = self._search(
            graph_id=graph_id,
            query=cap_query(query),
            scope="nodes",
            limit=SEMANTIC_LIMIT,
        )
        return render_graph_search(results) if results is not None else ""

    def assemble_context(self, layers: dict[str, str]) -> tuple[str, dict[str, dict[str, int]]]:
        # LAB TODO 4/4 -- done.
        # ContextBudgetManager already encodes the 10/4/3/3 budget and the
        # short_term -> long_term -> episodic -> semantic priority order.
        return self.budget.assemble(layers)
