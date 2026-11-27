# Security Policy

## Scope & Threat Model

`youtube-creator-skill` is an offline-first, text-and-stdlib-Python AI agent skill.
It does **not** require API keys, does **not** log into YouTube accounts, does
**not** auto-publish videos or comments, does **not** send telemetry, and its
bundled Python scripts make **zero network calls** and invoke **zero shell
subprocesses**.

Key security invariants enforced by design and automated tests:

1. **Untrusted Data Isolation (Prompt Injection Defense):**
   Fetched web pages, YouTube comments, video transcripts, CSV cells, and
   third-party READMEs are treated strictly as untrusted data — never as
   executable instructions.
2. **CSV Formula Injection Protection:**
   Human-opened CSV exports sanitize text cells starting with `=`, `+`, `-`,
   `@`, tab, or carriage return (prefixing a leading apostrophe `'`) while
   preserving legitimate numeric fields.
3. **No Secret Exfiltration or Auto-Execution:**
   The skill refuses requests to reveal environment variables, tokens, cookies,
   SSH keys, or unrelated workspace files, and refuses to execute automated
   channel writes or scraping bypasses.
4. **Safe Packaging & Path Traversal Guardrails:**
   Release archives are built strictly from an explicit allowlist, normalized
   with POSIX relative paths, checked against `..`/absolute paths/symlinks, and
   verified against byte-for-byte reproducibility.
5. **Bounded Script Inputs:**
   Optional Python scripts enforce a default 10 MB input size ceiling, reject
   non-finite numbers (`NaN`/`Infinity`), validate schemas strictly, and return
   structured exit codes (`0` = valid computation, `2` = invalid input).

## Reporting a Vulnerability

Please report suspected security issues privately rather than opening a public
issue with exploit details:

- Use **GitHub Private Vulnerability Reporting** on the repository's **Security**
  tab (`https://github.com/quocan050302/youtube-creator-skill/security/advisories`)
  if enabled on GitHub.
- If private advisory reporting is not yet enabled, open a minimal issue titled
  `[SECURITY] Request private contact channel` without including sensitive
  details, credentials, or private creator data.

Do **not** submit real OAuth tokens, browser cookies, API keys, or private
YouTube Studio exports containing personal revenue/PII in issues or pull
requests.
