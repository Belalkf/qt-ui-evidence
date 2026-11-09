from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from examples.inventory import Inventory
from tests.support import GuiCase, snapshot, wait_for


class RowPreferenceTests(GuiCase):
    def test_setting_change_has_measurable_effect_only_after_repair(self):
        counts = {}
        for repaired in (False, True):
            widget = self.show(Inventory(repaired))
            wait_for(lambda: len(snapshot.table_rows(widget.table)['full_vertical_rows']) == 3)
            self.capture(widget, {'table': widget.table}, 'rows-%s-before' % repaired)
            widget.preference.setFocus()
            widget.preference.selectAll()
            QTest.keyClicks(widget.preference, '6')
            QTest.keyClick(widget.preference, Qt.Key.Key_Enter)
            wait_for(lambda: widget.preference.value() == 6)
            if repaired:
                wait_for(lambda: len(snapshot.table_rows(widget.table)['full_vertical_rows']) == 6)
            counts[repaired] = len(snapshot.table_rows(widget.table)['full_vertical_rows'])
            self.capture(widget, {'table': widget.table}, 'rows-%s-after' % repaired)
            self.assertEqual(widget.table.rowCount(), 12)
        self.assertEqual(counts, {False: 3, True: 6})

    def test_small_dataset_is_valid(self):
        widget = self.show(Inventory(True, rows=2))
        wait_for(lambda: len(snapshot.table_rows(widget.table)['full_vertical_rows']) == 2)
        self.assertEqual(snapshot.table_rows(widget.table)['model_rows'], 2)

    def test_hidden_partial_scrolled_and_empty_rows(self):
        widget = self.show(Inventory(True))
        table = widget.table
        table.setRowHidden(1, True)
        table.setVerticalScrollMode(table.ScrollMode.ScrollPerPixel)
        table.setFixedHeight(110)
        table.verticalScrollBar().setValue(11)
        wait_for(lambda: table.verticalScrollBar().value() == 11)
        rows = snapshot.table_rows(table)
        self.assertNotIn(1, rows['full_vertical_rows'] + rows['partial_vertical_rows'])
        self.assertTrue(rows['partial_vertical_rows'])
        self.assertFalse(set(rows['full_vertical_rows']) & set(rows['partial_vertical_rows']))
        table.hide()
        self.assertEqual(snapshot.table_rows(table)['full_vertical_rows'], [])
        table.setRowCount(0)
        self.assertEqual(snapshot.table_rows(table)['model_rows'], 0)

    def test_scan_limit_reports_unknown(self):
        widget = self.show(Inventory())
        self.assertIn('unknown', snapshot.table_rows(widget.table, limit=1)['status'])
