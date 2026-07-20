# Codex Upgrade Report

Verified on 2026-07-20 without provider credentials or remote submissions.

## Files created

- Installation, running, troubleshooting, societal-impact, glossary, beginner-walkthrough, and figure-guide documents under `docs/`
- Professional architecture banner under `docs/assets/`
- Credit-safe repository validator and Makefile
- GitHub Actions workflow, contribution/security/conduct files, and pull-request template

## Files modified

- `README.md`: banner, functional badges, navigation, child-friendly explanation, and societal-impact summary
- IBM and Quantinuum submission scripts: common `--dry-run` and `--confirm-submit` aliases, conflict checks, and clearer backend/project/cost-preview output

## Figures

The new SVG header is conceptual and contains no scientific values. Existing publication figures and manifests were retained because they already derive from committed proxy/provider data. `docs/FIGURE_GUIDE.md` routes readers to the detailed interpretation guide and regeneration commands.

## Verification

- `python -m pytest -q`: 30 passed, including new common safety-flag tests
- `python scripts/validate_repository.py`: passed
- `mypy src tests`: passed
- `ruff check --no-cache .`: passed
- No IBM, Quantinuum, qBraid, simulator-quota, or physical-QPU job was submitted

## Problems found and fixed

- Missing consolidated cross-platform setup, command matrix, glossary, societal-impact, troubleshooting, and beginner documents
- Provider-specific safety flag vocabulary was hard to compare; compatible shared aliases were added without removing the second credit-awareness guard
- No public validator, Makefile, or CI workflow existed
- README lacked a professional header and compact navigation

## Remaining limitations

- qBraid validation remains notebook-based rather than a verified CLI route.
- Cost estimates depend on provider support and account access; none are fabricated offline.
- The IBM physical-hardware evidence and Quantinuum emulator evidence are not a matched physical-QPU comparison.
- Proxy assumptions are not live calibrations, and physical hardware is variable.

## Recommended next steps

Run the new CI on GitHub, independently inspect generated figures in light/dark mode, and conduct any new provider work only from reviewed dry-run plans with explicit authorization and recorded cost estimates.
