# Security Policy

## Supported version

Security and credential-handling improvements are applied to the current `main` branch.

## Reporting a vulnerability

Do not open a public issue when a report includes:

- an API key, access token, password, or session credential;
- private provider account or organization identifiers;
- a private quantum job payload or confidential attachment;
- a path that could trigger unapproved provider spending; or
- confidential or nondisclosure-protected information.

Instead, contact the repository maintainer using the address listed in [CITATION.cff](CITATION.cff). Include only the minimum information needed to reproduce the problem, and redact active credentials.

## Credential safety

- Store local secrets in environment variables or an ignored `.env` file.
- Use `.env.example` only for placeholder variable names.
- Never commit provider tokens, cloud service keys, job-session cookies, or copied terminal output containing credentials.
- Rotate a credential immediately if it is accidentally exposed.
- Treat public Git history as permanent, even after a file is deleted.

## Provider-spending safety

The default repository workflow is offline and does not submit paid hardware jobs. Any provider submission path should:

1. require explicit user action;
2. display or request a cost estimate when supported;
3. identify the exact target and shot count;
4. avoid automatic retries that may spend additional credits; and
5. keep submitted-job artifacts separate from proxy-model results.

## Research-integrity concerns

Reports about mislabeled evidence are also important. Examples include emulator results presented as physical hardware, proxy estimates presented as measured fidelity, or provider outputs mixed into controlled proxy tables without clear labeling.
