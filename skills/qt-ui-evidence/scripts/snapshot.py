"""Optional, in-process PySide6 QWidget evidence; no automatic defect verdicts."""

import json
import platform
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import PySide6
from PySide6.QtCore import QPoint, QRect, QThread, qVersion
from PySide6.QtWidgets import QApplication, QTableView, QWidget


def rect_values(rect):
    return [rect.x(), rect.y(), rect.width(), rect.height()]


def clipped_rect(widget, root):
    """Rectangular ancestor intersection, not paint/occlusion certainty."""
    if widget is root:
        return root.rect()
    rect = QRect(widget.mapTo(root, QPoint()), widget.size())
    parent = widget.parentWidget()
    while parent is not None:
        rect = rect.intersected(QRect(parent.mapTo(root, QPoint()), parent.size()))
        if parent is root:
            break
        parent = parent.parentWidget()
    return rect.intersected(root.rect())


def table_rows(table, limit=10000):
    """Count vertically contained/intersecting rows, not readable cells."""
    model = table.model()
    count = model.rowCount(table.rootIndex()) if model is not None else 0
    if count > limit:
        return {"model_rows": count, "status": "unknown: row scan limit"}
    full, partial = [], []
    viewport = table.viewport()
    bounds = viewport.rect()
    if table.isVisible() and viewport.isVisible():
        for row in range(count):
            if table.isRowHidden(row):
                continue
            top = table.rowViewportPosition(row)
            height = table.rowHeight(row)
            bottom = top + height - 1
            if height > 0 and bottom >= bounds.top() and top <= bounds.bottom():
                target = full if top >= bounds.top() and bottom <= bounds.bottom() else partial
                target.append(row)
    return {"model_rows": count, "full_vertical_rows": full,
            "partial_vertical_rows": partial, "viewport": rect_values(bounds),
            "vertical_scroll": table.verticalScrollBar().value(),
            "horizontal_scroll": table.horizontalScrollBar().value(),
            "status": "measured geometry; occlusion and cell contents unknown"}


def capture(root, widgets, output_dir):
    """Save selected widgets under caller labels; caller owns readiness/cleanup."""
    app = QApplication.instance()
    if app is None or QThread.currentThread() != app.thread():
        raise RuntimeError("Capture requires the QApplication UI thread")
    if not isinstance(root, QWidget) or not root.isVisible():
        raise ValueError("Root must be a visible QWidget; capture never shows it")
    selected = dict(widgets)
    for label, widget in selected.items():
        if not isinstance(label, str) or not label:
            raise ValueError("Use nonempty synthetic labels")
        if not isinstance(widget, QWidget) or (widget is not root and not root.isAncestorOf(widget)):
            raise ValueError("Every selected widget must belong to root")
        if widget.window() is not root.window():
            raise ValueError("Separate windows need separate captures")
    data = {"schema": 1, "captured_utc": datetime.now(timezone.utc).isoformat(),
            "environment": {"python": platform.python_version(),
                            "os": platform.system(), "os_release": platform.release(),
                            "machine": platform.machine(), "pyside": PySide6.__version__,
                            "qt": qVersion(), "plugin": app.platformName(),
                            "style": root.style().objectName(),
                            "device_pixel_ratio": root.devicePixelRatioF()},
            "root_size": [root.width(), root.height()], "widgets": {}}
    for label, widget in selected.items():
        origin = widget.mapTo(root, QPoint())
        region = widget.visibleRegion()
        center = widget.rect().center()
        hit = root.childAt(widget.mapTo(root, center))
        item = {"class": widget.metaObject().className(),
                "rect_in_root": rect_values(QRect(origin, widget.size())),
                "ancestor_intersection": rect_values(clipped_rect(widget, root)),
                "visible": widget.isVisible(), "explicitly_hidden": widget.isHidden(),
                "enabled": widget.isEnabled(),
                "visible_region_bounds": rect_values(region.boundingRect()),
                "visible_region_empty": region.isEmpty(),
                "center_in_visible_region": region.contains(center),
                "center_hit_self_or_child": hit is widget or (
                    hit is not None and widget.isAncestorOf(hit))}
        if isinstance(widget, QTableView):
            item["rows"] = table_rows(widget)
        data["widgets"][label] = item
    pixmap = root.grab()
    if pixmap.isNull():
        raise RuntimeError("Qt returned an empty widget image")
    data["image_pixels"] = [pixmap.width(), pixmap.height()]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="capture-", dir=str(output_dir)))
    if not pixmap.save(str(folder / "widget.png")):
        raise OSError("Could not save widget image; partial folder retained")
    (folder / "measurements.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return folder
