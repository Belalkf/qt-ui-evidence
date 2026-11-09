# Find text paragraphs and their locations

Use a text map when the complaint concerns text that appears split, clipped, crowded or grouped with the wrong content. A numbered region connects the actual text layout to a fresh image. It is evidence for review, not an automatic design verdict.

## Prefer the application's text data

With the optional helper, call `capture(window, selected_widgets, output_dir, text_map=True)`. It adds `text-map.png` beside the unchanged `widget.png`, and a `text_map` section in the JSON. The numbered image marks each paragraph and its measured line rectangles. Always inspect the original too, since markers cover some pixels.

The first implementation supports QTextEdit, QTextBrowser and QPlainTextEdit with their standard document layouts. Qt supplies paragraph identity and line geometry; wrapping one paragraph into more lines does not create more paragraphs. Selected widgets in separate columns keep separate identities. Empty, hidden and wholly outside-view text is excluded. Unsupported widgets, nested frames/tables, inline objects, missing layout and scan limits are reported in `unmapped`; an empty region list does not prove there is no text.

Bounds use logical coordinates relative to the captured root, including viewport placement and current scrolling. They describe Qt line layout, not exact glyph ink. The companion image uses the original device pixel ratio. Clipping is measured against the viewport, ancestor rectangles and capture bounds; other-window exposure, masks and physical display correctness remain unknown. Block numbers are useful across resizing/scrolling while the document structure stays the same, not permanent identities across edits.

The JSON omits text by default. `include_text=True` explicitly includes the complete source paragraph, potentially including its offscreen portion. Use synthetic inputs or keep that evidence private. This option requires `text_map=True`. The helper never changes the document, selection, cursor, focus or scroll position. It scans at most 1000 blocks/100000 characters per document and emits at most 200 regions, with at most 2000 lines per block.

## When only a picture is available

Use an existing local OCR tool when it helps; OCR means reading text from an image. Do not install an engine or language data silently. For example, an installed Tesseract can return words, line/paragraph grouping and rectangles using `tesseract widget.png stdout -l eng tsv`. Select installed languages appropriate to the content; English is only an example. Keep processing local unless sending the image elsewhere was explicitly authorized.

Treat OCR paragraphs as estimated visual groups. Engine confidence about a word is not confidence that a paragraph is grouped correctly. Record the engine/language, image dimensions, grouping source and uncertainties. Map image coordinates back only when the crop, resize and display-scale transforms are known. A failed recognition is unknown, not proof that a paragraph is absent or the interface is broken. The helper does not run OCR or merge its output automatically.

## Review realistic cases

Compare the same content before/after resizing, scrolling and restoration. Include a paragraph that wraps correctly, distinct nearby columns, blank separators, mixed text directions, a partly clipped paragraph and an unsupported text surface. Check that separate columns stay separate, hidden text is not claimed visible and normal wrapping is not flagged as splitting. If the expected grouping is a design judgment, label it as such and explain the user's intended relationship.
