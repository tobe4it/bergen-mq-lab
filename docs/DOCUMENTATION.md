# Documentation maintenance policy

## Source of truth

The English technical files in `README.md` and `docs/` are the versioned
implementation references. The translated, reader-oriented manuals live in
`wiki/en/Guide.md`, `wiki/de/Guide.md` and `wiki/fr/Guide.md`.
The three guides cover twelve matching subjects, with consistent security
limitations. They intentionally refer to the canonical technical sources
rather than reproduce every Ansible parameter or unsupported claim.

The directory `wiki/` is **a Git-versioned Wiki source**, not evidence that
the separate GitHub Wiki Git repository has been published. GitHub Wiki uses
a separate Git remote. The connected GitHub file API does not publish those
pages by itself.

## Publication

Once the repository's Wiki feature is enabled and write access is available,
publish the reviewed version from a trusted maintainer workstation. Avoid
committing generated files or credentials to the Wiki. GitHub Wiki's own
page paths and link resolution may differ from repository Markdown.
Verify every published language navigation link.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
git clone https://github.com/tobe4it/bergen-mq-lab.wiki.git
cd bergen-mq-lab.wiki
cp -R ../bergen-mq-lab/wiki/. .
git status --short
git add Home.md _Sidebar.md en/Guide.md de/Guide.md fr/Guide.md
git commit -m "docs: publish multilingual MQ Lab manuals"
git push origin HEAD
```

Use the Wiki web interface to confirm all pages and sidebar links. If Wiki
cloning is unavailable, enable Wikis in repository settings and initialize
the first page through GitHub, then repeat. A GitHub Wiki repository is **not**
maintained automatically by pushing changes to `main`; repeat publication or
set up a separately authorized publishing workflow when these files change.

## Editorial and review rules

- Update the English reference and all three guides when documented behavior
  changes. Preserve identical subject coverage and explicit limitations.
- Never claim passing live IBM MQ integration tests based only on offline CI.
- Require peer review for procedures that alter objects or access controls.
- Use consistent literal command names/variable names across translations.
- Include prerequisites, rollback limitations, risk, expected evidence and
  troubleshooting for operational changes.
- Keep site hostnames, Vault secrets and private keys out of both docs and Wiki.
- Review links and use a meaningful change summary.
- Run `python3 tools/check_documentation.py` before committing.
- CI checks section parity and local link targets; it does **not** verify
  translation semantics or the health of external web links.

## EU Quick Starts

Twenty-four Quick Start translations are maintained as `wiki/Quick-Start-XX.md`:
BG, CS, DA, DE, EL, EN, ES, ET, FI, FR, GA, HR, HU, IT, LT, LV, MT, NL, PL,
PT, RO, SK, SL, SV. Each has six matched sections and the same executable
examples. CI checks language coverage and command parity, not translation
quality. Have native speakers review the technical translations before formal
publication. See [Wiki publication](WIKI-PUBLISH.md).
