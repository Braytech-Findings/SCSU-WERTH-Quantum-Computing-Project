from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "submit_quantinuum_validation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("quantinuum_validation", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def module():
    return load_module()


def test_matched_suite_has_exact_seven_circuit_order(module) -> None:
    circuits = module.build_validation_suite("matched")
    assert [circuit.name for circuit in circuits] == [
        "bell_state",
        "ghz_3",
        "ghz_5",
        "ghz_7",
        "grover_search_2",
        "qft_3",
        "qft_5",
    ]


def test_manifest_stably_maps_indices_to_circuit_ids(module) -> None:
    manifest = module.circuit_manifest(module.build_validation_suite("matched"))
    assert [(row["circuit_index"], row["circuit_id"]) for row in manifest] == [
        (0, "bell_state"),
        (1, "ghz_3"),
        (2, "ghz_5"),
        (3, "ghz_7"),
        (4, "grover_search_2"),
        (5, "qft_3"),
        (6, "qft_5"),
    ]


@pytest.mark.parametrize(
    ("circuit_id", "counts"),
    [
        ("bell_state", {"00": 500, "11": 500}),
        ("ghz_7", {"0000000": 500, "1111111": 500}),
        ("grover_search_2", {"11": 1000}),
        ("qft_3", {f"{value:03b}": 125 for value in range(8)}),
        ("qft_5", {f"{value:05b}": 32 for value in range(8)} | {f"{value:05b}": 31 for value in range(8, 32)}),
    ],
)
def test_perfect_synthetic_scoring(module, circuit_id: str, counts: dict[str, int]) -> None:
    row = next(
        item
        for item in module.circuit_manifest(module.build_validation_suite("matched"))
        if item["circuit_id"] == circuit_id
    )
    # Use exact probabilities so the 5-qubit uniform case is not distorted by 1,000 shots.
    scale = 3200 if circuit_id == "qft_5" else sum(counts.values())
    if circuit_id == "qft_5":
        counts = {f"{value:05b}": 100 for value in range(32)}
    score = module.score_counts(counts, row, scale)
    assert score["distribution_fidelity"] == pytest.approx(1.0)
    assert score["total_variation_distance"] == pytest.approx(0.0)
    if circuit_id.startswith("qft"):
        assert score["all_zero_or_all_one_probability"] is None
        assert score["marked_state_probability"] is None


def test_intentionally_wrong_bell_counts_are_penalized(module) -> None:
    row = module.circuit_manifest(module.build_validation_suite("matched"))[0]
    score = module.score_counts({"01": 1000}, row, 1000)
    assert score["distribution_fidelity"] == 0
    assert score["total_variation_distance"] == 1


def test_tuple_bit_order_is_preserved_and_padded(module) -> None:
    assert module.normalize_bitstring((1, 0, 1), 3) == "101"
    assert module.normalize_bitstring("1", 3) == "001"
    assert module.normalize_bitstring("0x5", 3) == "101"


@pytest.mark.parametrize("counts", [None, {}, {"bad": 1}, {"00": -1}, {"00": 1.5}])
def test_malformed_or_missing_counts_are_rejected(module, counts) -> None:
    row = module.circuit_manifest(module.build_validation_suite("matched"))[0]
    with pytest.raises(ValueError):
        module.score_counts(counts, row)


def test_shot_total_mismatch_is_rejected(module) -> None:
    row = module.circuit_manifest(module.build_validation_suite("matched"))[0]
    with pytest.raises(ValueError, match="Retrieved 10 shots; expected 1000"):
        module.score_counts({"00": 5, "11": 5}, row, 1000)


def test_target_classification_and_quota_gate(module) -> None:
    assert module.classify_target("H2-1LE") == "emulator"
    assert module.classify_target("H2-Emulator") == "emulator"
    assert module.classify_target("H2-1E") == "compile_only_access_restricted"
    assert module.classify_target("H2-1") == "physical_qpu_refused"
    assert module.classify_target("mystery") == "unknown_refused"
    review = {"static_classification": "emulator", "catalog_confirms_emulator": True}
    assert module.execution_is_safe(review, [], None)[0] is False
    assert module.execution_is_safe(review, [{"reported_cost": 1}], "institutional quota")[0] is False
    assert module.execution_is_safe(review, [{"reported_cost": None}], "institutional simulator quota")[0]


def test_repetitions_and_timestamped_non_overwriting_dry_run(tmp_path: Path) -> None:
    command = [
        sys.executable,
        str(SCRIPT),
        "--dry-run",
        "--target",
        "H2-1LE",
        "--suite",
        "matched",
        "--shots",
        "1000",
        "--repetitions",
        "3",
        "--output-dir",
        str(tmp_path),
    ]
    result = subprocess.run(command, check=False, capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0
    paths = list(tmp_path.glob("quantinuum_run_manifest_H2-1LE_*.json"))
    assert len(paths) == 1
    plan = json.loads(paths[0].read_text(encoding="utf-8"))
    assert plan["circuit_count"] == 7
    assert plan["repetitions"] == 3
    assert plan["total_requested_shots"] == 21000
    with pytest.raises(FileExistsError):
        module = load_module()
        module._write_json_new(paths[0], {})


def test_legacy_small_suite_artifacts_remain_readable() -> None:
    legacy = ROOT / "results/hardware/quantinuum_job_H2-1LE_20260714T173914Z.json"
    payload = json.loads(legacy.read_text(encoding="utf-8"))
    assert payload["target"] == "H2-1LE"
    assert len(payload["results"]) == 3
