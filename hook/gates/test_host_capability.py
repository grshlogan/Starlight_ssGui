"""AC-11 host-capability gate.

This gate is `required: true` in the task packet, so it must FAIL — not skip — when the
evidence it asserts does not exist. A required gate that can exit 0 while skipping its only
assertion is not evidence; it is a silent pass.

Evidence contract: `coding/evidence/host-capability.md` must exist and carry
`status: BOUND`, `conclusion: direct|rust-adapter|windows-render-blocked`, and at least one
`command:` / `exit_code:` / `snapshot_sha256:` triple. While B01 is deferred the file records
`status: UNVERIFIED`, and this test fails with an explicit message naming the owner.
"""

import re
import unittest
from pathlib import Path

EVIDENCE_RELATIVE = Path("docs/tasks/stage1-gui-backend/coding/evidence/host-capability.md")
CONCLUSIONS = {"direct", "rust-adapter", "windows-render-blocked"}


class HostCapabilityTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[2]
        self.evidence = self.root / EVIDENCE_RELATIVE

    def test_evidence_exists(self):
        self.assertTrue(
            self.evidence.exists(),
            f"AC-11 evidence is missing at {EVIDENCE_RELATIVE}. B01-host-spike has not run. "
            "Owner: project owner (provide the <SHARED_LEARN_ROOT> read-only mapping), "
            "then A003 writes the evidence. This gate stays red until B01 is done.",
        )

    def test_evidence_is_bound(self):
        if not self.evidence.exists():
            self.fail("AC-11 evidence is missing; see test_evidence_exists for the owner.")
        text = self.evidence.read_text(encoding="utf-8")

        status = self._field(text, "status")
        self.assertEqual(
            status,
            "BOUND",
            f"AC-11 evidence status is {status!r}, so the host-capability conclusion is not "
            "bound. While B01 is deferred this gate must stay red; owner: project owner.",
        )

        conclusion = self._field(text, "conclusion")
        self.assertIn(
            conclusion,
            CONCLUSIONS,
            f"conclusion {conclusion!r} must be one of {sorted(CONCLUSIONS)}",
        )

        self.assertRegex(text, r"(?m)^command:\s*\S.+$")
        self.assertRegex(text, r"(?m)^exit_code:\s*\d+$")
        self.assertRegex(text, r"(?m)^snapshot_sha256:\s*[0-9a-f]{64}$")

    @staticmethod
    def _field(text, name):
        match = re.search(rf"^{name}:\s*(\S+)", text, re.MULTILINE)
        return match.group(1) if match else None


if __name__ == "__main__":
    unittest.main()
