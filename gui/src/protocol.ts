export type CommandName = "start" | "stop" | "cancel" | "refresh";
export type SessionStatus = "idle" | "starting" | "running" | "completed" | "failed" | "cancelled" | "unknown";

export type ControlCommand = {
  kind: "control_command";
  command: CommandName;
  launch_id?: string;
  payload?: Record<string, unknown>;
};

export type StateSnapshot = {
  kind: "state_snapshot";
  launch_id: string | null;
  status: SessionStatus;
  phase: string | null;
  progress: number | null;
  eta_seconds: number | null;
};

export type StructuredEvent = {
  kind: "structured_event";
  timestamp_utc: string;
  pid: number | null;
  launch_id: string;
  event: string;
  changes: Record<string, unknown>;
};

export type StructuredError = {
  kind: "structured_error";
  code: string;
  message: string;
  recoverable: boolean;
  details: Record<string, unknown>;
};

export type SeamMessage = ControlCommand | StateSnapshot | StructuredEvent | StructuredError;

export type ValidationFailure = {
  code: "invalid_message";
  message: string;
  path: string;
};

export type ParseResult =
  | { ok: true; value: SeamMessage }
  | { ok: false; error: ValidationFailure };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

function isNullableString(value: unknown): value is string | null {
  return value === null || isString(value);
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function fail(path: string, message: string): ParseResult {
  return { ok: false, error: { code: "invalid_message", message, path } };
}

function isCommand(value: unknown): value is CommandName {
  return value === "start" || value === "stop" || value === "cancel" || value === "refresh";
}

function isStatus(value: unknown): value is SessionStatus {
  return value === "idle" || value === "starting" || value === "running" || value === "completed" || value === "failed" || value === "cancelled" || value === "unknown";
}

function validateControl(message: Record<string, unknown>): ParseResult {
  if (!isCommand(message.command)) return fail("command", "unsupported control command");
  if (message.launch_id !== undefined && !isString(message.launch_id)) return fail("launch_id", "launch_id must be a non-empty string");
  if (message.payload !== undefined && !isRecord(message.payload)) return fail("payload", "payload must be an object");
  return { ok: true, value: message as unknown as ControlCommand };
}

function validateSnapshot(message: Record<string, unknown>): ParseResult {
  if (!isNullableString(message.launch_id)) return fail("launch_id", "launch_id must be a string or null");
  if (!isStatus(message.status)) return fail("status", "unsupported session status");
  if (!isNullableString(message.phase)) return fail("phase", "phase must be a string or null");
  if (message.progress !== null && !isFiniteNumber(message.progress)) return fail("progress", "progress must be a finite number or null");
  if (message.progress !== null && (message.progress as number) < 0) return fail("progress", "progress cannot be negative");
  if (message.eta_seconds !== null && !isFiniteNumber(message.eta_seconds)) return fail("eta_seconds", "eta_seconds must be a finite number or null");
  if (message.eta_seconds !== null && (message.eta_seconds as number) < 0) return fail("eta_seconds", "eta_seconds cannot be negative");
  return { ok: true, value: message as unknown as StateSnapshot };
}

function validateEvent(message: Record<string, unknown>): ParseResult {
  if (!isString(message.timestamp_utc)) return fail("timestamp_utc", "timestamp_utc is required");
  if (message.pid !== null && (!Number.isInteger(message.pid) || (message.pid as number) < 0)) return fail("pid", "pid must be a non-negative integer or null");
  if (!isString(message.launch_id)) return fail("launch_id", "launch_id is required");
  if (!isString(message.event)) return fail("event", "event is required");
  if (!isRecord(message.changes)) return fail("changes", "changes must be an object");
  return { ok: true, value: message as unknown as StructuredEvent };
}

function validateError(message: Record<string, unknown>): ParseResult {
  if (!isString(message.code)) return fail("code", "error code is required");
  if (!isString(message.message)) return fail("message", "error message is required");
  if (typeof message.recoverable !== "boolean") return fail("recoverable", "recoverable must be boolean");
  if (message.details !== undefined && !isRecord(message.details)) return fail("details", "details must be an object");
  const normalized = { ...message, details: message.details ?? {} };
  return { ok: true, value: normalized as StructuredError };
}

export function parseMessage(input: unknown): ParseResult {
  if (!isRecord(input)) return fail("message", "message must be an object");
  switch (input.kind) {
    case "control_command":
      return validateControl(input);
    case "state_snapshot":
      return validateSnapshot(input);
    case "structured_event":
      return validateEvent(input);
    case "structured_error":
      return validateError(input);
    default:
      return fail("kind", "unknown seam message kind");
  }
}

export function isSeamMessage(input: unknown): input is SeamMessage {
  return parseMessage(input).ok;
}
