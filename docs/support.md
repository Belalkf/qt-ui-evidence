# Supported scope and release limits

Version: **0.1.0-rc.1**, experimental, prepared for review rather than public publication. The supported workflow is an agent inspecting ordinary Qt Widgets/PySide6 in a trusted application test process. The optional helper captures a selected QWidget and measures selected descendants; the vertical row counter supports standard QTableView/QTableWidget section geometry only.

## Executed environment

| Component | Verified locally |
| --- | --- |
| OS / hardware | macOS 14.8.9, Apple Silicon arm64 |
| Python | CPython 3.9.6, Clang 16 build |
| Binding / Qt | PySide6 6.10.3 / Qt 6.10.3 |
| Rendering | Explicit `QT_QPA_PLATFORM=offscreen`, Fusion style, device pixel ratio 1 |
| Test tools | Python unittest and PySide6.QtTest, with existing installed dependencies |
| Skill host | Codex skill format validated; explicit-path independent agent evaluation |

This is the tested combination, not a promise covering all Python 3.9+, Qt versions, machines or styles. Python 3.9 is end-of-life upstream; it is recorded because it was the available test interpreter, not recommended for new deployments. Newer Python, Windows, Linux, native Cocoa rendering, Retina/other scaling, physical screens and automatic fresh-session skill discovery remain unverified. The prepared macOS GitHub workflow has not run. pytest-qt integration is documented using its public API, but pytest-qt itself was not installed or executed for this candidate.

No runtime was downloaded or product environment modified for local verification. A pre-existing interpreter provided PySide6; tests ran in a separate synthetic repository and a clean external copy, with no product imports. No private application code or assets were used.

## Covered behavior

The regression suite exercises changed preference versus displayed rows, full versus partial/scrolled/hidden/empty rows, a small valid dataset, an explicit scan limit, deliberate overlap and clipping, valid nested decoration, collapse/expand and resize round trips. Capture checks cover repeated outputs without overwrites, preserved visibility/size/display attributes, Unicode labels, hidden/foreign/separate-window rejection, failed output saves and nested capture coordinates. The nested-coordinate defect was reproduced with a failing test before its repair.

Fresh synthetic images were inspected for the row and layout comparisons, collapsed state and narrow/wide states. Visible interpretation remains separate from assertions: an image save is not a visual pass. Runtime logs include expected offscreen `propagateSizeHints` warnings and a missing generic font alias warning; no native-equivalence claim follows from them.

## Not covered

QML/Qt Quick, OpenGL, embedded native widgets, video, tree/list/custom-delegate row counting, precise text-fit analysis, accessibility, native pointer routing, multi-screen placement, async application startup and arbitrary existing application factories are outside the helper's supported scope. QtTest verifies Qt event handling, not physical mouse delivery. Very large tables return unknown above the scan cap. Captures are sequential observations, not an atomic frame/geometry transaction; callers must wait for a stable state.

The helper is not an automatic layout detector and has no attach-to-process command. Rectangular ancestor intersections and visible-region bounds do not prove all pixels are exposed. Full vertical rows can still contain horizontally clipped or obscured cells. Widget images can differ from what a user sees on a physical display. Unsupported content must be reported as unknown or captured using its own suitable tools.

## Distribution acceptance

The self-contained install folder is `skills/qt-ui-evidence`. Repository documentation, tests and synthetic examples are not runtime dependencies. A minimal `.codex-plugin/plugin.json` prepares a plugin envelope following [official packaging guidance](https://developers.openai.com/plugins/build/plugins), without connectors, credentials, hooks or invented publisher details. It has not been uploaded, installed as a plugin, reviewed by a directory or accepted by a marketplace.

Public repository destination, publisher identity and final distribution route need owner review. Hosted checks, branch protection, private vulnerability reporting, dependency/secret scanning and remote-tip verification are pending publication-stage work. No remote exists for this candidate. A local archive and commit establish a review boundary, not a public release or PyPI availability.
