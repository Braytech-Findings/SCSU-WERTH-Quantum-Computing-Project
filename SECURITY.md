# Security Policy

Do not report provider tokens, IBM instances, Nexus internal identifiers, account screenshots, or private institutional information in a public issue. Revoke exposed credentials immediately and use GitHub's private security-reporting channel for repository vulnerabilities.

The project reads optional local provider settings only for explicitly invoked submission tools. `.env*` files are ignored except for the empty `.env.example`. Tests, validation, proxy experiments, and reporting are designed to work without credentials or remote submission.
