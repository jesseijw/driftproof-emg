from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from driftproof.acquisition.simulated import generate_synthetic_session, write_jsonl
from driftproof.evaluation.reporting import evaluate_session, write_scorecard_report

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
