import contextlib
import importlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock


class FailsafeTests(unittest.TestCase):
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

    def test_failsafe_import_failure_matches_native_import_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = root / "models" / "slp2"
            package.mkdir(parents=True)
            (root / "models" / "__init__.py").write_text("", encoding="utf-8")
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "broken.py").write_text(
                "PARTIAL = True\nraise RuntimeError('target import failure')\n",
                encoding="utf-8",
            )
            (package / "healthy.py").write_text("VALUE = 42\n", encoding="utf-8")
            audit_path = root / "audit.jsonl"
            self.configure(audit_path)
            importlib.reload(self.sitecustomize)
            sys.path.insert(0, str(root))
            module_names = ["models.slp2.broken", "models.slp2.healthy", "models.slp2", "models"]
            try:
                importlib.invalidate_caches()
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    with self.assertRaises(RuntimeError) as raised:
                        importlib.import_module("models.slp2.broken")
                self.assertIs(type(raised.exception), RuntimeError)
                self.assertTrue(stderr.getvalue().startswith(self.sitecustomize.ERROR_PREFIX + " "))
                import_error = next(
                    event
                    for event in self.read_events(audit_path)
                    if event.get("event") == "error"
                    and event.get("changes", {}).get("stage") == "import"
                )
                self.assertEqual(import_error["changes"]["stage"], "import")
                self.assertEqual(import_error["changes"]["error_type"], "RuntimeError")
                self.assertIn("target import failure", import_error["changes"]["error"])
                self.assertNotIn("models.slp2.broken", sys.modules)
                healthy = importlib.import_module("models.slp2.healthy")
                self.assertEqual(healthy.VALUE, 42)
            finally:
                sys.path.remove(str(root))
                for name in module_names:
                    sys.modules.pop(name, None)

    def test_failsafe_contract_failure_keeps_target_importable_and_records_error(self):
        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit.jsonl"
            self.configure(audit_path)
            importlib.reload(self.sitecustomize)
            module = ModuleType("models.slp25.synthetic")
            module.PIX_CHUNK_SIZE = 33
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertFalse(self.sitecustomize.apply_overrides(module))
            self.assertTrue(self.sitecustomize.ERROR_PREFIX)
            self.assertTrue(stderr.getvalue().startswith(self.sitecustomize.ERROR_PREFIX + " "))
            self.assertEqual(module.PIX_CHUNK_SIZE, 33)
            self.assertEqual(self.read_events(audit_path)[-1]["event"], "error")

    def test_failsafe_setattr_failure_is_fail_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit.jsonl"
            self.configure(audit_path)
            importlib.reload(self.sitecustomize)
            module = self.target_module()
            with mock.patch.object(self.sitecustomize, "_set_attribute", side_effect=RuntimeError("setattr")):
                self.assertFalse(self.sitecustomize.apply_overrides(module))
            self.assertEqual(module.PIX_CHUNK_SIZE, 33)
            self.assertEqual(self.read_events(audit_path)[-1]["event"], "error")

    def test_failsafe_setattr_failure_on_second_change_rolls_back_all(self):
        with tempfile.TemporaryDirectory() as directory:
            audit_path = Path(directory) / "audit.jsonl"
            self.configure(audit_path)
            os.environ["TOPAZ_SLP_VAE_DECODE_TILE_SIZE"] = "480"
            importlib.reload(self.sitecustomize)
            module = self.target_module()
            original = (module.PIX_CHUNK_SIZE, module.VAE_DECODE_TILE_SIZE)
            calls = 0

            def fail_on_second_set(target, name, value):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise RuntimeError("setattr on second change")
                setattr(target, name, value)

            with mock.patch.object(self.sitecustomize, "_set_attribute", side_effect=fail_on_second_set):
                self.assertFalse(self.sitecustomize.apply_overrides(module))
            self.assertEqual((module.PIX_CHUNK_SIZE, module.VAE_DECODE_TILE_SIZE), original)
            events = self.read_events(audit_path)
            self.assertEqual([event["event"] for event in events], ["header", "rollback", "error"])
            self.assertEqual(events[1]["changes"]["attributes"], ["PIX_CHUNK_SIZE"])

    def test_failsafe_audit_write_failure_is_fail_safe(self):
        module = self.target_module()
        os.environ.update(
            {
                "TOPAZ_SLP_OVERRIDE_ENABLE": "1",
                "TOPAZ_SLP_PIX_CHUNK_SIZE": "121",
            }
        )
        with mock.patch.object(self.sitecustomize, "_write_audit_line", side_effect=OSError("audit unavailable")):
            self.assertTrue(self.sitecustomize.apply_overrides(module))
        self.assertEqual(module.PIX_CHUNK_SIZE, 121)


if __name__ == "__main__":
    unittest.main()
