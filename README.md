# 0.rumiel2021a-commits

## Documentation memory index

Run `python -m rafael_memory.indexer` from the repository root to index Markdown
files under `docs/`. The command writes a local JSON index to
`.rafael/docs-index.json`, including each document's SHA-256 hash and nested
heading structure.

The initial configuration is available through `rafael_memory.config.load_config()`.
It reads `TEST_APP_ID` (default: `rafael-ai-office-test`) and the C02 replay
protection settings `C02_REPLAY_PROTECTION_ENABLED` and
`C02_NONCE_TTL_SECONDS`. These settings provide configuration scaffolding;
they do not implement nonce storage or request validation.