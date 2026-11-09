import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from qt_ui_evidence.cli import main
from qt_ui_evidence.compare import compare, read_capture


def record(rows=(0, 1, 2), plugin='offscreen'):
    return {'schema': 1, 'environment': {'plugin': plugin}, 'root_size': [400, 300],
            'widgets': {'table': {'visible': True, 'rows': {
                'model_rows': 12, 'full_vertical_rows': list(rows),
                'partial_vertical_rows': []}}}}


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def save(self, name, data):
        path = self.folder / name
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def test_rows_unchanged_and_increased_are_facts_not_verdicts(self):
        before = record()
        unchanged = compare(before, record())
        changed = compare(before, record(range(6)))
        key = 'full_vertical_rows'
        self.assertEqual(unchanged['widgets']['table']['row_counts'][key]['delta'], 0)
        self.assertEqual(changed['widgets']['table']['row_counts'][key],
                         {'before': 3, 'after': 6, 'delta': 3})
        self.assertIn('Images were not inspected', changed['unknowns'][0])
        self.assertNotIn('verdict', changed)

    def test_missing_widget_and_missing_rows_stay_unknown(self):
        after = record()
        del after['widgets']['table']['rows']['full_vertical_rows']
        result = compare(record(), after)
        self.assertIn('unknown', result['widgets']['table']['row_counts']['full_vertical_rows']['status'])
        after['widgets'].clear()
        self.assertIn('unknown', compare(record(), after)['widgets']['table']['status'])

    def test_changed_environment_is_reported(self):
        result = compare(record(), record(plugin='cocoa'))
        self.assertEqual(result['environment_changes']['plugin'],
                         {'before': 'offscreen', 'after': 'cocoa'})
        self.assertTrue(any('missing' in item for item in result['unknowns']))

    def test_invalid_input_is_rejected(self):
        for data in ([], {}, {'schema': 2}, {'schema': 1, 'widgets': []}):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    read_capture(self.save('bad.json', data))
        for rows in (None, 'three', {'full_vertical_rows': [1, 1]},
                     {'full_vertical_rows': [-1]}, {'full_vertical_rows': [True]}):
            data = record()
            data['widgets']['table']['rows'] = rows
            with self.subTest(rows=rows):
                with self.assertRaises(ValueError):
                    read_capture(self.save('bad-rows.json', data))

    def test_oversize_and_invalid_json_are_rejected(self):
        path = self.folder / 'large.json'
        path.write_bytes(b' ' * 2_000_001)
        with self.assertRaises(ValueError):
            read_capture(path)
        path.write_text('{')
        with self.assertRaises(ValueError):
            read_capture(path)

    def test_cli_reads_directory_and_never_edits_inputs(self):
        before = self.save('measurements.json', record())
        after = self.save('after.json', record(range(6)))
        original = before.read_bytes()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(['compare', str(self.folder), str(after)])
        self.assertEqual(status, 0)
        self.assertEqual(before.read_bytes(), original)
        self.assertEqual(json.loads(output.getvalue())['widgets']['table']
                         ['row_counts']['full_vertical_rows']['delta'], 3)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['compare', str(before), str(self.folder/'missing')]), 2)

    def test_scroll_context_is_kept_when_row_counts_match(self):
        before, after = record(), record(rows=(3, 4, 5))
        before['widgets']['table']['rows'].update(
            vertical_scroll=0, horizontal_scroll=0, viewport=[0, 0, 300, 90])
        after['widgets']['table']['rows'].update(
            vertical_scroll=90, horizontal_scroll=0, viewport=[0, 0, 300, 90])
        result = compare(before, after)['widgets']['table']
        self.assertEqual(result['row_counts']['full_vertical_rows']['delta'], 0)
        self.assertEqual(result['row_context']['vertical_scroll'],
                         {'before': 0, 'after': 90})
        self.assertEqual(result['row_context']['full_vertical_rows'],
                         {'before': [0, 1, 2], 'after': [3, 4, 5]})
