import math
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class HeatmapScore:
    topic: str
    citation_velocity: float
    recency_weight: float
    gap_signal: float
    replication_index: float
    composite: float


class HeatmapScorer:
    WEIGHTS = {
        "citation_velocity": 0.30,
        "recency_weight": 0.20,
        "gap_signal": 0.30,
        "replication_index": 0.20,
    }

    def score_topic(self, works: list[dict], topic: str) -> HeatmapScore:
        cv = self._citation_velocity(works)
        rw = self._recency_weight(works)
        gs = self._gap_signal(works)
        ri = self._replication_index(works)
        composite = (
            self.WEIGHTS["citation_velocity"] * cv +
            self.WEIGHTS["recency_weight"] * rw +
            self.WEIGHTS["gap_signal"] * gs +
            self.WEIGHTS["replication_index"] * ri
        )
        return HeatmapScore(topic, cv, rw, gs, ri, round(composite, 2))

    def _citation_velocity(self, works: list[dict]) -> float:
        now = datetime.utcnow().year
        recent = [w for w in works if w.get("publication_year", 0) >= now - 3]
        if not recent:
            return 0.0
        avg_cite = sum(w.get("cited_by_count", 0) for w in recent) / len(recent)
        older = [w for w in works if w.get("publication_year", 0) < now - 3]
        old_avg = sum(w.get("cited_by_count", 0) for w in older) / max(len(older), 1)
        if old_avg == 0:
            return min(100.0, avg_cite * 2)
        ratio = avg_cite / old_avg
        return min(100.0, ratio * 25)

    def _recency_weight(self, works: list[dict]) -> float:
        now = datetime.utcnow().year
        if not works:
            return 0.0
        ages = [now - w.get("publication_year", now) for w in works]
        avg_age = sum(ages) / len(ages)
        return max(0, min(100, 100 - (avg_age * 10)))

    def _gap_signal(self, works: list[dict]) -> float:
        all_keywords = []
        for w in works:
            kws = w.get("keywords", [])
            all_keywords.extend([k.get("display_name", "") for k in kws])
        if not all_keywords:
            return 50.0
        unique = len(set(all_keywords))
        total = len(all_keywords)
        diversity = unique / total if total else 0
        return min(100.0, diversity * 120)

    def _replication_index(self, works: list[dict]) -> float:
        if not works:
            return 0.0
        multi = sum(1 for w in works if len(w.get("indexed_in", [])) >= 2)
        return (multi / len(works)) * 100

    def rank_topics(self, topic_scores: list[HeatmapScore]) -> list[HeatmapScore]:
        return sorted(topic_scores, key=lambda s: s.composite, reverse=True)
