import httpx
import json
from datetime import datetime


class ArticleGenerator:
    SYSTEM_PROMPT = (
        "You are a scholarly research synthesizer. Given bibliometric "
        "data, scored topics, and live datasets, produce a structured academic article with: "
        "Abstract, Introduction, Methodology, Findings, Discussion, Conclusion. "
        "Use inline citations in [Author, Year] format. Include data tables where applicable. "
        "Output valid Markdown."
    )

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514", provider: str = "anthropic"):
        self.api_key = api_key
        self.model = model
        self.provider = provider

    async def generate(self, topic: str, scored_works: list,
                       augmented_data: list, heatmap_score: dict) -> dict:
        prompt = self._build_prompt(topic, scored_works, augmented_data, heatmap_score)
        if self.provider == "anthropic":
            content = await self._call_anthropic(prompt)
        else:
            content = await self._call_openai(prompt)
        return {
            "title": f"Synthesized Review: {topic}",
            "content_markdown": content,
            "generated_at": datetime.utcnow().isoformat(),
            "model": self.model,
            "sources_count": len(scored_works),
            "augmentation_sources": len(augmented_data),
            "heatmap_score": heatmap_score,
        }

    def _build_prompt(self, topic, works, aug, score) -> str:
        return (
            f"Topic: {topic}\n"
            f"Heatmap Score: {json.dumps(score, default=str)}\n"
            f"Top Sources ({len(works)} works): {json.dumps(works[:10], default=str)[:3000]}\n"
            f"Live Augmentation Data: {json.dumps(aug[:5], default=str)[:2000]}\n\n"
            f"Synthesize a scholarly article following academic structure."
        )

    async def _call_anthropic(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as c:
            resp = await c.post("https://api.anthropic.com/v1/messages", json={
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "system": self.SYSTEM_PROMPT,
            }, headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            })
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]

    async def _call_openai(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as c:
            resp = await c.post("https://api.openai.com/v1/chat/completions", json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4096,
            }, headers={"Authorization": f"Bearer {self.api_key}"})
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
