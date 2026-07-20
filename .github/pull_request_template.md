## Summary

Describe what changed and why.

## Change type

- [ ] Code
- [ ] Tests
- [ ] Documentation
- [ ] Data or generated artifacts
- [ ] Provider validation
- [ ] Research interpretation

## Evidence classification

Check every evidence type affected by this pull request.

- [ ] Offline proxy model
- [ ] Physical hardware
- [ ] Emulator or simulator
- [ ] Syntax checker
- [ ] Reproducibility or environment validation
- [ ] No evidence outputs changed

## Validation

- [ ] `python -m quantum_compare.cli check`
- [ ] `ruff check .`
- [ ] `pytest -q`
- [ ] `mypy src tests`
- [ ] Generated artifacts were regenerated when required
- [ ] Documentation was updated when behavior or interpretation changed

## Research-integrity checklist

- [ ] Proxy estimates are not described as measured hardware performance.
- [ ] Emulator or simulator output is not described as physical-QPU output.
- [ ] Physical hardware artifacts remain separate from proxy tables.
- [ ] Limitations and assumptions remain visible.
- [ ] No secrets, private account identifiers, or confidential material are included.

## Output changes

List any changed tables, figures, reports, schemas, or baseline comparisons. Write `None` when there are no output changes.

## Screenshots or figures

Add before-and-after visuals when the pull request changes presentation or generated figures.
