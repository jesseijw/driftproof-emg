from __future__ import annotations

from pathlib import Path
from typing import cast

import typer
from rich.console import Console
from rich.table import Table

from driftproof.acquisition.capture import CaptureConfig, capture_lines_to_jsonl
from driftproof.acquisition.simulated import generate_synthetic_session, write_jsonl
from driftproof.evaluation.reporting import evaluate_session, write_scorecard_report
from driftproof.experiments.manifest import ManifestError, run_manifest
from driftproof.types import IntentLabel

app = typer.Typer(help="DriftProof EMG research platform")
console = Console()


@app.command()
def simulate(
    out: Path = typer.Option(Path("data/demo/session.jsonl"), help="Output JSONL path"),
    seconds: float = typer.Option(24.0, help="Session duration"),
    drift_after_s: float = typer.Option(12.0, help="Time when synthetic drift begins"),
    sample_rate_hz: int = typer.Option(1_000, help="Sample rate"),
    seed: int = typer.Option(42, help="Random seed"),
) -> None:
    """Generate a synthetic baseline/drift EMG session."""
    samples = generate_synthetic_session(
        seconds=seconds,
        sample_rate_hz=sample_rate_hz,
        drift_after_s=drift_after_s,
        seed=seed,
    )
    write_jsonl(samples, out)
    console.print(f"Wrote {len(samples)} samples to [bold]{out}[/bold]")


@app.command("capture-file")
def capture_file(
    source: Path = typer.Argument(..., help="Raw firmware JSONL input"),
    out: Path = typer.Option(Path("data/raw/session.jsonl"), help="Normalized session JSONL path"),
    session_id: str = typer.Option("capture", help="Session id to apply when missing"),
    sample_rate_hz: int = typer.Option(1_000, help="Sample rate for timestamp synthesis"),
    label: str = typer.Option("rest", help="Label to apply when missing"),
    condition: str = typer.Option("baseline", help="Condition to apply when missing"),
) -> None:
    """Normalize firmware-style capture logs into replayable session JSONL."""
    if label not in {"rest", "open", "close"}:
        raise typer.BadParameter("label must be one of: rest, open, close")
    intent_label = cast(IntentLabel, label)
    with source.open("r", encoding="utf-8") as f:
        count = capture_lines_to_jsonl(
            f,
            out,
            CaptureConfig(
                session_id=session_id,
                sample_rate_hz=sample_rate_hz,
                label=intent_label,
                condition=condition,
            ),
        )
    console.print(f"Wrote {count} EMG samples to [bold]{out}[/bold]")


@app.command("run-manifest")
def run_experiment_manifest(
    manifest: Path = typer.Argument(..., help="Experiment manifest JSON path"),
) -> None:
    """Run an evaluation from a versioned experiment manifest."""
    try:
        report = run_manifest(manifest)
    except ManifestError as exc:
        raise typer.BadParameter(str(exc)) from exc
    experiment = report["experiment"]
    console.print(
        f"Ran [bold]{experiment['name']}[/bold] and wrote [bold]{experiment['report_path']}[/bold]"
    )


@app.command()
def evaluate(
    path: Path = typer.Argument(..., help="Session JSONL path"),
    window_ms: int = typer.Option(200, help="Window size"),
    step_ms: int = typer.Option(100, help="Window step"),
    sample_rate_hz: int = typer.Option(1_000, help="Sample rate"),
    report: Path | None = typer.Option(None, help="Optional JSON scorecard output path"),
    adaptation: bool = typer.Option(True, help="Compare normalization adaptation on drifted replay"),
) -> None:
    """Train on baseline windows and evaluate on drifted windows."""
    try:
        scorecard = evaluate_session(
            path,
            window_ms=window_ms,
            step_ms=step_ms,
            sample_rate_hz=sample_rate_hz,
            adaptation_enabled=adaptation,
        )
    except ValueError as exc:
        raise typer.BadParameter("session must include both baseline and drifted windows") from exc
    if report is not None:
        write_scorecard_report(scorecard, report)

    table = Table(title="DriftProof Synthetic Scorecard")
    table.add_column("Split")
    table.add_column("Windows", justify="right")
    table.add_column("Accuracy", justify="right")
    table.add_column("Macro F1", justify="right")
    table.add_column("Mean drift score", justify="right")
    for split_name in scorecard["splits"]:
        split = scorecard["splits"][split_name]
        mean_drift = split["drift_score_mean"]
        table.add_row(
            split_name,
            str(split["n_windows"]),
            f"{split['accuracy']:.3f}",
            f"{split['macro_f1']:.3f}",
            "-" if mean_drift is None else f"{mean_drift:.2f}",
        )
    console.print(table)
    if report is not None:
        console.print(f"Wrote scorecard report to [bold]{report}[/bold]")


if __name__ == "__main__":
    app()
