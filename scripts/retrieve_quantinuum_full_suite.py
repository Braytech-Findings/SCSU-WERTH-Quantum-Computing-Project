#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import qnexus as qnx

import submit_quantinuum_validation as validation


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Retrieve existing full-suite emulator jobs.")
    result.add_argument("--target", required=True, choices=sorted(validation.EXECUTABLE_EMULATORS))
    result.add_argument("--stamp", required=True)
    result.add_argument("--shots", type=int, default=1000)
    result.add_argument("--repetitions", type=int, default=3)
    result.add_argument("--output-dir", default="results/hardware")
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parser().parse_args()
    output = Path(args.output_dir)
    project = qnx.projects.get(name="SCSU WERTH Quantum Validation")
    circuits = validation.build_validation_suite("matched")
    manifest = validation.circuit_manifest(circuits)
    all_rows: list[dict[str, Any]] = []
    job_names = []
    for repetition in range(1, args.repetitions + 1):
        job_name = f"execute-{args.target}-matched-r{repetition}-{args.stamp}"
        saved_path = output / f"quantinuum_full_suite_{args.target}_{args.stamp}_r{repetition}.json"
        if saved_path.exists():
            saved = json.loads(saved_path.read_text(encoding="utf-8"))
            all_rows.extend(saved["results"])
            job_names.append(job_name)
            print(f"Reused validated artifact for {job_name}", flush=True)
            continue
        job = qnx.jobs.get(name=job_name, project=project)
        status = qnx.jobs.status(job)
        if str(status.status).split(".")[-1] != "COMPLETED":
            raise RuntimeError(f"{job_name} is {status.status}: {status.message}")
        refs: Any = qnx.jobs.results(job)  # type: ignore[call-overload]
        if len(refs) != 7:
            raise RuntimeError(f"{job_name} returned {len(refs)} results instead of 7.")
        run_rows = []
        for index, (ref, identity) in enumerate(zip(refs, manifest, strict=True)):
            result = ref.download_result()
            scored = validation.score_counts(result.get_counts(), identity, args.shots)
            row = {
                "target": args.target,
                "target_classification": "emulator",
                "evidence_type": "emulator",
                "repetition": repetition,
                "execute_job_name": job_name,
                "circuit_index": index,
                "circuit_id": identity["circuit_id"],
                "display_name": identity["display_name"],
                "algorithm_family": identity["algorithm_family"],
                "shots_requested": args.shots,
                "shots_retrieved": scored["shots_retrieved"],
                "distribution_fidelity": scored["distribution_fidelity"],
                "total_variation_distance": scored["total_variation_distance"],
                "all_zero_or_all_one_probability": scored["all_zero_or_all_one_probability"],
                "marked_state_probability": scored["marked_state_probability"],
                "distinct_outcomes": scored["distinct_outcomes"],
                "counts_json": json.dumps(scored["counts"], sort_keys=True),
                "ideal_distribution_json": json.dumps(identity["ideal_distribution"], sort_keys=True),
            }
            run_rows.append(row)
        all_rows.extend(run_rows)
        validation.write_result_artifacts(
            {
                "target": args.target,
                "target_classification": "emulator",
                "evidence_type": "emulator",
                "repetition": repetition,
                "execute_job_name": job_name,
                "shots_requested": 7000,
                "shots_retrieved": sum(row["shots_retrieved"] for row in run_rows),
                "results": run_rows,
                "claim_boundary": validation.CLAIM_BOUNDARY,
            },
            output / f"quantinuum_full_suite_{args.target}_{args.stamp}_r{repetition}",
        )
        job_names.append(job_name)
        print(f"Retrieved {job_name}: 7,000 shots", flush=True)
    write_csv(output / f"quantinuum_full_suite_{args.target}_{args.stamp}_raw.csv", all_rows)
    aggregates = validation.aggregate_rows(all_rows)
    write_csv(output / f"quantinuum_full_suite_{args.target}_{args.stamp}_aggregate.csv", aggregates)
    submission = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": args.target,
        "target_classification": "emulator",
        "evidence_type": "emulator",
        "compile_job_name": (
            "compile-H2-1LE-matched-20260723T162500Z"
            if args.target == "H2-1LE"
            else "compile-H2-Emulator-matched-20260723T162900Z"
        ),
        "execute_job_names": job_names,
        "circuit_count": 7,
        "repetitions": args.repetitions,
        "shots_per_circuit": args.shots,
        "shots_requested": 7 * args.shots * args.repetitions,
        "shots_retrieved": sum(row["shots_retrieved"] for row in all_rows),
        "reported_cost": None,
        "quota_message": "Nexus simulation CPU quota: No quota set for user.",
        "claim_boundary": validation.CLAIM_BOUNDARY,
    }
    validation._write_json_new(
        output / f"quantinuum_full_suite_manifest_{args.target}_{args.stamp}.json", submission
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
