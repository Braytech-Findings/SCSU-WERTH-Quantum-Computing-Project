# IBM Hardware Validation Note

This page records a separate IBM Quantum hardware job reference provided by the project
author. It is not part of the offline proxy-model result tables.

## Current Status

- Provider: IBM Quantum
- Author-reported target name: IBM Kingston
- IBM Runtime job ID: `d8up2d1ropqc738b44pg`
- Counts: pending extraction
- Backend metadata: pending extraction
- Shot count: pending extraction
- Run date: pending extraction

Because the measured counts and backend metadata are not stored in this repository yet,
this job should not be used as a benchmark result or mixed into the proxy-model tables.

## Why This Is Separate

The main project results compare offline architecture proxy models. A real IBM hardware
job is a different kind of evidence. It can be useful as a validation note, but it must
stay separate unless the exact backend, date, shots, counts, and result format are saved.

## Safe Retrieval Pattern

Do not commit IBM Quantum tokens, CRNs, service instances, or account identifiers. Put
private account values in environment variables or local-only files.

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
