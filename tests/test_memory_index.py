import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rafael_memory.config import load_config
from rafael_memory.indexer import build_index, extract_structure, write_index


class IndexerTests(unittest.TestCase):
    def test_extract_structure_builds_heading_tree_and_ignores_fences(self):
        structure = extract_structure(
            "# Overview\n"
            "## Setup\n"
            "### Details\n"
            "```markdown\n"
            "# Not a heading\n"
            "```\n"
            "# Next\n"
        )

        self.assertEqual(
            structure,
            [
                {
                    "level": 1,
                    "title": "Overview",
                    "line": 1,
                    "children": [
                        {
                            "level": 2,
                            "title": "Setup",
                            "line": 2,
                            "children": [
                                {
                                    "level": 3,
                                    "title": "Details",
                                    "line": 3,
                                    "children": [],
                                }
                            ],
                        }
                    ],
                },
                {"level": 1, "title": "Next", "line": 7, "children": []},
            ],
        )

    def test_build_index_records_relative_paths_and_content_hashes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            docs = Path(temporary_directory) / "docs"
            nested = docs / "guide"
            nested.mkdir(parents=True)
            content = "# Guide\n\n## Install\n"
            (nested / "start.md").write_text(content, encoding="utf-8")
            (docs / "ignored.txt").write_text("ignored", encoding="utf-8")

            index = build_index(docs)

        self.assertEqual(index["schema_version"], 1)
        self.assertEqual(len(index["documents"]), 1)
        self.assertEqual(index["documents"][0]["path"], "guide/start.md")
        self.assertEqual(
            index["documents"][0]["sha256"],
            hashlib.sha256(content.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(index["documents"][0]["structure"][0]["title"], "Guide")

    def test_write_index_creates_local_json_index(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "readme.md").write_text("# Local\n", encoding="utf-8")
            output = root / ".rafael" / "docs-index.json"

            write_index(docs, output)

            stored = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(stored["documents"][0]["path"], "readme.md")


class ConfigTests(unittest.TestCase):
    def test_config_uses_isolated_test_app_and_replay_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()

        self.assertEqual(config.app_id, "rafael-ai-office-test")
        self.assertTrue(config.replay_protection.enabled)
        self.assertEqual(config.replay_protection.nonce_ttl_seconds, 300)

    def test_config_reads_test_app_and_c02_settings(self):
        with patch.dict(
            os.environ,
            {
                "TEST_APP_ID": "isolated-suite",
                "C02_REPLAY_PROTECTION_ENABLED": "false",
                "C02_NONCE_TTL_SECONDS": "120",
            },
            clear=True,
        ):
            config = load_config()

        self.assertEqual(config.app_id, "isolated-suite")
        self.assertFalse(config.replay_protection.enabled)
        self.assertEqual(config.replay_protection.nonce_ttl_seconds, 120)


if __name__ == "__main__":
    unittest.main()
