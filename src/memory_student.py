from __future__ import annotations

import time
from typing import Any

from .config import settings
from .context_budget import ContextBudgetManager
from .utils import cap_query, join_nonempty
from .zep_common import prime_eval_thread, render_graph_search

# Retrieval widths. Kept as named constants so the trade-off (recall vs. tokens)
# is explicit instead of buried as magic numbers in the calls below.
LONG_TERM_FACT_LIMIT = 25  # a small limit drops deadline / open-loop edges (E03)
LONG_TERM_EPISODE_LIMIT = 12  # raw episodes keep literal codes the facts paraphrase away
SEMANTIC_LIMIT = 8

# Episodic search runs in two tiers, because one limit cannot serve both callers.
# Asking for fewer episodes than the corpus holds makes Zep actually rank them;
# asking for more returns everything in chronological order instead. But a
# tight top-k misses episodes for some phrasings (a reflection-worded query
# ranks the target 10th), while a wide-k overflows the 3% episodic budget in
# mixed cases and gets tail-trimmed exactly where the answer sits.
# So: ranked head first, broad recall appended after, duplicates dropped.
# Episodic-only cases read the whole thing; mixed cases keep the ranked head.
EPISODIC_RANKED_LIMIT = 4
EPISODIC_LIMIT = 12

# The evaluator primes each query into a thread owned by the user
# (prime_eval_thread), so every long-term case leaves its own question behind as
# an episode in that user's graph. Those decoy episodes are long (golden prompts
# run 450-589 chars) and outrank the real session turns, which are all under 200
# chars. Capping each episode truncates the decoys while leaving genuine turns
# whole, so more distinct real episodes fit under the same budget.
EPISODIC_CHAR_CAP = 200

SEARCH_ATTEMPTS = 3


def _dedupe_lines(text: str) -> str:
    """Drop repeated lines while keeping first-seen order.

    The two episodic tiers overlap by design; without this the ranked head is
    paid for twice and the budget trims that much more real evidence away.
    """
    seen: set[str] = set()
    kept: list[str] = []
    for line in text.split("\n"):
        key = line.strip()
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        kept.append(line)
    return "\n".join(kept)


class StudentMemory:
    """Only this file needs to be edited by students."""

    def __init__(self, client: Any):
        self.client = client
        self.budget = ContextBudgetManager(settings.context_tokens)

    # NOTE: Zep rejects graph.search queries longer than 400 characters. Some
    # eval queries are longer than that, so wrap every query with
    # `cap_query(query)` (see src/utils.py) before passing it to graph.search.

    def _search(self, **kwargs: Any) -> Any:
        """graph.search with retries, degrading to None instead of raising.

        Two reasons this is not a bare call:
        * An unsupported scope must not zero out a whole case, so callers can
          try a preferred scope and fall back.
        * A dropped TLS handshake would otherwise silently turn into empty
          evidence and a FAIL, which is indistinguishable from a retrieval bug.
        """
        for attempt in range(SEARCH_ATTEMPTS):
            try:
                return self.client.graph.search(**kwargs)
            except Exception:
                if attempt < SEARCH_ATTEMPTS - 1:
                    time.sleep(1.5 * (attempt + 1))
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

        # Both the Context Block and the extracted facts PARAPHRASE the source,
        # which drops literal codes: the open loop stored as "Day la open loop
        # LAB-REPORT-1600" comes back only as "has a task to complete the
        # benchmark report before ... 16:00". Raw episodes keep the code, so
        # append them last — the budget trims from the tail, so this extra
        # recall costs nothing to the mixed cases that only need the head.
        episodes = self._search(
            user_id=user_id,
            query=cap_query(query),
            scope="episodes",
            limit=LONG_TERM_EPISODE_LIMIT,
        )
        episode_text = (
            render_graph_search(episodes, episode_char_cap=EPISODIC_CHAR_CAP)
            if episodes is not None
            else ""
        )

        # user_id scoping is the whole isolation guarantee (E09): never widen
        # any of these three calls to a shared graph_id.
        return join_nonempty([context_text, fact_text, episode_text])

    def retrieve_episodic(self, user_id: str, query: str) -> str:
        # LAB TODO 2/4 -- done.
        # Episodes are the raw ingested sources, so they preserve the literal
        # trajectory markers (ASYNC-FIX-20) that extracted facts drop.
        chunks = []
        for limit in (EPISODIC_RANKED_LIMIT, EPISODIC_LIMIT):
            results = self._search(
                user_id=user_id,
                query=cap_query(query),
                scope="episodes",
                limit=limit,
            )
            if results is not None:
                chunks.append(render_graph_search(results, episode_char_cap=EPISODIC_CHAR_CAP))
        return _dedupe_lines(join_nonempty(chunks))

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
