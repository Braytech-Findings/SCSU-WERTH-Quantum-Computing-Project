# IBM Hardware Validation Note

This page records IBM Quantum hardware jobs provided by the project author. These are
real machine results. They are kept separate from the offline proxy-model result tables
so readers can tell which numbers came from architecture estimates and which numbers
came from IBM hardware.

## Current Status

- Provider: IBM Quantum
- Retrieved backend identifier: `ibm_kingston`
- IBM Runtime job ID: `d8up2d1ropqc738b44pg`
- Job status at retrieval: `DONE`
- Result type: `PrimitiveResult`
- Pub results retrieved: `90`
- Classical register name: `meas`
- Shot count: `4096` shots per pub result
- Counts artifact: `results/hardware/ibm_job_d8up2d1ropqc738b44pg.json`
- Summary artifact: `results/hardware/ibm_job_d8up2d1ropqc738b44pg_summary.csv`
- Backend metadata beyond backend name: `null`
- Run date: pending extraction

The measured counts are now stored in a separate hardware artifact. This hardware job
should still not be mixed into the proxy-model tables because the proxy study and the
IBM hardware job answer different questions.

## Compact Result Summary

The summary CSV groups each pub result by measured bit-width. Each pub result has 4096
shots. The `all_zero_or_all_one_probability` column is useful for Bell/GHZ-style circuits
where the ideal result should mostly be all zeros or all ones.

| Bit width | Pub results | Min all-zero/all-one probability | Mean | Max |
| --- | ---: | ---: | ---: | ---: |
| 2 | 15 | 0.959717 | 0.967774 | 0.975586 |
| 4 | 15 | 0.858398 | 0.919238 | 0.955811 |
| 6 | 15 | 0.735840 | 0.849219 | 0.912109 |
| 8 | 15 | 0.155762 | 0.588997 | 0.843750 |
| 12 | 15 | 0.115723 | 0.525602 | 0.793701 |
| 16 | 15 | 0.058594 | 0.444173 | 0.710205 |

The artifact does not identify the original circuit name for each pub index, so the
repository records the measured bit-width and counts without guessing circuit-family
labels.

## Why This Is Separate

The main project results compare offline architecture proxy models. A real IBM hardware
job is a different kind of evidence. It can be useful as a validation note, but it must
stay separate unless the exact backend, date, shots, counts, and result format are saved.

## Safe Retrieval Pattern

Do not commit IBM Quantum tokens, CRNs, service instances, or account identifiers. Put
private account values in environment variables or local-only files.

The easiest local workflow in this repository is:

1. Open `.env.ibm`.
2. Fill in `IBM_QUANTUM_TOKEN` and `IBM_QUANTUM_INSTANCE`.
3. Run:

```bash
python scripts/fetch_ibm_hardware_job.py
```

The `.env.ibm` file is ignored by Git. The script writes sanitized public artifacts to
`results/hardware/ibm_job_d8up2d1ropqc738b44pg.json` and
`results/hardware/ibm_job_d8up2d1ropqc738b44pg_summary.csv` if the job can be retrieved.

```python
import os

from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService(
    channel="ibm_quantum_platform",
    instance=os.environ["IBM_QUANTUM_INSTANCE"],
)

job = service.job("d8up2d1ropqc738b44pg")
job_result = job.result()

print("job_id:", job.job_id())
print("status:", job.status())
print("backend:", job.backend().name if hasattr(job.backend(), "name") else job.backend())

# For a Sampler-style primitive result, inspect each pub result.
# Replace <idx> and <classical_register_name> with the actual result index and register.
# pub_result = job_result[<idx>]
# counts = pub_result.data.<classical_register_name>.get_counts()
# print(counts)
```

## What To Save Before Drawing Conclusions

Save these fields before describing the hardware result:

- exact backend identifier
- job ID
- run date and time
- shot count
- circuit family and qubit count
- classical register name
- measured counts
- any provider-reported mitigation or calibration metadata

If any value is unavailable, record it as `null`, not zero.

## Extended Hardware Validation Suite

For a larger IBM hardware validation, use the extended validation helper. It creates a
substantial circuit bundle and writes a plan first.

Dry-run plan only:

```bash
python scripts/submit_ibm_extended_validation.py --backend ibm_kingston --shots 4096 --repetitions 5 --max-qubits 16
```

This writes:

`results/hardware/ibm_extended_validation_plan.json`

No job is submitted in dry-run mode.

To submit the planned workload to IBM hardware after reviewing the plan and confirming
quota/credit use:

```bash
python scripts/submit_ibm_extended_validation.py --backend ibm_kingston --shots 4096 --repetitions 5 --max-qubits 16 --submit-hardware --i-understand-this-may-use-credits
```

The submission command saves the IBM job ID under `results/hardware/` and keeps it
separate from the offline proxy-model tables. Do not use this command casually: it can
consume IBM Quantum quota or credits.

## Extended Hardware Submission Record

An extended IBM hardware validation job was submitted after the dry-run plan was reviewed.

- Backend: `ibm_kingston`
- IBM Runtime job ID: `d95vhvd2su3c739gc080`
- Submitted at: `2026-07-06T18:50:37.389941+00:00`
- Circuit count: `115`
- Shots per circuit: `4096`
- Total requested shots: `471040`
- Submission record:
  `results/hardware/ibm_extended_validation_submission_d95vhvd2su3c739gc080.json`

IBM reported that `ibm_kingston` was in maintenance at submission time, so this job may
wait in the queue or complete later than usual.

After the job finishes, fetch the sanitized result artifacts with:

```bash
python scripts/fetch_ibm_hardware_job.py --job-id d95vhvd2su3c739gc080
```

## Extended Hardware Result

The extended IBM hardware validation job finished and was retrieved successfully.

- Backend: `ibm_kingston`
- IBM Runtime job ID: `d95vhvd2su3c739gc080`
- Job status at retrieval: `DONE`
- Retrieved at: `2026-07-07T17:05:08.704922+00:00`
- Result type: `PrimitiveResult`
- Pub results retrieved: `115`
- Classical register name: `c`
- Shot count: `4096` shots per pub result
- Total retrieved shots: `471040`
- Counts artifact: `results/hardware/ibm_job_d95vhvd2su3c739gc080.json`
- Summary artifact: `results/hardware/ibm_job_d95vhvd2su3c739gc080_summary.csv`
- Backend metadata beyond backend name: `null`
- Run date: `null`

These results are real IBM hardware counts, but they are still separate from the offline
proxy-model tables. The proxy tables compare architecture assumptions in a controlled
offline model. The IBM job shows what one real backend returned for this submitted
validation bundle.

### Extended Compact Result Summary

Each row in the summary CSV is one pub result. The
`all_zero_or_all_one_probability` column is easiest to read for Bell/GHZ-style circuits:
larger values mean the result landed more often in the two simplest ideal states, all
zeros or all ones. Other circuit families can naturally spread counts over many bit
strings, so this column should not be treated as a universal score for every row.

| Bit width | Pub results | Min all-zero/all-one probability | Mean | Max |
| --- | ---: | ---: | ---: | ---: |
| 2 | 10 | 0.491455 | 0.735156 | 0.971680 |
| 4 | 15 | 0.123047 | 0.403613 | 0.959229 |
| 6 | 15 | 0.027588 | 0.316471 | 0.916260 |
| 8 | 15 | 0.007080 | 0.292334 | 0.861572 |
| 10 | 15 | 0.000977 | 0.259066 | 0.791504 |
| 12 | 15 | 0.000244 | 0.239827 | 0.728516 |
| 14 | 15 | 0.000000 | 0.220459 | 0.677002 |
| 16 | 15 | 0.000000 | 0.203939 | 0.624023 |
