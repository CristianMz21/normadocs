# Security

**Do not** open a public GitHub issue to report a security vulnerability.
Anyone could read it before a fix is shipped.

## How to report

Use **GitHub private vulnerability reporting** on this repository:

1. Go to the [Security tab](https://github.com/CristianMz21/normadocs/security)
   of the repository.
2. Click **"Report a vulnerability"**.
3. Fill in the form with the details below.

If the GitHub private channel is unavailable in your environment, open a
minimal, non-sensitive issue asking the maintainer for a private contact
channel. Do not include vulnerability details in the public issue.

## What to include

- A description of the vulnerability and its impact.
- Reproduction steps (Markdown sample, CLI command, or code snippet).
- The NormaDocs version, Python version, OS, and Pandoc version.
- Whether you would like to be credited when the fix is released.

## Response timeline

- We aim to **acknowledge** new reports within **72 hours**.
- Triage and severity assessment: typically within **7 days**.
- Fix timeline depends on severity and complexity; the maintainer will keep
  the reporter updated.

The full policy — supported versions, response SLAs, and best practices —
lives in
[`.github/SECURITY.md`](https://github.com/CristianMz21/normadocs/blob/main/.github/SECURITY.md).

## Security best practices when using NormaDocs

- Install **Pandoc** from [official sources](https://pandoc.org) only.
- Use `--bibliography` and `--csl` only with files you trust; both are
  passed to Pandoc and executed in a subprocess.
- Process untrusted Markdown in an isolated environment (container or
  VM). NormaDocs runs Pandoc as a subprocess on the contents of the input
  file, so a hostile Markdown file with malicious citations could
  theoretically affect the host.
- Keep Python and Pandoc up to date; security issues in either can
  affect NormaDocs output integrity.
