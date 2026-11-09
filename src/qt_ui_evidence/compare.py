"""Compare capture facts, without claiming a layout or native-display verdict."""
import json
from pathlib import Path

from .text_compare import compare_maps, validate_map

MAX_BYTES = 2_000_000
FIELDS = ('rect_in_root', 'ancestor_intersection', 'visible', 'explicitly_hidden',
          'enabled', 'center_in_visible_region', 'center_hit_self_or_child')
ENVIRONMENT = ('os', 'os_release', 'machine', 'python', 'pyside', 'qt', 'plugin',
               'style', 'device_pixel_ratio')


def read_capture(path):
    path = Path(path)
    if path.is_dir():
        path = path / 'measurements.json'
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Capture exceeds the 2 MB comparison limit')
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ValueError('Expected a schema 1 capture')
    if not isinstance(data.get('widgets'), dict) or not isinstance(data.get('environment'), dict):
        raise ValueError('Capture must contain widget and environment objects')
    for label, widget in data['widgets'].items():
        if not isinstance(label, str) or not isinstance(widget, dict):
            raise ValueError('Invalid widget record')
        rows = widget.get('rows')
        if 'rows' in widget:
            if not isinstance(rows, dict):
                raise ValueError('Invalid rows record')
            for field in ('full_vertical_rows', 'partial_vertical_rows'):
                indices = rows.get(field)
                if indices is not None and (not isinstance(indices, list) or
                        any(type(i) is not int or i < 0 for i in indices) or
                        len(indices) != len(set(indices))):
                    raise ValueError('Row indices must be unique nonnegative integer lists')
    if "text_map" in data:
        validate_map(data["text_map"])
    return data


def compare(before, after):
    """Return observed changes; caller decides whether they meet the complaint."""
    differences = {}
    unknowns = ['Images were not inspected by this command.',
                'No pass/fail, font, accessibility or native-display verdict is inferred.']
    for key in ENVIRONMENT:
        left, right = before['environment'].get(key), after['environment'].get(key)
        if left is None or right is None:
            unknowns.append('Environment field missing: ' + key)
        elif left != right:
            differences[key] = {'before': left, 'after': right}
    results = {}
    labels = before['widgets'].keys() | after['widgets'].keys()
    for label in sorted(labels):
        left, right = before['widgets'].get(label), after['widgets'].get(label)
        if left is None or right is None:
            results[label] = {'status': 'unknown: widget missing from one capture'}
            continue
        changes = {key: {'before': left.get(key), 'after': right.get(key)}
                   for key in FIELDS if left.get(key) != right.get(key)}
        row_counts = {}
        row_context = {}
        if 'rows' in left or 'rows' in right:
            for field in ('viewport', 'vertical_scroll', 'horizontal_scroll',
                          'full_vertical_rows', 'partial_vertical_rows'):
                row_context[field] = {'before': left.get('rows', {}).get(field),
                                      'after': right.get('rows', {}).get(field)}
            for field in ('full_vertical_rows', 'partial_vertical_rows'):
                a, b = left.get('rows', {}).get(field), right.get('rows', {}).get(field)
                row_counts[field] = ({'before': len(a), 'after': len(b), 'delta': len(b)-len(a)}
                                     if isinstance(a, list) and isinstance(b, list)
                                     else {'status': 'unknown: row measurement unavailable'})
            changes['model_rows'] = {'before': left.get('rows', {}).get('model_rows'),
                                     'after': right.get('rows', {}).get('model_rows')}
        results[label] = {'changes': changes, 'row_counts': row_counts,
                         'row_context': row_context}
    result = {'schema': 1, 'environment_changes': differences,
            'root_size': {'before': before.get('root_size'), 'after': after.get('root_size')},
            'widgets': results, 'unknowns': unknowns}
    if 'text_map' in before or 'text_map' in after:
        result['text_map'] = compare_maps(before.get('text_map'), after.get('text_map'))
    return result
