from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from driftproof.types import IntentLabel


@dataclass(frozen=True)
class GripperTracePoint:
    t: float
    command: IntentLabel
    position: float


@dataclass(frozen=True)
class FunctionalScore:
    n_steps: int
    mean_target_error: float
    final_target_error: float
    wrong_direction_commands: int
    rest_motion: float


def step_gripper(
    position: float,
    command: IntentLabel,
    *,
    dt_s: float,
    speed_per_s: float = 1.5,
) -> float:
    """Advance a one-degree-of-freedom gripper state by one command."""
    if dt_s < 0:
        raise ValueError("dt_s must be non-negative")
    if speed_per_s < 0:
        raise ValueError("speed_per_s must be non-negative")

    if command == "open":
        position += speed_per_s * dt_s
    elif command == "close":
        position -= speed_per_s * dt_s
    elif command != "rest":
        raise ValueError(f"unknown gripper command: {command}")
    return min(1.0, max(0.0, position))


def replay_commands(
    commands: Iterable[IntentLabel],
    timestamps_s: Iterable[float],
    *,
    initial_position: float = 0.5,
    speed_per_s: float = 1.5,
) -> list[GripperTracePoint]:
    """Replay discrete intent commands into a virtual gripper trace."""
    command_list = list(commands)
    timestamp_list = list(timestamps_s)
    if len(command_list) != len(timestamp_list):
        raise ValueError("commands and timestamps_s must have the same length")
    if not command_list:
        return []

    position = min(1.0, max(0.0, initial_position))
    previous_t = timestamp_list[0]
    trace: list[GripperTracePoint] = []
    for command, t in zip(command_list, timestamp_list, strict=True):
        if t < previous_t:
            raise ValueError("timestamps_s must be monotonic")
        position = step_gripper(
            position,
            command,
            dt_s=t - previous_t,
            speed_per_s=speed_per_s,
        )
        trace.append(GripperTracePoint(t=t, command=command, position=position))
        previous_t = t
    return trace


def score_functional_control(
    predicted_commands: Iterable[IntentLabel],
    target_commands: Iterable[IntentLabel],
    timestamps_s: Iterable[float],
    *,
    initial_position: float = 0.5,
    speed_per_s: float = 1.5,
) -> FunctionalScore:
    """Score predicted commands as one-degree-of-freedom gripper control."""
    predicted = list(predicted_commands)
    target = list(target_commands)
    timestamps = list(timestamps_s)
    if len(predicted) != len(target) or len(predicted) != len(timestamps):
        raise ValueError("predicted_commands, target_commands, and timestamps_s must align")
    if not predicted:
        return FunctionalScore(
            n_steps=0,
            mean_target_error=0.0,
            final_target_error=0.0,
            wrong_direction_commands=0,
            rest_motion=0.0,
        )

    trace = replay_commands(
        predicted,
        timestamps,
        initial_position=initial_position,
        speed_per_s=speed_per_s,
    )
    target_positions = [_target_position(command, initial_position) for command in target]
    errors = [abs(point.position - target_pos) for point, target_pos in zip(trace, target_positions)]
    wrong_direction_commands = sum(
        _is_wrong_direction(predicted_command, target_command)
        for predicted_command, target_command in zip(predicted, target, strict=True)
    )
    rest_motion = sum(
        abs(trace[index].position - trace[index - 1].position)
        for index, target_command in enumerate(target)
        if index > 0 and target_command == "rest"
    )
    return FunctionalScore(
        n_steps=len(predicted),
        mean_target_error=sum(errors) / len(errors),
        final_target_error=errors[-1],
        wrong_direction_commands=wrong_direction_commands,
        rest_motion=rest_motion,
    )


def _target_position(command: IntentLabel, rest_position: float) -> float:
    if command == "open":
        return 1.0
    if command == "close":
        return 0.0
    return rest_position


def _is_wrong_direction(predicted: IntentLabel, target: IntentLabel) -> bool:
    return (target == "open" and predicted == "close") or (
        target == "close" and predicted == "open"
    )
