"""Locate Qt text paragraphs; rectangles describe layout, not exact glyph ink."""
from PySide6.QtCore import QPoint, QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QTextEdit


def values(rect):
    return [round(value, 3) for value in
            (rect.x(), rect.y(), rect.width(), rect.height())]


def paragraphs(root, widgets, clip_bounds, include_text=False):
    """Map selected text editors without changing text, cursor, focus or scroll."""
    result = {'coordinate_space': 'root logical pixels', 'regions': [], 'unmapped': [],
              'limits': ['Qt layout bounds are not exact glyph-ink boundaries.',
                         'Clipping is measured; physical exposure and readability are unknown.',
                         'Block identities match only while document structure is unchanged.']}
    for label, widget in widgets.items():
        def unknown(reason):
            result['unmapped'].append({'widget': label, 'reason': reason})

        if not isinstance(widget, (QTextEdit, QPlainTextEdit)):
            unknown('No paragraph geometry for this widget; use image review or optional OCR.')
            continue
        if not widget.isVisible():
            unknown('Hidden widget excluded; this is not a defect verdict.')
            continue
        document = widget.document()
        if document.blockCount() > 1000 or document.characterCount() > 100000:
            unknown('Document exceeds the 1000-block or 100000-character scan limit.')
            continue
        if document.rootFrame().childFrames():
            unknown('Nested text frames and tables are not supported.')
            continue
        expected_layout = ('QPlainTextDocumentLayout' if isinstance(widget, QPlainTextEdit)
                           else 'QTextDocumentLayout')
        if document.documentLayout().metaObject().className() != expected_layout:
            unknown('Custom document layout is not supported.')
            continue
        viewport = widget.viewport()
        clip = QRectF(clip_bounds(viewport, root))
        origin = QPointF(viewport.mapTo(root, QPoint()))
        plain = isinstance(widget, QPlainTextEdit)
        last_visible = (widget.cursorForPosition(viewport.rect().bottomRight()).blockNumber()
                        if plain else document.blockCount() - 1)
        block = widget.firstVisibleBlock() if plain else document.begin()
        while block.isValid() and block.blockNumber() <= last_visible:
            if len(result['regions']) >= 200:
                unknown('Map stopped at the 200-region limit.')
                break
            text = block.text()
            layout = block.layout()
            count = layout.lineCount()
            if text.strip() and block.isVisible():
                if '\ufffc' in text:
                    unknown('Inline objects are not supported in block %d.' % block.blockNumber())
                elif not count or count > 2000:
                    unknown('Block layout unavailable or over the 2000-line limit.')
                else:
                    if plain:
                        geometry = widget.blockBoundingGeometry(block).translated(widget.contentOffset())
                        if geometry.top() > viewport.height():
                            break
                        offset = origin + geometry.topLeft()
                    else:
                        first = layout.lineAt(0)
                        caret = widget.cursorRect(QTextCursor(block))
                        caret_x = first.cursorToX(first.textStart())[0]
                        offset = origin + QPointF(caret.x() - caret_x, caret.y() - first.y())
                    lines = [layout.lineAt(index).naturalTextRect().translated(offset)
                             for index in range(count)]
                    visible = [rect.intersected(clip) for rect in lines if rect.intersects(clip)]
                    if visible:
                        bounds = QRectF()
                        for rect in lines:
                            bounds = bounds.united(rect)
                        item = {'id': '%s:block-%d' % (label, block.blockNumber()),
                                'widget': label, 'source': 'qt-document', 'kind': 'paragraph',
                                'block_number': block.blockNumber(), 'character_count': len(text),
                                'bounds_in_root': values(bounds),
                                'line_count': count, 'intersecting_line_count': len(visible),
                                'fully_contained_line_count': sum(clip.contains(rect) for rect in lines),
                                'clipped': any(not clip.contains(rect) for rect in lines),
                                'visible_line_boxes': [values(rect) for rect in visible]}
                        if include_text:
                            item['source_text'] = text
                        result['regions'].append(item)
            block = block.next()
    for index, region in enumerate(result['regions'], 1):
        region['marker'] = 'P%d' % index
    return result


def annotate(pixmap, mapping):
    """Draw numbered measured bounds on a copy; keep the original image intact."""
    result = pixmap.copy()
    painter = QPainter(result)
    try:
        painter.setPen(QPen(QColor('#c00058'), 1.5))
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        for region in mapping['regions']:
            for box in region['visible_line_boxes']:
                painter.drawRect(QRectF(*box))
            first = QRectF(*region['visible_line_boxes'][0])
            label = region['marker']
            label_box = QRectF(first.x(), first.y(), 34, 16)
            painter.fillRect(label_box, QColor('#fff3aa'))
            painter.drawText(label_box, label)
    finally:
        painter.end()
    return result
