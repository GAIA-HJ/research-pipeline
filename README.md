# Research Pipeline

Automated, secure, blockchain-integrated research publication pipeline that continuously synthesizes existing research into validated scholarly articles using live open data.

## What It Does

Every week, this pipeline automatically:
1. **Ingests** research metadata from OpenAlex (250M+ academic works)
2. **Scores** topics using a proprietary heatmap algorithm (citation velocity, recency, gap signals, replication index)
3. **Augments** top-scoring topics with live data from WHO, World Bank, PubChem
4. **Generates** scholarly articles via AI (Claude/GPT) with full academic structure
5. **Anchors** content hashes to Polygon blockchain for tamper-proof provenance
6. **Publishes** to your website with Google Scholar meta tags for automatic indexing

## Quick Start (Non-Technical)

### Step 1: Clone this repo
```bash
git clone https://github.com/GAIA-HJ/research-pipeline.git
cd research-pipeline
```

### Step 2: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure your keys
```bash
cp .env.example .env
# Edit .env with your keys (see below)
```

### Step 4: Run your first cycle
```bash
python orchestrator.py
```

### Step 5: Start weekly automation
```bash
python scheduler.py
```

## API Keys Needed

| Key | Where | Cost |
|-----|-------|------|
| OpenAlex | openalex.org | Free |
| Anthropic (or OpenAI) | console.anthropic.com | ~$3/article |
| Polygon wallet (optional) | MetaMask | ~$0.01/anchor |

## Architecture

```
OpenAlex API --> biblio_engine.py --> heatmap_scorer.py --> augmentor.py
                                                              |
                                                              v
                                                        generator.py
                                                              |
                                              +---------------+---------------+
                                              |               |               |
                                              v               v               v
                                        publisher.py  blockchain_anchor.py  evidence_store.py
                                              |               |               |
                                              v               v               v
                                         Your Website    Polygon Chain    SQLite Audit DB
```

## File Guide

| File | What it does |
|------|--------------|
| `config.py` | All settings from .env file |
| `biblio_engine.py` | Fetches research from OpenAlex |
| `heatmap_scorer.py` | Scores topics (0-100) for synthesis potential |
| `augmentor.py` | Enriches with live open data |
| `generator.py` | AI-powered article synthesis |
| `blockchain_anchor.py` | Polygon hash anchoring |
| `evidence_store.py` | Local SQLite audit trail |
| `publisher.py` | HTML + Google Scholar tags |
| `orchestrator.py` | Runs full pipeline end-to-end |
| `scheduler.py` | Weekly Saturday 10 AM auto-trigger |

## Security

- Zero-training rule: No data sent for AI model training
- Local-first: All articles stored on YOUR server
- Blockchain: Only SHA-256 hashes on-chain (zero content)
- Siloed phases: No phase accesses another's raw data
- See GOVERNANCE.md for full compliance details

## License

CC BY-NC 4.0
