# Measurements and interpretation

## Geometry

Use logical Qt coordinates for comparisons. Map each selected widget to the same root with `mapTo`; `geometry()` alone is parent-relative. Intersect with ancestor rectangles and inspect scroll viewports. `visibleRegion()` is an approximation; its bounding rectangle discards holes. Record whether the intended click point lies inside the region and whether `childAt` reaches the target or its child. Neither this nor `isVisible()` proves the window is unobscured on a physical display.

A parent/child rectangle intersection is normal. Compare controls that should be separate, then judge whether their actual painted content or hit areas conflict. Deliberate badges, overlays, tab pages and collapsed panels need their intended state recorded. Rectangular clipping ignores masks and rounded shapes. A visible rectangle is not a text-fit measurement.

## Rows

For a standard `QTableView`/`QTableWidget`, count nonhidden row extents intersecting the viewport after scrolling settles. Separate fully vertically contained rows from partial rows. Record model row count and viewport height so a preference change cannot masquerade as a display change. A model with two rows cannot display six occupied rows; a maximum-row setting may correctly shrink on a small screen.

The helper counts vertical section geometry only. It does not establish horizontal cell visibility, text readability, viewport exposure through ancestors, occlusion, row-span semantics, delegate painting or lazy-loaded content. `QTreeView`, `QListView`, QML and custom painted lists need project-specific measurements; do not reuse the table counter as if it covered them. Above 10,000 model rows the helper returns an explicit unknown rather than scan unbounded data.

## Optional helper

Requirements: an existing `QApplication`, the UI thread, a shown ordinary QWidget root, selected descendants and an explicit output directory. Import by absolute helper location from the installed skill, using `importlib.util.spec_from_file_location` if needed. No runtime is installed by importing the skill. Example inside an existing test:

```python
# snapshot is the imported scripts/snapshot.py module.
# qtbot and the real widget come from the project's existing tests.
qtbot.waitUntil(lambda: widget.table.model().rowCount() == 12, timeout=1000)
before = snapshot.capture(widget, {"table": widget.table}, evidence_dir)
widget.row_setting.selectAll()
qtbot.keyClicks(widget.row_setting, "6")
qtbot.waitUntil(lambda: widget.row_setting.value() == 6, timeout=1000)
qtbot.waitUntil(
    lambda: len(snapshot.table_rows(widget.table)["full_vertical_rows"]) == 6,
    timeout=1000,
)
after = snapshot.capture(widget, {"table": widget.table}, evidence_dir)
```

The caller must also wait for the expected rendered geometry, not just the setting value. Prefer `qtbot.screenshot` plus local assertions if they already provide sufficient evidence. The helper adds a matching JSON record with environment, root size, selected geometry, visibility, hit-point facts and table row indices; it exports no widget text or object names in the default capture. The optional [paragraph map](paragraphs.md) has a separate, explicit source-text option. The image still contains all rendered content, including potentially private data: use synthetic inputs or keep evidence private.

Each call creates a unique `capture-*` folder containing `widget.png` and `measurements.json`; no filename derives from labels. Repeated calls preserve earlier files. An I/O failure raises and may leave partial evidence, which is not a completed capture. Caller-owned cleanup should remove only known temporary artifacts when no longer needed. Do not delete the user's evidence automatically.

The helper neither shows hidden roots nor changes `WA_DontShowOnScreen`, focus, size, values or collapse state. It rejects foreign widgets and separate child windows; capture dialogs separately. It does not create a QApplication, run an event loop, enforce a process timeout, attach to another process or generate a pass/fail verdict. Run tests under an owned finite deadline and cancel only their process if they hang.

## Capture limits

Use this helper only for ordinary raster Qt Widgets. OpenGL, Qt Quick, embedded native windows, video and compositor effects are unsupported. Their dedicated framebuffer/native capture tools and display checks are separate work. A widget grab may repaint content and can omit the window frame, cursor, menus or another top-level popup. Capture popups explicitly with the right tool. Keep image pixel dimensions separate from Qt logical dimensions when device pixel ratio differs from one.

Configured font properties may be queried from the widget when relevant, but screenshot appearance does not identify an exact font or prove fallback glyph selection. Confirm font resolution separately if the complaint concerns it. Do not certify native sizing, focus, accessibility or display scaling from an offscreen capture.
