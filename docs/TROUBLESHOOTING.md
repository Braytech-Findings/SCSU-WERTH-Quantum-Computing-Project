# Troubleshooting

| Problem | Meaning | Safe response |
|---|---|---|
| `No module named quantum_compare` | The package is not installed in the active environment | Activate `.venv`, then run `python -m pip install -e .`. |
| Qiskit dependency conflict | Installed versions are outside `pyproject.toml` ranges | Create a clean Python 3.11 virtual environment and reinstall. |
| New proxy values differ | Package/compiler behavior or configuration may have changed | Use `compare_run_artifacts.py`; preserve the old baseline and document versions. |
| qBraid notebook differs from local run | Environment or package versions differ | Save the environment record described in [QBRAID_VALIDATION.md](QBRAID_VALIDATION.md). |
| IBM credentials missing | Hardware submission cannot authenticate | Keep using dry-run/offline workflows or configure `.env.ibm` locally; never commit it. |
| Nexus package/access error | Client dependencies, project membership, or quota may be missing | Stop submission attempts and check current provider access with your administrator. |
| A target is visible but execution fails | Visibility is not entitlement or quota | Confirm project access and obtain a cost estimate where supported. |
| `--dry-run` conflicts with a submit flag | Safety modes were mixed | Choose preview or submission, never both. |

Never paste provider tokens, instances, internal UUIDs, or unredacted account screenshots into a public issue.
