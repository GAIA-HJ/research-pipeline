import httpx


class BiblioEngine:
    BASE = "https://api.openalex.org"

    def __init__(self, api_key: str = "", email: str = ""):
        self.params = {}
        if api_key:
            self.params["api_key"] = api_key
        if email:
            self.params["mailto"] = email
        self.client = httpx.AsyncClient(timeout=30)

    async def search_works(self, query: str, per_page: int = 25,
                           sort: str = "cited_by_count:desc") -> list[dict]:
        resp = await self.client.get(f"{self.BASE}/works", params={
            "search": query, "per_page": per_page, "sort": sort,
            **self.params,
        })
        resp.raise_for_status()
        return resp.json().get("results", [])

    async def get_work(self, work_id: str) -> dict:
        resp = await self.client.get(f"{self.BASE}/works/{work_id}",
                                     params=self.params)
        resp.raise_for_status()
        return resp.json()

    async def search_concepts(self, query: str, per_page: int = 10) -> list[dict]:
        resp = await self.client.get(f"{self.BASE}/concepts", params={
            "search": query, "per_page": per_page, **self.params,
        })
        resp.raise_for_status()
        return resp.json().get("results", [])

    async def get_author(self, author_id: str) -> dict:
        resp = await self.client.get(f"{self.BASE}/authors/{author_id}",
                                     params=self.params)
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self.client.aclose()
