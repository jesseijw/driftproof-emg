from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from driftproof.evaluation.reporting import evaluate_session, write_scorecard_report


@dataclass(frozen=True)
class EvaluationConfig:
    window_ms: int = 200
    step_ms: int = 100
    sample_rate_hz: int = 1_000


@dataclass(frozen=True)
class AdaptationConfig:
    enabled: bool = True
    confidence_threshold: float = 0.6
    momentum: float = 0.02


@dataclass(frozen=True)
class ExperimentManifest:
    name: str
    session_path: Path
    report_path: Path
    evaluation: EvaluationConfig
    adaptation: AdaptationConfig
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["session_path"] = str(self.session_path.resolve())
        data["report_path"] = str(self.report_path.resolve())
        return data


class ManifestError(ValueError):
    """Raised when an experiment manifest is invalid."""


def load_manifest(path: str | Path) -> ExperimentManifest:
    manifest_path = Path(path)
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"{manifest_path}: invalid JSON: {exc.msg}") from exc
    if not isinstance(raw, dict):
        raise ManifestError(f"{manifest_path}: manifest must be a JSON object")
    return parse_manifest(raw, base_dir=manifest_path.parent)


def parse_manifest(raw: dict[str, Any], *, base_dir: Path | None = None) -> ExperimentManifest:
    base = base_dir or Path.cwd()
    name = _required_string(raw, "name")
    session_path = _path_field(raw, "session_path", base)
    report_path = _path_field(raw, "report_path", base)
    evaluation = _evaluation_config(raw.get("evaluation", {}))
    adaptation = _adaptation_config(raw.get("adaptation", {}))
    notes = _optional_string(raw, "notes", "")
    return ExperimentManifest(
        name=name,
        session_path=session_path,
        report_path=report_path,
        evaluation=evaluation,
        adaptation=adaptation,
        notes=notes,
    )


def run_manifest(path: str | Path) -> dict[str, Any]:
    manifest = load_manifest(path)
    report = evaluate_session(
        manifest.session_path,
        window_ms=manifest.evaluation.window_ms,
        step_ms=manifest.evaluation.step_ms,
        sample_rate_hz=manifest.evaluation.sample_rate_hz,
        adaptation_enabled=manifest.adaptation.enabled,
        adaptation_confidence_threshold=manifest.adaptation.confidence_threshold,
        adaptation_momentum=manifest.adaptation.momentum,
    )
    report["experiment"] = manifest.to_dict()
    write_scorecard_report(report, manifest.report_path)
    return report


def _evaluation_config(raw: Any) -> EvaluationConfig:
    if not isinstance(raw, dict):
        raise ManifestError("field 'evaluation' must be an object")
    return EvaluationConfig(
        window_ms=_positive_int(raw, "window_ms", 200),
        step_ms=_positive_int(raw, "step_ms", 100),
        sample_rate_hz=_positive_int(raw, "sample_rate_hz", 1_000),
    )


def _adaptation_config(raw: Any) -> AdaptationConfig:
    if not isinstance(raw, dict):
        raise ManifestError("field 'adaptation' must be an object")
    enabled = raw.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ManifestError("field 'adaptation.enabled' must be a boolean")
    confidence_threshold = _float_range(raw, "confidence_threshold", 0.6, lower=0.0, upper=1.0)
    momentum = _float_range(raw, "momentum", 0.02, lower=0.0, upper=1.0)
    return AdaptationConfig(
        enabled=enabled,
        confidence_threshold=confidence_threshold,
        momentum=momentum,
    )


def _required_string(raw: dict[str, Any], field_name: str) -> str:
    value = raw.get(field_name)
    if not isinstance(value, str) or not value:
        raise ManifestError(f"field '{field_name}' must be a non-empty string")
    return value


def _optional_string(raw: dict[str, Any], field_name: str, default: str) -> str:
    value = raw.get(field_name, default)
    if not isinstance(value, str):
        raise ManifestError(f"field '{field_name}' must be a string")
    return value


def _path_field(raw: dict[str, Any], field_name: str, base_dir: Path) -> Path:
    value = _required_string(raw, field_name)
    path = Path(value)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _positive_int(raw: dict[str, Any], field_name: str, default: int) -> int:
    value = raw.get(field_name, default)
    if not isinstance(value, int) or value <= 0:
        raise ManifestError(f"field '{field_name}' must be a positive integer")
    return value


def _float_range(
    raw: dict[str, Any],
    field_name: str,
    default: float,
    *,
    lower: float,
    upper: float,
) -> float:
    value = raw.get(field_name, default)
    if not isinstance(value, int | float):
        raise ManifestError(f"field '{field_name}' must be numeric")
    numeric = float(value)
    if numeric < lower or numeric > upper:
        raise ManifestError(f"field '{field_name}' must be between {lower} and {upper}")
    return numeric
