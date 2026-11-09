import importlib.util
import os
from pathlib import Path
import tempfile
import time
import unittest

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(os.environ.get('QT_EVIDENCE_SKILL', ROOT / 'skills' / 'qt-ui-evidence'))
SCRIPTS = SKILL / 'scripts'


def load_snapshot():
    spec = importlib.util.spec_from_file_location('qt_evidence_snapshot', SCRIPTS / 'snapshot.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


snapshot = load_snapshot()
APP = QApplication.instance() or QApplication([])
APP.setStyle('Fusion')


def wait_for(condition, timeout_ms=1000):
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        APP.processEvents()
        if condition():
            return
        QTest.qWait(10)
    raise AssertionError('UI condition did not settle within %d ms' % timeout_ms)


class GuiCase(unittest.TestCase):
    def setUp(self):
        self.owned = []
        self.temp = tempfile.TemporaryDirectory(prefix='qt-evidence-test-')
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.close_owned)

    def close_owned(self):
        for widget in self.owned:
            widget.close()
            widget.deleteLater()
        APP.processEvents()

    def show(self, widget):
        self.owned.append(widget)
        widget.show()
        wait_for(lambda: widget.isVisible() and widget.width() > 0)
        return widget

    def capture(self, widget, selected, name, **options):
        base = Path(os.environ.get('QT_EVIDENCE_OUTPUT', self.temp.name))
        return snapshot.capture(widget, selected, base / name, **options)

    def click(self, root, button):
        self.assertTrue(button.isVisible() and button.isEnabled())
        point = button.rect().center()
        self.assertTrue(button.visibleRegion().contains(point))
        hit = root.childAt(button.mapTo(root, point))
        self.assertTrue(hit is button or (hit is not None and button.isAncestorOf(hit)))
        QTest.mouseClick(button, Qt.MouseButton.LeftButton, pos=point)
