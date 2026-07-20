# Contributing

Thank you for helping improve this research repository. Contributions are welcome when they strengthen scientific clarity, reproducibility, testing, documentation, accessibility, or careful interpretation.

## Before you begin

Please read:

- [README.md](README.md) for project scope;
- [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md) for the controlled method;
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) for claims that the project does not make; and
- [docs/OWNERSHIP_AND_CITATION.md](docs/OWNERSHIP_AND_CITATION.md) for reuse and attribution guidance.

## Ground rules

1. Keep proxy, physical-hardware, emulator, and syntax-checker evidence clearly separated.
2. Do not describe emulator output as physical-QPU output.
3. Do not describe proxy timing or success estimates as measured device performance.
4. Never commit API keys, access tokens, account identifiers, private job metadata, or confidential material.
5. Preserve reproducibility by documenting configuration, package versions, random seeds, and data provenance.
6. Prefer plain language alongside specialized terminology.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

## Quality checks

Run these commands before opening a pull request:

```bash
python -m quantum_compare.cli check
ruff check .
pytest -q
mypy src tests
```

When a change affects generated figures or tables, also regenerate the relevant artifacts and explain why the output changed.

## Types of contributions

### Documentation

Good documentation contributions include:

- clearer beginner explanations;
- corrected links or commands;
- better figure captions and alt text;
- more explicit evidence labels; and
- reproducibility notes.

### Code

Code changes should:

- remain compatible with Python 3.11 or newer;
- include tests for new behavior;
- avoid provider submission by default;
- keep hardware spending explicit and opt-in; and
- preserve existing output schemas unless the change is documented.

### Data and provider evidence

New evidence must include:

- provider and target name;
- whether the target is physical hardware, emulator, simulator, or syntax checker;
- circuit family and size;
- shot count where applicable;
- retrieval or execution date;
- sanitized raw output or a documented reason it cannot be shared; and
- a plain-language statement of what the evidence can and cannot prove.

## Pull-request process

1. Create a focused branch.
2. Make one logically related set of changes.
3. Run the quality checks.
4. Update documentation and tests with the code.
5. Complete the pull-request template.
6. Clearly call out any generated artifacts, assumption changes, or scientific interpretation changes.

A pull request may be held back when it mixes evidence types, overstates conclusions, removes limitations, exposes credentials, or cannot be reproduced.

## Commit guidance

Use short, descriptive commit messages, such as:

```text
Clarify emulator evidence labels
Add GHZ routing regression test
Improve beginner figure explanations
```

## Reporting problems

Use a GitHub issue for reproducible bugs, documentation problems, or research questions. For security or credential exposure, follow [SECURITY.md](SECURITY.md) instead of posting sensitive details publicly.
