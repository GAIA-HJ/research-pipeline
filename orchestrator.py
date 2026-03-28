import asyncio
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path

from config import Config
from biblio_engine import BiblioEngine
from heatmap_scorer import HeatmapScorer, HeatmapScore
from augmentor import LiveAugmentor
from generator import ArticleGenerator
from blockchain_anchor import BlockchainAnchor
from evidence_store import EvidenceStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("orchestrator")


class PipelineOrchestrator:
    def __init__(self, config: Config):
        self.cfg = config
        self.engine = BiblioEngine(config.OPENALEX_API_KEY)
        self.scorer = HeatmapScorer()
        self.augmentor = LiveAugmentor(config.OPENALEX_API_KEY)
        self.generator = ArticleGenerator(
            api_key=config.LLM_API_KEY,
            model=config.LLM_MODEL,
            provider=config.LLM_PROVIDER,
        )
        self.anchor = (
            BlockchainAnchor(config.POLYGON_RPC_URL, config.POLYGON_PRIVATE_KEY)
            if config.POLYGON_PRIVATE_KEY
            else None
        )
        self.evidence = EvidenceStore(config.EVIDENCE_DB_PATH)
        self.out = Path(config.OUTPUT_DIR)
        self.out.mkdir(parents=True, exist_ok=True)

    async def run_cycle(self, topics=None):
        topics = topics or self.cfg.DEFAULT_TOPICS
        cycle_id = datetime.utcnow().strftime("%Y%m%d_%H%M")
        log.info(f"Cycle {cycle_id} | {len(topics)} topics")

        scored = []
        for t in topics:
            log.info(f"[ingest] {t}")
            works = await self.engine.search_works(t, per_page=25)
            hs = self.scorer.score_topic(works, t)
            scored.append((hs, works))
            log.info(f"  score={hs.composite} works={len(works)}")

        scored.sort(key=lambda x: x[0].composite, reverse=True)
        selected = scored[:self.cfg.ARTICLES_PER_CYCLE]
        articles_produced = []

        for hs, works in selected:
            topic = hs.topic
            log.info(f"[generate] {topic} (score {hs.composite})")
            aug = await self.augmentor.augment_topic(topic)
            aug_dicts = [{"source": a.source, "dataset": a.dataset,
                         "records": a.records_count, "sample": a.sample} for a in aug]

            article = await self.generator.generate(
                topic=topic, scored_works=works, augmented_data=aug_dicts,
                heatmap_score={"composite": hs.composite, "citation_velocity": hs.citation_velocity,
                               "recency": hs.recency_weight, "gap_signal": hs.gap_signal,
                               "replication": hs.replication_index},
            )

            content_hash = hashlib.sha256(article["content_markdown"].encode()).hexdigest()
            self.evidence.store({"cycle": cycle_id, "topic": topic,
                                 "content_hash": content_hash, "sources_count": len(works),
                                 "heatmap": hs.composite, "generated_at": article["generated_at"]})

            anchor_receipt = None
            if self.anchor:
                try:
                    anchor_receipt = self.anchor.anchor_hash(content_hash, {"cycle": cycle_id, "topic": topic})
                    log.info(f"  anchored tx={anchor_receipt['tx_hash'][:16]}")
                except Exception as e:
                    log.warning(f"  anchor failed: {e}")

            slug = topic.lower().replace(" ", "_")[:40]
            folder = self.out / cycle_id / slug
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "article.md").write_text(article["content_markdown"])
            (folder / "meta.json").write_text(json.dumps(
                {**article, "content_hash": content_hash, "anchor": anchor_receipt},
                indent=2, default=str))
            (folder / "sources.json").write_text(json.dumps(works[:30], indent=2, default=str))

            articles_produced.append({"topic": topic, "score": hs.composite,
                                      "hash": content_hash, "path": str(folder),
                                      "anchor_tx": anchor_receipt["tx_hash"] if anchor_receipt else None})
            log.info(f"  saved {folder}")

        summary_path = self.out / cycle_id / "cycle_summary.json"
        summary_path.write_text(json.dumps({"cycle_id": cycle_id, "ran_at": datetime.utcnow().isoformat(),
                                            "topics_evaluated": len(topics),
                                            "articles_produced": len(articles_produced),
                                            "articles": articles_produced}, indent=2, default=str))
        log.info(f"Cycle {cycle_id} complete: {len(articles_produced)} articles")
        await self.augmentor.close()
        return articles_produced


async def main():
    config = Config()
    orch = PipelineOrchestrator(config)
    results = await orch.run_cycle()
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
