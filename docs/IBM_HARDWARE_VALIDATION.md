# IBM Hardware Validation Note

This page records a separate IBM Quantum hardware job reference provided by the project
author. It is not part of the offline proxy-model result tables.

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
