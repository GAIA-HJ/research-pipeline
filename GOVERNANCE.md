# Research Pipeline - Data Governance Framework
Version 1.0 | March 2026

## 1. ZERO-TRAINING RULE
- No user data sent for model training (API calls default to NO training)
- No content cached by third parties
- No raw articles stored on blockchain (only SHA-256 hashes)
- Local-first storage for all generated content

## 2. DATA FLOW ISOLATION (Siloed Phases)
- Phase 1 INGEST: Data flows IN only (OpenAlex to your server)
- Phase 2 SCORE/AUGMENT: Processing happens LOCALLY only
- Phase 3 GENERATE: Only topic summaries sent to LLM (no raw PDFs)
- Phase 4 PUBLISH: Data flows OUT only (your server to your website)
- Phase 5 ANCHOR: Only hash string goes to blockchain

## 3. IP PROTECTION
- Generated articles: SHA-256 hash + Polygon timestamp = proof of authorship
- Scoring algorithm: Proprietary (never leaves your server)
- Source mappings: evidence.db audit trail with timestamps

## 4. PUBLICATION STRATEGY
- Your website first with Google Scholar meta tags
- Google Scholar: Auto-indexed via citation meta tags
- Semantic Scholar: Auto-crawl or API submission
- Default license: CC BY-NC 4.0

## 5. COMPLIANCE
- GDPR: No personal data collected; only public metadata
- Saudi PDPL: No Saudi resident data processed
- US Copyright: Transformative synthesis with attribution
- CCPA: No consumer data involved

## 6. AUDIT TRAIL
Every pipeline run produces:
1. cycle_summary.json - what was generated, when, from what
2. sources.json - full provenance of every cited work
3. evidence.db - immutable local log of all actions
4. Blockchain receipt - tamper-proof external timestamp
