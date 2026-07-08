# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

Only the latest minor line receives security fixes. Earlier versions are
end-of-life and will not receive backports.

## Reporting a Vulnerability

If you discover a security vulnerability within NormaDocs, please report it
responsibly. **Do NOT** create a public GitHub issue for security
vulnerabilities — anyone could read it before a fix is shipped.

Use the **GitHub private vulnerability reporting** feature on this repository
("Security" tab → "Report a vulnerability"). If that channel is unavailable in
your environment, open a minimal, non-sensitive issue asking the maintainer
for a private contact channel.

When reporting, please include:

- A description of the vulnerability and its impact.
- Reproduction steps (Markdown sample, CLI command, or code snippet).
- The NormaDocs version, Python version, OS, and Pandoc version.
- Whether you would like to be credited when the fix is released.

## Response timeline

- We aim to **acknowledge** new reports within **72 hours**.
- Triage and severity assessment: typically within **7 days**.
- Fix timeline depends on severity and complexity; the maintainer will keep
  the reporter updated.

## Security Best Practices When Using NormaDocs

- Install **Pandoc** from official sources only (https://pandoc.org).
- Use `--bibliography` and `--csl` only with trusted files; both are passed
  to Pandoc and executed in a subprocess.
- Process untrusted Markdown in an isolated environment (container or VM).
- Keep Python and Pandoc up to date; security issues in either can affect
  NormaDocs output integrity.

Thank you for helping keep NormaDocs and its users safe.