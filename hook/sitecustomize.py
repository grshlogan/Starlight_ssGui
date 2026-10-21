"""Fail-safe, stdlib-only SLP parameter hook loaded through PYTHONPATH."""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from types import ModuleType
from typing import Any

ERROR_PREFIX = "[Starlight hook]"
_REQUIRED_ATTRIBUTES = ("PIX_CHUNK_SIZE", "VAE_DECODE_TILE_SIZE")
_ENV_TO_ATTRIBUTE = {
    "TOPAZ_SLP_PIX_CHUNK_SIZE": "PIX_CHUNK_SIZE",
    "TOPAZ_SLP_PIX_OVERLAP": "PIX_OVERLAP",
    "SLP25_VAE_CONV_MAX_MEM": "VAE_CONV_MAX_MEM",
    "TOPAZ_SLP_VAE_ENCODE_TILE_SIZE": "VAE_ENCODE_TILE_SIZE",
    "TOPAZ_SLP_VAE_DECODE_TILE_SIZE": "VAE_DECODE_TILE_SIZE",
    "TOPAZ_SLP_VAE_ENCODE_TILE_OVERLAP": "VAE_ENCODE_TILE_OVERLAP",
    "TOPAZ_SLP_VAE_DECODE_TILE_OVERLAP": "VAE_DECODE_TILE_OVERLAP",
    "TOPAZ_SLP_VAE_ENCODE_TILED": "VAE_ENCODE_TILED",
    "TOPAZ_SLP_VAE_DECODE_TILED": "VAE_DECODE_TILED",
    "TOPAZ_SLP_CAUSAL_SPLIT_SIZE": "CAUSAL_SPLIT_SIZE",
    "SLP25_DIT_BLOCK_CHUNK": "DIT_BLOCK_CHUNK",
    "SLP25_DIT_MLP_CHUNK": "DIT_MLP_CHUNK",
    "SLP25_DIT_WIN_GROUP": "DIT_WIN_GROUP",
    "TOPAZ_SLP_COLOR_CORRECTION": "COLOR_CORRECTION",
    "TOPAZ_SLP_FULL_POOL": "FULL_POOL",
    "TOPAZ_SLP_THREADED_PREFLIGHT": "THREADED_PREFLIGHT",
    "TOPAZ_SLP_FORCE_ATTENTION": "FORCE_ATTENTION",
}


class ContractError(RuntimeError):
    """The imported module is not a supported SLP target."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _launch_id() -> str:
    return os.environ.get("TOPAZ_SLP_LAUNCH_ID") or uuid.uuid4().hex


def _install_path_forbidden(path: str) -> bool:
    install_dir = os.environ.get("TOPAZ_INSTALL_DIR")
    if not install_dir:
        return False
    try:
        return os.path.commonpath((os.path.abspath(path), os.path.abspath(install_dir))) == os.path.abspath(install_dir)
    except ValueError:
        return False


def _event(event: str, changes: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp_utc": _utc_timestamp(),
        "pid": os.getpid(),
        "launch_id": _launch_id(),
        "event": event,
        "changes": changes,
    }


def _write_audit_line(event: str, changes: dict[str, Any]) -> None:
    path = os.environ.get("TOPAZ_SLP_OVERRIDE_AUDIT_FILE")
    if not path:
        return
    if _install_path_forbidden(path):
        raise PermissionError("audit path is inside TOPAZ_INSTALL_DIR")
    with open(path, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(_event(event, changes), sort_keys=True, separators=(",", ":")))
        stream.write("\n")


def _stderr(stage: str, error: BaseException) -> None:
    print(f"{ERROR_PREFIX} {stage}: {type(error).__name__}: {error}", file=sys.stderr)


def _record(event: str, changes: dict[str, Any]) -> None:
    try:
        _write_audit_line(event, changes)
    except Exception as error:  # noqa: BLE001 - fail-safe boundary
        _stderr("audit", error)


def _record_error(stage: str, error: BaseException) -> None:
    details = {"stage": stage, "error_type": type(error).__name__, "error": str(error)}
    _stderr(stage, error)
    _record("error", details)


def _matches_target(module_name: str) -> bool:
    exact = os.environ.get("TOPAZ_SLP_TARGET_MODULE_NAME")
    if exact:
        return module_name == exact
    return module_name.startswith("models.slp2")


def _validate_contract(module: ModuleType) -> None:
    missing = [name for name in _REQUIRED_ATTRIBUTES if not hasattr(module, name)]
    if missing:
        raise ContractError(f"missing contract attributes: {','.join(missing)}")


def _coerce(value: str, old_value: Any) -> Any:
    if isinstance(old_value, bool):
        if value not in {"0", "1"}:
            raise ValueError(f"boolean override must be 0 or 1: {value}")
        return value == "1"
    if isinstance(old_value, int) and not isinstance(old_value, bool):
        return int(value)
    if isinstance(old_value, float):
        return float(value)
    return value


def _set_attribute(module: ModuleType, name: str, value: Any) -> None:
    setattr(module, name, value)


def _requested_changes(module: ModuleType) -> dict[str, Any]:
    pending: list[tuple[str, str, Any, Any]] = []
    for environment_name, attribute_name in _ENV_TO_ATTRIBUTE.items():
        raw = os.environ.get(environment_name)
        if raw is None:
            continue
        old_value = getattr(module, attribute_name)
        new_value = _coerce(raw, old_value)
        pending.append((environment_name, attribute_name, old_value, new_value))

    changes = {
        attribute_name: {"before": old_value, "after": new_value, "source": environment_name}
        for environment_name, attribute_name, old_value, new_value in pending
    }
    applied: list[tuple[str, Any]] = []
    try:
        for _, attribute_name, old_value, new_value in pending:
            _set_attribute(module, attribute_name, new_value)
            applied.append((attribute_name, old_value))
    except Exception as error:  # noqa: BLE001 - rollback is part of the fail-safe boundary
        rolled_back: list[str] = []
        rollback_error: BaseException | None = None
        for attribute_name, old_value in reversed(applied):
            try:
                _set_attribute(module, attribute_name, old_value)
                rolled_back.append(attribute_name)
            except Exception as rollback_failure:  # noqa: BLE001 - preserve the original failure
                rollback_error = rollback_failure
                break
        rollback_details: dict[str, Any] = {
            "attributes": rolled_back,
            "error_type": type(error).__name__,
            "error": str(error),
        }
        if rollback_error is not None:
            rollback_details["rollback_error_type"] = type(rollback_error).__name__
            rollback_details["rollback_error"] = str(rollback_error)
        _record("rollback", rollback_details)
        raise
    return changes


def apply_overrides(module: ModuleType, module_name: str | None = None) -> bool:
    """Apply requested changes while converting every hook failure to an error event."""
    name = module_name or getattr(module, "__name__", "")
    if os.environ.get("TOPAZ_SLP_OVERRIDE_ENABLE") != "1" or not _matches_target(name):
        return False
    try:
        _validate_contract(module)
        changes = _requested_changes(module)
        if not changes:
            return False
        _record("apply", changes)
        return True
    except Exception as error:  # noqa: BLE001 - target import must remain native
        _record_error("apply", error)
        return False


class _LoaderProxy:
    def __init__(self, loader: Any, module_name: str) -> None:
        self._loader = loader
        self._module_name = module_name

    def create_module(self, spec: Any) -> ModuleType | None:
        create = getattr(self._loader, "create_module", None)
        return create(spec) if create is not None else None

    def exec_module(self, module: ModuleType) -> None:
        try:
            self._loader.exec_module(module)
        except Exception as error:  # noqa: BLE001 - preserve target process availability
            _record_error("import", error)
            raise
        apply_overrides(module, self._module_name)


class _TargetFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname: str, path: Any, target: ModuleType | None = None) -> Any:
        if not _matches_target(fullname):
            return None
        try:
            spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
            if spec is not None and spec.loader is not None and hasattr(spec.loader, "exec_module"):
                spec.loader = _LoaderProxy(spec.loader, fullname)
            return spec
        except Exception as error:  # noqa: BLE001 - fail-safe installation boundary
            _record_error("import", error)
            return None


_FINDER = _TargetFinder()
_INSTALLED = False


def install_import_hook() -> bool:
    global _INSTALLED
    if _INSTALLED:
        return True
    try:
        sys.meta_path.insert(0, _FINDER)
        _INSTALLED = True
        return True
    except Exception as error:  # noqa: BLE001 - native fallback boundary
        _record_error("install", error)
        return False


def _bootstrap() -> None:
    _record("header", {"enabled": os.environ.get("TOPAZ_SLP_OVERRIDE_ENABLE") == "1"})
    if os.environ.get("TOPAZ_SLP_OVERRIDE_ENABLE") == "1":
        install_import_hook()


_bootstrap()
