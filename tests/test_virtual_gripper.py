from __future__ import annotations

import pytest

from driftproof.control.virtual_gripper import (
    replay_commands,
    score_functional_control,
    step_gripper,
)


def test_step_gripper_clamps_position() -> None:
    assert step_gripper(0.95, "open", dt_s=1.0, speed_per_s=1.5) == 1.0
    assert step_gripper(0.05, "close", dt_s=1.0, speed_per_s=1.5) == 0.0
    assert step_gripper(0.4, "rest", dt_s=1.0, speed_per_s=1.5) == 0.4


def test_replay_commands_tracks_position_over_time() -> None:
    trace = replay_commands(
        ["open", "open", "close"],
        [0.0, 0.5, 1.0],
        initial_position=0.5,
        speed_per_s=1.0,
    )

    assert [point.position for point in trace] == [0.5, 1.0, 0.5]


def test_replay_commands_rejects_timestamp_regression() -> None:
    with pytest.raises(ValueError, match="monotonic"):
        replay_commands(["open", "close"], [1.0, 0.5])


def test_functional_score_counts_wrong_direction_commands() -> None:
    score = score_functional_control(
        predicted_commands=["close", "open", "rest"],
        target_commands=["open", "close", "rest"],
        timestamps_s=[0.0, 0.5, 1.0],
        initial_position=0.5,
        speed_per_s=1.0,
    )

    assert score.n_steps == 3
    assert score.wrong_direction_commands == 2
    assert score.mean_target_error > 0
    assert score.rest_motion == 0
