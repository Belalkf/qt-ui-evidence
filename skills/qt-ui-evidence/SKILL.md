---
name: qt-ui-evidence
description: Investigate Qt Widgets/PySide6 complaints about displayed rows, paragraph placement, clipped or overlapping controls, and collapse or resize behavior using fresh screenshots, widget measurements and normal input. Use for complaint-driven Qt interface verification; not screenshot cloning, web UI, QML or native-display certification.
---

# Qt UI Evidence

Turn a visible complaint into a reproducible check and a measured before/after result. Use the project's existing harness (pytest-qt when present, otherwise QtTest); do not replace it or create a parallel application merely to obtain a passing image.

## Establish the claim

Record the user's expected result, starting state, data, window size and actions. Translate the complaint into an observable condition: for example, changing a row preference from 3 to 6 should increase fully displayed rows when six exist and space permits. Clarify whether it is a target, maximum or minimum before calling a constrained layout defective. A changed setting or model row count alone proves no displayed-row change.

Identify the actual widget factory and safe synthetic data. Keep live content, settings and background work untouched. Record Python, PySide6/Qt, OS, platform plugin, style and device pixel ratio. Choose the project's authorized desktop or offscreen route explicitly. Never silently install dependencies, switch rendering modes or change production settings to make the test pass.

## Gather connected evidence

1. Reproduce on the real affected widget. Wait for a meaningful ready condition with a finite timeout; one `processEvents()` or a fixed sleep is not proof of completion. Capture the starting state with a fresh, identifiable image.
2. Inspect geometry in a shared coordinate space, effective visibility, ancestor clipping, relevant viewport and constraints. For tables distinguish available model rows, hidden rows, full vertical rows and partial rows; scroll position, headers and scrollbars affect the count. Inspect spanning cells or custom delegates separately. See [measurement details](references/measurements.md).
3. Follow the user's action with `qtbot.mouseClick`/`keyClicks` or `QTest` events. Verify the control is enabled, exposed within its ancestors and reachable at the intended hit point; assert the resulting state. Calling `.click()`, setting values or invoking a slot can diagnose logic but does not verify input delivery. QtTest events still do not prove OS-level mouse/focus routing.
4. Capture the resulting state and repeat identical actions after a repair. Keep window size, data, style and rendering route comparable; document intentional differences. Exercise collapse → expand → collapse and narrow → wide → narrow where relevant. Restore temporary state and close only owned windows/jobs.

Use existing screenshot/measurement tools when sufficient. The optional [snapshot helper](scripts/snapshot.py) saves a widget image and selected measurements in a fresh directory without showing, hiding, resizing or modifying the widget. Import it in the UI thread of the existing test process; it cannot attach to another running application. It does not wait for readiness or decide whether a layout is defective. If the optional Python tool is installed, `qt-ui-evidence compare BEFORE AFTER` compares the saved measurements, including row identities and scroll context; it does not inspect the images or issue a visual verdict. See [helper usage](references/measurements.md#optional-helper).

## Decide without inventing defects

Overlap is a candidate, not a verdict: intentional badges, child controls within parents and stacked pages can be correct. Hidden/collapsed controls and scrolling content are not automatically clipped defects. Compare ancestor clipping, hit testing, intended layout rules and the image. A geometric rectangle inside its parent does not prove the label fits; inspect the actual text rendering and use project-specific text metrics if needed.

Include a nearby valid case in a regression so the check cannot pass merely by flagging every intersection. Reproduce the defect before the repair when feasible; add a regression for the demonstrated user-visible behavior. Do not weaken the expectation or alter unrelated sizing to manufacture success.

## Locate paragraphs when text grouping matters

For text that appears split, crowded, clipped or grouped with the wrong column, read [paragraph maps](references/paragraphs.md). Prefer Qt document structure and line geometry over guessing paragraph boundaries from pixels. The optional helper's `text_map=True` adds numbered bounds on a separate image and maps visible paragraphs in standard Qt text editors; `include_text=True` is a separate opt-in for source text. Review the original image as well as the map. Normal wrapping is not a paragraph split, and an unmapped region is not proof of missing text.

When only an image or an unsupported text surface is available, use an existing OCR tool if useful and authorized. Label OCR groups as estimates, keep their coordinate transforms and word confidence distinct from semantic grouping, and retain failures as unknowns. Do not merge columns merely because words are close, infer hidden text from a crop, or add an OCR engine/dependency without need. The current helper does not run OCR automatically.

## Report evidence and limits

Explain what the user now sees, followed by:

- **Measured:** actions, actual setting values, window/viewport dimensions, full/partial row counts, effective visibility and exact image/measurement artifacts before and after.
- **Visual judgment:** what the freshly inspected image appears to show, with the affected region and rationale. Use human-review language for subjective spacing or readability.
- **Unknown:** missing input, unsupported rendering, unexecuted desktop checks or ambiguity in the intended behavior. If only a screenshot exists, request or obtain live measurements where possible and keep those claims unknown meanwhile.

Never infer exact fonts, hidden content, accessibility or native display correctness from screenshots. `QWidget.grab()` renders widget contents; it is not an OS screenshot and may include content obscured by another window. Offscreen success is useful bounded evidence, never native acceptance. If unable to reproduce or inspect an image, say so; do not report a visual pass from a JSON file or successful save.
