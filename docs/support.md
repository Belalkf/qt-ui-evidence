# Scope, compatibility and verification

Version **0.1.0** is an early release for ordinary Qt Widgets/PySide6 interfaces across unrelated applications. The skill's method is platform-independent: it uses each project's normal test tools and asks for evidence appropriate to the complaint. The execution record below says where this release was checked; it does not restrict the skill to that machine or require every reader to reproduce its exact versions.

## Intended compatibility

The Python comparison/installation command supports Python 3.9+ on macOS, Linux and Windows and uses only the standard library. The optional capture helper uses public Qt Widgets APIs through PySide6 6.5–6.x; the `qt` extra requests that range. Projects can use their existing compatible PySide6 installation. The skill itself is Markdown and can be used without installing the Python distribution.

The snapshot helper measures standard QTableView/QTableWidget vertical row sections, selected widget geometry and effective visibility. It runs in the application's trusted test process. QtTest or pytest-qt handles interaction and waiting; neither toolkit input events nor a screenshot certify OS-level pointer routing.

## Execution evidence

The initial local Qt run used macOS 14.8.9 arm64, CPython 3.9.6, PySide6/Qt 6.10.3, explicitly selected offscreen rendering, Fusion style and DPR 1. Python-only commands and built package resources were also exercised on CPython 3.11.11 without Qt. The oldest declared Python/build-tool combination was used to build the distribution. Hosted matrix results are visible in [Actions](https://github.com/Belalkf/qt-ui-evidence/actions); a configured job is not a completed check. Hosted runs also exercised the suite on Ubuntu 24.04 x64, macOS 15 Intel and Windows Server 2025 x64, with both Python 3.9/PySide6 6.5.0 and Python 3.13/PySide6 6.10.3. These are representative version pairs, not an exhaustive compatibility matrix. Linux capture needs Qt system libraries such as libEGL; the workflow installs them explicitly.

The suite covers ineffective row preferences, full/partial/scrolled/hidden/empty rows, small valid datasets, scan limits, intentional and accidental intersections, clipping, collapse/expand and resize round trips. Capture checks cover preserved state and outputs, Unicode, rejected hidden/foreign/separate-window input, save failures, nested coordinates and UI-thread ownership. Comparison and installation tests cover invalid records, unknowns, different environments, input preservation, packaged resources and existing-installation refusal.

Twelve initial widget/helper tests passed outside the original project and from the extracted candidate. The public package adds comparison and installation checks. A nested-coordinate defect was reproduced with a failing test before repair; malformed/duplicate row records also have failing-before regressions. Original synthetic before/after images were inspected, including collapsed and narrow/wide states. The [independent comparison](alternatives.md#independent-comparison) records actual agent behavior and does not claim superior detection or measured time savings.

No private application code or assets were used. Native desktop appearance, fonts, Retina/scaling, accessibility, physical displays and automatic discovery in every agent host remain unverified. pytest-qt's public API is documented but was not executed locally. Offscreen logs can include platform/font warnings; success does not prove native equivalence. Python 3.9 is retained for existing environments; prefer a maintained Python version for new setups.

## Measurement limits

QML/Qt Quick, OpenGL, embedded native widgets, video, tree/list/custom-delegate row counting and precise text-fit analysis are outside the helper. Their own capture/measurement tools are required. Arbitrary application factories and attaching to running processes are not provided.

A full vertical row can still contain clipped or obscured cells. Rectangular ancestor intersections ignore masks; visible-region bounds discard holes and Qt visibility is not proof of physical screen exposure. Above 10,000 model rows the row helper returns unknown instead of scanning indefinitely. Images and measurements are sequential observations, so callers must wait for a stable state. The comparison command reports these facts; it never decides whether a particular intersection is a defect.

## Distribution

The Python wheel bundles the complete skill from the same source folder; the helper is not maintained twice. `pip install` installs the tool only; `install-skill` is an explicit separate action. The GitHub install folder remains `skills/qt-ui-evidence`. A minimal plugin envelope is provided, but no plugin-directory acceptance or universal host compatibility is claimed. [Official packaging guidance](https://developers.openai.com/plugins/build/plugins) describes that separate distribution route.
