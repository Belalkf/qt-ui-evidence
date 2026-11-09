import json
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QLabel, QPlainTextEdit, QTextEdit

from examples.paragraphs import ParagraphWindow
from tests.support import GuiCase, wait_for


class ParagraphTests(GuiCase):
    def mapping(self, root, widgets, name='text'):
        folder = self.capture(root, widgets, name, text_map=True)
        return json.loads((folder / 'measurements.json').read_text())['text_map'], folder

    def test_wrapping_preserves_paragraphs_and_column_identity(self):
        root = self.show(ParagraphWindow())
        selected = {'left': root.left, 'right': root.right}
        wide, _ = self.mapping(root, selected, 'wide')
        self.assertEqual(len(wide['regions']), 5)
        root.resize(500, 400)
        wait_for(lambda: root.width() == 500)
        narrow, _ = self.mapping(root, selected, 'narrow')
        self.assertEqual([r['id'] for r in wide['regions']], [r['id'] for r in narrow['regions']])
        self.assertGreater(narrow['regions'][0]['line_count'], wide['regions'][0]['line_count'])
        self.assertEqual({r['widget'] for r in narrow['regions']}, {'left', 'right'})
        self.assertFalse(narrow['unmapped'])
        root.resize(720, 280)
        wait_for(lambda: root.width() == 720)
        restored, _ = self.mapping(root, selected, 'restored')
        self.assertEqual(wide['regions'], restored['regions'])

    def test_scroll_and_clip_are_measured_without_changing_state(self):
        for cls in (QTextEdit, QPlainTextEdit):
            widget = self.show(cls())
            widget.resize(270, 105)
            widget.setPlainText('\n'.join('Paragraph %d with enough words to wrap in this view.' % i
                                         for i in range(15)))
            wait_for(lambda: widget.verticalScrollBar().maximum() > 0)
            bar = widget.verticalScrollBar()
            bar.setValue(bar.maximum())
            wait_for(lambda: bar.value() == bar.maximum())
            before = (bar.value(), widget.textCursor().position(), widget.size(), widget.hasFocus())
            result, _ = self.mapping(widget, {'body': widget})
            self.assertEqual(before, (bar.value(), widget.textCursor().position(),
                                      widget.size(), widget.hasFocus()))
            self.assertTrue(result['regions'])
            self.assertNotIn('body:block-0', [r['id'] for r in result['regions']])
            for region in result['regions']:
                for x, y, width, height in region['visible_line_boxes']:
                    self.assertGreaterEqual(x, 0)
                    self.assertGreaterEqual(y, 0)
                    self.assertLessEqual(x + width, widget.width() + .01)
                    self.assertLessEqual(y + height, widget.height() + .01)

    def test_rtl_alignment_and_rich_text_use_real_line_layout(self):
        widget = self.show(QTextEdit())
        widget.resize(350, 200)
        widget.setHtml('<p align="right">مرحبا بالعالم مع نص تجريبي طويل</p>'
                       '<p align="center"><b>Large bold text</b> and normal text.</p>')
        wait_for(lambda: widget.document().begin().layout().lineCount() > 0)
        result, _ = self.mapping(widget, {'body': widget})
        self.assertEqual(len(result['regions']), 2)
        for region in result['regions']:
            block = widget.document().findBlockByNumber(region['block_number'])
            point = widget.cursorRect(QTextCursor(block)).center()
            box = region['bounds_in_root']
            self.assertLessEqual(box[1], point.y())
            self.assertGreaterEqual(box[1] + box[3], point.y())

    def test_hidden_unsupported_and_nested_content_stay_unknown(self):
        root = self.show(ParagraphWindow())
        root.right.hide()
        unsupported = QLabel('A label does not expose paragraph geometry', root)
        unsupported.show()
        result, _ = self.mapping(root, {'hidden': root.right, 'label': unsupported})
        self.assertEqual(result['regions'], [])
        self.assertEqual(len(result['unmapped']), 2)
        root.left.setHtml('<table><tr><td>Nested text</td></tr></table>')
        result, _ = self.mapping(root, {'nested': root.left})
        self.assertIn('Nested', result['unmapped'][0]['reason'])

    def test_text_is_opt_in_and_companion_image_preserves_original(self):
        widget = self.show(QTextEdit())
        widget.setPlainText('Synthetic private-style text\n\nAnother paragraph')
        wait_for(lambda: widget.document().begin().layout().lineCount() > 0)
        result, folder = self.mapping(widget, {'body': widget})
        self.assertNotIn('Synthetic private-style', json.dumps(result))
        self.assertEqual(len(result['regions']), 2)
        original = (folder / 'widget.png').read_bytes()
        self.assertTrue((folder / 'text-map.png').is_file())
        self.assertNotEqual(original, (folder / 'text-map.png').read_bytes())
        other = self.capture(widget, {'body': widget}, 'with-text', text_map=True, include_text=True)
        data = json.loads((other / 'measurements.json').read_text())
        self.assertEqual(data['text_map']['regions'][0]['source_text'], 'Synthetic private-style text')
        self.assertEqual((folder / 'widget.png').read_bytes(), original)

    def test_partial_paragraph_and_scan_limit_are_explicit(self):
        widget = self.show(QTextEdit())
        widget.resize(180, 60)
        widget.setPlainText('A long synthetic paragraph with enough words to wrap. ' * 8)
        wait_for(lambda: widget.document().begin().layout().lineCount() > 3)
        result, _ = self.mapping(widget, {'body': widget})
        region = result['regions'][0]
        self.assertTrue(region['clipped'])
        self.assertLess(region['intersecting_line_count'], region['line_count'])
        widget.setPlainText('\n'.join('text' for _ in range(1001)))
        result, _ = self.mapping(widget, {'body': widget})
        self.assertEqual(result['regions'], [])
        self.assertIn('scan limit', result['unmapped'][0]['reason'])

    def test_unpainted_plain_text_blocks_are_not_forced_into_layout(self):
        widget = self.show(QPlainTextEdit())
        widget.resize(250, 100)
        widget.setPlainText('\n'.join('Paragraph %d with enough words to wrap here.' % i
                                     for i in range(80)))
        wait_for(lambda: widget.document().begin().layout().lineCount() > 0)
        bar = widget.verticalScrollBar()
        before = (bar.value(), bar.maximum())
        result, _ = self.mapping(widget, {'body': widget})
        self.assertEqual((bar.value(), bar.maximum()), before)
        self.assertFalse(result['unmapped'])
        self.assertLess(len(result['regions']), 80)
