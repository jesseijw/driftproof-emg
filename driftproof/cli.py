from __future__ import annotations

from pathlib import Path

import numpy as np
import typer
from rich.console import Console
from rich.table import Table

from driftproof.acquisition.simulated import generate_synthetic_session, read_jsonl, write_jsonl
from driftproof.drift.mahalanobis import fit_reference, score
from driftproof.evaluation.metrics import classify_scorecard
from driftproof.features.classical import extract_many, feature_matrix
from driftproof.models.baseline import train_baseline
from driftproof.preprocessing.windowing import make_windows

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
) -> None:
    """Train on baseline windows and evaluate on drifted windows."""
    samples = read_jsonl(path)
    windows = make_windows(
        samples,
        window_ms=window_ms,
        step_ms=step_ms,
        sample_rate_hz=sample_rate_hz,
    )
    rows = extract_many(windows)
    x, y, condition = feature_matrix(rows)
    train_mask = condition == "baseline"
    test_mask = condition == "drifted"
    if not train_mask.any() or not test_mask.any():
        raise typer.BadParameter("session must include both baseline and drifted windows")

    model = train_baseline(x[train_mask], y[train_mask])
    pred_baseline = model.predict(x[train_mask])
    pred_drifted = model.predict(x[test_mask])

    ref = fit_reference(x[train_mask])
    drift_scores = score(ref, x[test_mask])

    base_score = classify_scorecard(y[train_mask], pred_baseline)
    drift_scorecard = classify_scorecard(y[test_mask], pred_drifted, drift_scores=drift_scores)

    table = Table(title="DriftProof Synthetic Scorecard")
    table.add_column("Split")
    table.add_column("Windows", justify="right")
    table.add_column("Accuracy", justify="right")
    table.add_column("Macro F1", justify="right")
    table.add_column("Mean drift score", justify="right")
    table.add_row(
        "baseline",
        str(base_score.n_windows),
        f"{base_score.accuracy:.3f}",
        f"{base_score.macro_f1:.3f}",
        "-",
    )
    table.add_row(
        "drifted",
        str(drift_scorecard.n_windows),
        f"{drift_scorecard.accuracy:.3f}",
        f"{drift_scorecard.macro_f1:.3f}",
        f"{np.mean(drift_scores):.2f}",
    )
    console.print(table)


if __name__ == "__main__":
    app()
