import json
from pathlib import Path
import tempfile
import unittest

from qt_ui_evidence.compare import compare, read_capture


def capture(region=True):
    regions = [{'id': 'body:block-0', 'source': 'qt-document',
                'bounds_in_root': [4, 4, 180, 60], 'line_count': 4,
                'intersecting_line_count': 4, 'fully_contained_line_count': 4,
                'clipped': False, 'source_text': 'Text must stay out of comparison output'}]
    return {'schema': 1, 'environment': {}, 'widgets': {},
            'text_map': {'coordinate_space': 'root logical pixels',
                         'regions': regions if region else [], 'unmapped': []}}


class TextComparisonTests(unittest.TestCase):
    def test_reflow_is_reported_without_copying_text_or_claiming_a_defect(self):
        before, after = capture(), capture()
        item = after['text_map']['regions'][0]
        item.update(bounds_in_root=[4, 4, 480, 30], line_count=2,
                    intersecting_line_count=2, fully_contained_line_count=2)
        result = compare(before, after)['text_map']
        self.assertEqual(result['regions']['body:block-0']['changes']['line_count'],
                         {'before': 4, 'after': 2})
        self.assertNotIn('Text must stay', json.dumps(result))
        self.assertNotIn('verdict', result)

    def test_missing_map_or_region_is_unknown_not_a_deleted_paragraph(self):
        before, after = capture(), capture(False)
        result = compare(before, after)['text_map']
        self.assertIn('unknown', result['regions']['body:block-0']['status'])
        after.pop('text_map')
        self.assertIn('unknown', compare(before, after)['text_map']['status'])

    def test_invalid_bounds_ids_and_line_counts_are_rejected(self):
        cases = []
        for value in ([0, 0, -1, 30], [0, 0, float('nan'), 30], [True, 0, 20, 30]):
            item = capture()
            item['text_map']['regions'][0]['bounds_in_root'] = value
            cases.append(item)
        duplicate = capture()
        duplicate['text_map']['regions'] *= 2
        cases.append(duplicate)
        impossible = capture()
        impossible['text_map']['regions'][0]['intersecting_line_count'] = 5
        cases.append(impossible)
        wrong_space = capture()
        wrong_space['text_map']['coordinate_space'] = 'image pixels'
        cases.append(wrong_space)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'capture.json'
            for item in cases:
                path.write_text(json.dumps(item))
                with self.subTest(item=item), self.assertRaises(ValueError):
                    read_capture(path)
