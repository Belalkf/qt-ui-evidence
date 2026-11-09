from PySide6.QtCore import QPoint, QRect
from examples.station import Station
from tests.support import GuiCase, snapshot, wait_for


class LayoutTests(GuiCase):
    def test_overlap_and_clipping_with_valid_nested_decoration(self):
        for repaired in (False, True):
            widget = self.show(Station(repaired))
            self.capture(widget, {'action': widget.action, 'status': widget.status,
                                  'badge': widget.badge}, 'layout-%s' % repaired)
            a, b = widget.action, widget.status
            a_rect = QRect(a.mapTo(widget, QPoint()), a.size())
            b_rect = QRect(b.mapTo(widget, QPoint()), b.size())
            self.assertEqual(a_rect.intersects(b_rect), not repaired)
            clipped = snapshot.clipped_rect(a, widget)
            self.assertEqual(clipped.width() < a.width(), not repaired)
            # A child badge inside its button is intentional, never a defect verdict.
            self.assertTrue(a.rect().contains(widget.badge.geometry()))

    def test_collapse_expand_and_resize_round_trip(self):
        for repaired in (False, True):
            widget = self.show(Station(repaired))
            self.click(widget, widget.toggle)
            wait_for(lambda: widget.toggle.isChecked())
            self.assertEqual(widget.panel.isVisible(), not repaired)
            self.capture(widget, {'panel': widget.panel}, 'collapse-%s' % repaired)
            self.click(widget, widget.toggle)
            wait_for(lambda: not widget.toggle.isChecked() and widget.panel.isVisible())
            for width in (300, 540, 300):
                widget.resize(width, 220)
                wait_for(lambda: widget.width() == width)
                self.capture(widget, {'panel': widget.panel, 'action': widget.action},
                             'resize-%s-%d' % (repaired, width))
                if repaired:
                    self.assertEqual(snapshot.clipped_rect(widget.action, widget).width(),
                                     widget.action.width())
            self.click(widget, widget.toggle)
            self.assertEqual(widget.panel.isVisible(), not repaired)
