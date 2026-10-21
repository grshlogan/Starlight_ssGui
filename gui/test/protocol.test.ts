import { test } from "node:test";
import assert from "node:assert/strict";
import { isSeamMessage, parseMessage } from "../src/protocol.ts";

test("accepts all four seam message kinds", () => {
  const messages = [
    { kind: "control_command", command: "start", launch_id: "launch-1" },
    { kind: "state_snapshot", launch_id: "launch-1", status: "running", phase: "VAE Encode", progress: 20, eta_seconds: null },
    { kind: "structured_event", timestamp_utc: "2026-10-19T10:00:00.000Z", pid: 42, launch_id: "launch-1", event: "apply", changes: { PIX_CHUNK_SIZE: 121 } },
    { kind: "structured_error", code: "hook_missing", message: "hook is unavailable", recoverable: true, details: {} },
  ];
  for (const message of messages) {
    const result = parseMessage(message);
    assert.equal(result.ok, true);
    assert.equal(isSeamMessage(message), true);
  }
});

test("rejects malformed commands and preserves a structured error", () => {
  const result = parseMessage({ kind: "control_command", command: "launch" });
  assert.deepEqual(result, {
    ok: false,
    error: { code: "invalid_message", message: "unsupported control command", path: "command" },
  });
});

test("rejects fabricated progress and invalid error payloads", () => {
  const negative = parseMessage({ kind: "state_snapshot", launch_id: null, status: "running", phase: null, progress: -1, eta_seconds: null });
  assert.equal(negative.ok, false);
  const badError = parseMessage({ kind: "structured_error", code: "x", message: "bad", recoverable: "yes" });
  assert.equal(badError.ok, false);
});

test("rejects structured events missing required fields", () => {
  const missingChanges = parseMessage({
    kind: "structured_event",
    timestamp_utc: "2026-10-19T10:00:00.000Z",
    pid: 42,
    launch_id: "launch-1",
    event: "apply",
  });
  const missingTimestamp = parseMessage({
    kind: "structured_event",
    pid: 42,
    launch_id: "launch-1",
    event: "apply",
    changes: {},
  });
  assert.deepEqual(missingChanges, {
    ok: false,
    error: { code: "invalid_message", message: "changes must be an object", path: "changes" },
  });
  assert.deepEqual(missingTimestamp, {
    ok: false,
    error: { code: "invalid_message", message: "timestamp_utc is required", path: "timestamp_utc" },
  });
});

test("rejects unknown seam message kinds with a structured error", () => {
  assert.deepEqual(parseMessage({ kind: "future_message" }), {
    ok: false,
    error: { code: "invalid_message", message: "unknown seam message kind", path: "kind" },
  });
});

test("accepts unknown values only through explicit nullable fields", () => {
  const snapshot = parseMessage({ kind: "state_snapshot", launch_id: null, status: "unknown", phase: null, progress: null, eta_seconds: null });
  assert.equal(snapshot.ok, true);
  const badPhase = parseMessage({ kind: "state_snapshot", launch_id: null, status: "unknown", phase: 1, progress: null, eta_seconds: null });
  assert.equal(badPhase.ok, false);
});
