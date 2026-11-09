# Contributing

Use original synthetic examples and preserve existing files and settings. Keep the skill Qt Widgets/PySide6-specific. Prefer existing Qt/pytest-qt tools before adding helpers. Each demonstrated defect needs a behavioural regression and a valid nearby case where possible. Separate measurements, image-based judgment and missing evidence.

Run `python -m unittest discover -s tests -t . -v` with an explicitly selected Qt platform. Review captured images after relevant layout changes. The tested environment and limits belong in [support](docs/support.md); do not expand compatibility claims merely because a workflow is configured. If Codex skill-creator is available, run its `quick_validate.py` on `skills/qt-ui-evidence`; otherwise inspect frontmatter, referenced resources and installation manually.

Report ordinary problems through the eventual repository's Issues tab, including synthetic reproduction, environment, expected and observed result. Until publication, include them in the local review. Never upload real application screenshots without reviewing their contents. See [security reporting](SECURITY.md) for sensitive findings.

Before a release, test a clean checkout and the complete installed skill folder outside the source tree, review source and reachable history for private data and inspect the final archive. Publish only with the owner's explicit authorization. Hosted jobs and protections must be checked on the actual destination after publication; a local workflow file is not proof they ran.
