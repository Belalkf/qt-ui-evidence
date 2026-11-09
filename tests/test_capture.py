import json
from pathlib import Path
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget
from tests.support import GuiCase, snapshot


class CaptureTests(GuiCase):
    def test_preserves_visibility_size_attributes_and_prior_evidence(self):
        root = self.show(QWidget())
        root.resize(240, 100)
        child = QLabel('Synthetic label', root)
        child.show()
        hidden = QLabel('Intentionally hidden', root)
        hidden.hide()
        state = (root.size(), root.isVisible(),
                 root.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen))
        first = self.capture(root, {'shown': child, 'hidden': hidden}, 'same')
        original = (first / 'widget.png').read_bytes()
        second = self.capture(root, {'shown': child}, 'same')
        self.assertNotEqual(first, second)
        self.assertEqual((first / 'widget.png').read_bytes(), original)
        self.assertEqual(state, (root.size(), root.isVisible(),
                         root.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)))
        data = json.loads((first / 'measurements.json').read_text())
        self.assertFalse(data['widgets']['hidden']['visible'])
        self.assertTrue(data['widgets']['hidden']['visible_region_empty'])
        self.assertNotIn('Synthetic label', json.dumps(data))

    def test_hidden_foreign_and_separate_window_rejected(self):
        hidden = QWidget()
        self.owned.append(hidden)
        with self.assertRaises(ValueError):
            self.capture(hidden, {}, 'hidden')
        self.assertFalse(hidden.isVisible())
        root = self.show(QWidget())
        foreign = self.show(QWidget())
        dialog = QWidget(root, Qt.WindowType.Window)
        self.owned.append(dialog)
        for item in (foreign, dialog):
            with self.assertRaises(ValueError):
                self.capture(root, {'other': item}, 'invalid')

    def test_unwritable_destination_and_image_failure_raise(self):
        root = self.show(QWidget())
        file = Path(self.temp.name) / 'existing'
        file.write_text('preserve me')
        with self.assertRaises(OSError):
            snapshot.capture(root, {}, file)
        self.assertEqual(file.read_text(), 'preserve me')
        with patch.object(snapshot, 'QWidget', QWidget):
            with patch('PySide6.QtGui.QPixmap.save', return_value=False):
                with self.assertRaises(OSError):
                    self.capture(root, {}, 'save-failure')

    def test_unicode_labels_and_root_measurement(self):
        root = self.show(QWidget())
        folder = self.capture(root, {'حالة/../é': root}, 'unicode')
        data = json.loads((folder / 'measurements.json').read_text())
        self.assertEqual(data['widgets']['حالة/../é']['rect_in_root'],
                         [0, 0, root.width(), root.height()])
        self.assertEqual(set(p.name for p in folder.iterdir()),
                         {'widget.png', 'measurements.json'})

    def test_nested_capture_root_uses_its_own_coordinates(self):
        window = self.show(QWidget())
        window.resize(100, 100)
        root = QWidget(window)
        root.setGeometry(80, 80, 90, 60)
        root.show()
        # A widget grab captures the selected root, not its parent's viewport.
        self.assertEqual(snapshot.rect_values(snapshot.clipped_rect(root, root)),
                         [0, 0, 90, 60])

    def test_wrong_thread_rejected_before_widget_access(self):
        import threading
        root = self.show(QWidget())
        failures = []

        def attempt():
            try:
                snapshot.capture(root, {}, self.temp.name)
            except RuntimeError as error:
                failures.append(str(error))

        worker = threading.Thread(target=attempt)
        worker.start()
        worker.join(timeout=2)
        self.assertFalse(worker.is_alive())
        self.assertEqual(len(failures), 1)
        self.assertIn('UI thread', failures[0])
