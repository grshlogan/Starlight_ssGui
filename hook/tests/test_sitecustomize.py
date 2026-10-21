import importlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


class HookTests(unittest.TestCase):
    def setUp(self):
        self.sitecustomize = importlib.import_module("hook.sitecustomize")
        self.original_environment = os.environ.copy()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_environment)

    def configure(self, audit_path):
        os.environ.update(
            {
                "TOPAZ_SLP_OVERRIDE_ENABLE": "1",
                "TOPAZ_SLP_OVERRIDE_AUDIT_FILE": str(audit_path),
                "TOPAZ_SLP_LAUNCH_ID": "test-launch",
                "TOPAZ_SLP_PIX_CHUNK_SIZE": "121",
            }
        )

    def read_events(self, audit_path):
        return [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]

    def target_module(self):
        module = ModuleType("models.slp25.synthetic")
        module.PIX_CHUNK_SIZE = 33
        module.VAE_DECODE_TILE_SIZE = 640
        return module

    def test_header_and_apply_have_required_audit_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit.jsonl"
            self.configure(audit_path)
            importlib.reload(self.sitecustomize)
            module = self.target_module()
            self.assertTrue(self.sitecustomize.apply_overrides(module))
            self.assertEqual(module.PIX_CHUNK_SIZE, 121)
            events = self.read_events(audit_path)
            self.assertEqual([event["event"] for event in events], ["header", "apply"])
            for event in events:
                self.assertEqual(set(event), {"timestamp_utc", "pid", "launch_id", "event", "changes"})
                self.assertEqual(event["launch_id"], "test-launch")
            changes = events[-1]["changes"]["PIX_CHUNK_SIZE"]
            self.assertEqual(changes["before"], 33)
            self.assertEqual(changes["after"], 121)
            self.assertEqual(changes["source"], "TOPAZ_SLP_PIX_CHUNK_SIZE")

    def test_audit_inside_install_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audit_path = root / "audit.jsonl"
            self.configure(audit_path)
            os.environ["TOPAZ_INSTALL_DIR"] = str(root)
            self.sitecustomize._record("header", {"enabled": True})
            self.assertFalse(audit_path.exists())


if __name__ == "__main__":
    unittest.main()
