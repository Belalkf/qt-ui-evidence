# Qt UI Evidence

Investigate a Qt/PySide6 interface complaint with fresh screenshots, actual widget measurements and normal control input. Compare the expected visible result before and after a repair, while keeping measurements, visual judgments and unknowns separate.

The skill applies across unrelated Qt Widgets projects. It is not tied to a particular operating system, application, font or test framework. The Python tool compares captured measurements and optionally installs the skill into Codex; it does not automatically decide whether a layout is correct. Version **0.1.0** is an early release. See [scope and verification](docs/support.md) and the [comparison with existing tools](docs/alternatives.md).

## Install

```sh
python -m pip install qt-ui-evidence
```

The base tool needs Python 3.9 or later, with no third-party runtime dependencies. It can compare evidence without Qt. If you also need the optional capture helper and do not already have PySide6 in your application's environment:

```sh
python -m pip install 'qt-ui-evidence[qt]'
```

For a source checkout before a registry release is available, use `python -m pip install .` from its root, or `python -m pip install git+https://github.com/Belalkf/qt-ui-evidence.git`. Choose the environment used by your application; do not replace its existing Qt dependency merely to use the skill.

## Install the Codex skill

Run one explicit command after installing the package:

```sh
qt-ui-evidence install-skill --user
```

This creates `~/.agents/skills/qt-ui-evidence`. For one project instead, use `qt-ui-evidence install-skill --project /path/to/project`. Both refuse existing files, directories or links; inspect an existing installation before changing it. A write failure may leave a partial installation for inspection. Installing the Python package alone never changes agent settings or skill directories.

Invoke it in Codex:

> Use $qt-ui-evidence to investigate why increasing the visible-row setting does not increase the rows displayed. Use synthetic data, compare the starting and changed states, and report measurements, visual judgments and unknowns.

You can also install just `skills/qt-ui-evidence` using Codex's skill installer or copy that complete folder into a [supported skill discovery directory](https://learn.chatgpt.com/docs/build-skills). The skill works with existing QtTest or pytest-qt tools; the Python package is optional. Skill discovery does not install Qt or prove that a native display check ran.

## Capture in an existing application test

Use the real affected widget in a trusted test process after its layout is ready:

```python
from qt_ui_evidence import capture

before = capture(window, {"table": window.table}, evidence_directory)
# Perform the user's action with QtTest/pytest-qt and wait for the layout.
after = capture(window, {"table": window.table}, evidence_directory)
```

Capture requires an existing QApplication and its UI thread. It never shows hidden windows or changes their values, size or display mode. Each call creates a new folder containing `widget.png` and `measurements.json`; earlier evidence is preserved. The image can still contain private content: use synthetic data or keep it private. See [measurement and capture limits](skills/qt-ui-evidence/references/measurements.md).

Compare the two saved folders:

```sh
qt-ui-evidence compare before/capture-folder after/capture-folder
```

The command prints JSON containing changes in full/partial vertical row counts, selected geometry, visibility and environment. Exit 0 means comparison completed, not that the interface passed. Missing measurements stay unknown; changed environments are reported. It never edits inputs or infers fonts, hidden contents, accessibility or native correctness. Inspect the matching screenshots separately.

## Run the original synthetic examples

From a checkout with the package and PySide6 installed:

```sh
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -t . -v
```

Select `offscreen` explicitly before QApplication is created. On PowerShell, set `$env:QT_QPA_PLATFORM='offscreen'` before running Python. The tests cover a row preference that changes without revealing more rows, misplaced controls and nonworking collapse behavior, alongside corrected variants and valid layouts. They close owned windows and normally clean temporary captures. Set `QT_EVIDENCE_OUTPUT` to your chosen folder to retain unique evidence folders. Interrupt with Ctrl-C; only the foreground test process is owned by the run.

Both row screenshots have the setting at 6: [before](docs/images/rows-before.png) shows 3 rows; [after](docs/images/rows-after.png) shows 6. The station examples show [clipped/overlapping controls](docs/images/layout-before.png) and [the working layout](docs/images/layout-after.png), including an intentional child badge. These are synthetic offscreen examples, not native-display acceptance.

## Contribution and limits

Existing Qt tools already perform input, waits and capture. This project adds a complaint-driven procedure and repeatable evidence records; its independent baseline trial did not demonstrate better detection than a capable agent using those tools. Improvements can also be contributed to qt-testing. See [the evidence and decision](docs/alternatives.md#independent-comparison).

QML, OpenGL, video and native embedded surfaces are outside this capture helper. Screenshot-only font identification and native display certification are not supported. [Support](docs/support.md) distinguishes intended compatibility from environments actually tested. [Contributing](CONTRIBUTING.md) and [security reporting](SECURITY.md) describe maintenance and safe examples. Original files are MIT licensed; Qt and other dependencies retain their own licences.
