# Qt UI Evidence

**Experimental release candidate: 0.1.0-rc.1. Not published.** A Codex skill for investigating a Qt/PySide6 interface complaint with fresh pictures, actual widget measurements and normal control input. It connects an expected visible result to before/after evidence and keeps measured facts separate from visual judgments and unknowns.

This is a skill with an optional in-process snapshot helper, not a replacement test framework or a Python package. Use existing QtTest or pytest-qt tools. See [why this exists](docs/alternatives.md) and [supported environments](docs/support.md) before relying on it.

## Try from a checkout

Prerequisite: Codex with local skills support. From this repository root, install into the current project's discovery folder without overwriting an existing skill:

```sh
mkdir -p .agents/skills
python3 - <<'PY'
import shutil
shutil.copytree('skills/qt-ui-evidence', '.agents/skills/qt-ui-evidence')
PY
```

The copy fails if the destination exists; inspect an existing installation before changing it. For personal use, copy the same source folder into `~/.agents/skills/qt-ui-evidence` instead. Start Codex in the project and invoke:

> Use $qt-ui-evidence to investigate why changing the visible row setting does not increase the rows displayed. Use synthetic data, compare the starting and changed states, and report measurements, visual judgments and unknowns.

[Official skill documentation](https://learn.chatgpt.com/docs/build-skills) describes local discovery and invocation. This local installation does not install Python, Qt, or a screenshot viewer. Publication to GitHub, plugin distribution and directory listings are separate steps; none have happened. There is no `pip install qt-ui-evidence` command.

## Run the synthetic demonstration

Use an environment that already has PySide6, or explicitly choose to install the tested dependency in a new virtual environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install PySide6==6.10.3
QT_QPA_PLATFORM=offscreen .venv/bin/python -m unittest discover -s tests -t . -v
```

These commands are for macOS/Linux shells; Windows execution has not been verified. `offscreen` must be chosen before creating QApplication; do not silently switch a running application. The tests create synthetic windows, exercise keys/clicks and close them. By default temporary captures are removed after each test. To retain evidence, set `QT_EVIDENCE_OUTPUT` to your own output folder before running; each capture creates a unique subfolder. Read the images yourself; passing assertions do not establish visual or native-display correctness. Interrupt with Ctrl-C; only the foreground test process is owned by this run.

The row fixture compares a missing setting connection with a working one. The station fixture compares deliberately misplaced controls and a nonworking collapse action with a layout that responds to input and resizing. Valid small datasets, hidden rows and an intentional child badge guard against blanket defect reports. [Development and review](CONTRIBUTING.md) explains checks and reporting.

## Release boundary

The candidate is ready for local review, with limited platform evidence documented in [support](docs/support.md). Before public publication: choose the destination and distribution route, approve the reviewed files and identity, then publish and verify hosted checks/protections. No user data, application code or private project assumptions belong in a contribution. The MIT licence covers original files here; Qt/PySide6 and other tools retain their own licences.

## Review recommendation and example evidence

The independent baseline and skill-guided trial reached the same useful findings. **Prefer improving qt-testing before launching a separate competing skill.** This candidate makes that proposed improvement concrete; it does not establish better detection or justify PyPI packaging. See the [comparison and decision](docs/alternatives.md#independent-comparison).

Both row screenshots have the setting at 6: [before](docs/images/rows-before.png) still shows 3 rows; [after](docs/images/rows-after.png) shows 6. The station images show [clipped/overlapping controls](docs/images/layout-before.png) and [the working layout](docs/images/layout-after.png), including the intentional small child badge. These are synthetic offscreen examples, not native-display acceptance.
