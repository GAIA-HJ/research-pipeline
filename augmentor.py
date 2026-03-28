import httpx
import asyncio
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AugmentedData:
    source: str
    dataset: str
    records_count: int
    sample: list
    retrieval_timestamp: str


class LiveAugmentor:
    SOURCES = {
        "world_bank": "https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&per_page=50",
        "who_gho": "https://ghoapi.azureedge.net/api/{indicator}?$top=50",
        "pubchem": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{query}/JSON",
        "openalex_concepts": "https://api.openalex.org/concepts?search={query}&per_page=10",
    }

    def __init__(self, openalex_key: str = None):
        self.openalex_key = openalex_key
        self.client = httpx.AsyncClient(timeout=30)

    async def augment_topic(self, topic: str, sources: list = None) -> list:
        sources = sources or ["openalex_concepts"]
        tasks = [self._fetch(src, topic) for src in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, AugmentedData)]

    async def _fetch(self, source: str, query: str) -> AugmentedData:
        url_tpl = self.SOURCES.get(source, "")
        url = url_tpl.format(query=query, indicator=query)
        if self.openalex_key and "openalex" in source:
            url += f"&api_key={self.openalex_key}"
        resp = await self.client.get(url)
        resp.raise_for_status()
        data = resp.json()
        records = data if isinstance(data, list) else data.get("results", data.get("value", []))
        if isinstance(records, dict):
            records = [records]
        return AugmentedData(
            source=source,
            dataset=query,
            records_count=len(records),
            sample=records[:5],
            retrieval_timestamp=datetime.utcnow().isoformat()
        )

    async def close(self):
        await self.client.aclose()
