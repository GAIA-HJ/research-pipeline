import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime


SCHOLAR_META_TEMPLATE = (
    '<meta name="citation_title" content="{title}">\n'
    '<meta name="citation_author" content="{author}">\n'
    '<meta name="citation_publication_date" content="{date}">\n'
    '<meta name="citation_journal_title" content="{journal}">\n'
    '<meta name="citation_pdf_url" content="{pdf_url}">\n'
    '<meta name="citation_abstract" content="{abstract}">\n'
)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  {scholar_meta}
  <style>
    body {{ max-width:800px; margin:2rem auto; font-family:Georgia,serif; line-height:1.7; padding:0 1rem; }}
    h1 {{ font-size:1.8rem; }} h2 {{ font-size:1.3rem; margin-top:2rem; }}
    .meta {{ color:#666; font-size:0.9rem; }}
    table {{ border-collapse:collapse; width:100%; }} td,th {{ border:1px solid #ccc; padding:6px; }}
  </style>
</head>
<body>
  <article>
    <h1>{title}</h1>
    <p class="meta">Generated: {date} | Heatmap Score: {score} | Sources: {sources}</p>
    <p class="meta">Content Hash: <code>{content_hash}</code></p>
    {body_html}
  </article>
</body>
</html>"""


class Publisher:
    def __init__(self, site_dir: str, site_url: str, author: str, journal_name: str):
        self.site_dir = Path(site_dir)
        self.site_url = site_url.rstrip("/")
        self.author = author
        self.journal = journal_name

    def publish_article(self, article_folder: Path) -> str:
        meta = json.loads((article_folder / "meta.json").read_text())
        md_text = (article_folder / "article.md").read_text()
        body_html = self._md_to_html(md_text)
        title = meta.get("title", "Untitled")
        date = meta.get("generated_at", "")[:10]
        slug = article_folder.name
        scholar_meta = SCHOLAR_META_TEMPLATE.format(
            title=title, author=self.author, date=date,
            journal=self.journal,
            pdf_url=f"{self.site_url}/articles/{slug}/article.pdf",
            abstract=body_html[:300].replace("<", "").replace(">", ""),
        )
        html = HTML_TEMPLATE.format(
            title=title, scholar_meta=scholar_meta, date=date,
            score=meta.get("heatmap_score", {}).get("composite", "N/A"),
            sources=meta.get("sources_count", 0),
            content_hash=meta.get("content_hash", ""),
            body_html=body_html,
        )
        dest = self.site_dir / "articles" / slug
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(html)
        shutil.copy2(article_folder / "meta.json", dest / "meta.json")
        return f"{self.site_url}/articles/{slug}/"

    def push_to_git(self, commit_msg: str = None):
        msg = commit_msg or f"Auto-publish {datetime.utcnow().strftime('%Y-%m-%d')}"
        subprocess.run(["git", "add", "."], cwd=self.site_dir, check=True)
        subprocess.run(["git", "commit", "-m", msg], cwd=self.site_dir, check=True)
        subprocess.run(["git", "push"], cwd=self.site_dir, check=True)

    def _md_to_html(self, md: str) -> str:
        try:
            import markdown
            return markdown.markdown(md, extensions=["tables", "fenced_code"])
        except ImportError:
            return f"<pre>{md}</pre>"
