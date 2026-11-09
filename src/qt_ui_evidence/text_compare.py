"""Check paragraph-map records and compare geometry without a design verdict."""
import math

FIELDS = ('bounds_in_root', 'line_count', 'intersecting_line_count',
          'fully_contained_line_count', 'clipped')


def validate_map(value):
    if not isinstance(value, dict) or not isinstance(value.get('regions'), list):
        raise ValueError('Text map must contain a region list')
    if not isinstance(value.get('unmapped'), list):
        raise ValueError('Text map must contain an unmapped list')
    if value.get('coordinate_space') != 'root logical pixels':
        raise ValueError('Text map coordinates must be root logical pixels')
    identifiers = set()
    for region in value['regions']:
        if not isinstance(region, dict):
            raise ValueError('Invalid text region')
        identifier = region.get('id')
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError('Text region IDs must be nonempty and unique')
        identifiers.add(identifier)
        rect = region.get('bounds_in_root')
        if (not isinstance(rect, list) or len(rect) != 4 or
                any(type(v) not in (int, float) or not math.isfinite(v) for v in rect) or
                rect[2] < 0 or rect[3] < 0):
            raise ValueError('Text region bounds must be four finite coordinates')
        for field in FIELDS[1:4]:
            if type(region.get(field)) is not int or region[field] < 0:
                raise ValueError('Text line counts must be nonnegative integers')
        if not (region['fully_contained_line_count'] <= region['intersecting_line_count']
                <= region['line_count']):
            raise ValueError('Visible line counts cannot exceed the paragraph line count')
        if type(region.get('clipped')) is not bool:
            raise ValueError('Text clipping must be a boolean')


def compare_maps(before, after):
    if before is None or after is None:
        return {'status': 'unknown: text map missing from one capture'}
    left = {item['id']: item for item in before['regions']}
    right = {item['id']: item for item in after['regions']}
    regions = {}
    for identifier in sorted(left.keys() | right.keys()):
        a, b = left.get(identifier), right.get(identifier)
        if a is None or b is None:
            regions[identifier] = {'status': 'unknown: not mapped in one view; not proof of deletion'}
        else:
            regions[identifier] = {'sources': {'before': a.get('source'), 'after': b.get('source')},
                                   'changes': {field: {'before': a[field], 'after': b[field]}
                                               for field in FIELDS if a[field] != b[field]}}
    return {'regions': regions, 'unmapped': {'before': before['unmapped'], 'after': after['unmapped']},
            'limits': ['IDs match only while document structure stays unchanged.',
                       'Matched IDs do not prove unchanged text.',
                       'Images and paragraph grouping still require review.']}
