import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # OpenAlex
    OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY", "")
    OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL", "")

    # LLM (Article Generation)
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

    # Blockchain (Polygon)
    POLYGON_RPC_URL = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")
    POLYGON_PRIVATE_KEY = os.getenv("POLYGON_PRIVATE_KEY", "")

    # Publishing
    SITE_DIR = os.getenv("SITE_DIR", "./website")
    SITE_URL = os.getenv("SITE_URL", "https://yoursite.com")
    AUTHOR_NAME = os.getenv("AUTHOR_NAME", "Research Pipeline")
    JOURNAL_NAME = os.getenv("JOURNAL_NAME", "Automated Research Review")

    # Pipeline Settings
    DEFAULT_TOPICS = [
        "bibliometrics and citation analysis",
        "artificial intelligence in healthcare",
        "climate change mitigation strategies",
        "computational biology genomics",
        "quantum computing applications",
    ]
    ARTICLES_PER_CYCLE = int(os.getenv("ARTICLES_PER_CYCLE", "3"))
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    EVIDENCE_DB_PATH = os.getenv("EVIDENCE_DB_PATH", "./evidence.db")
