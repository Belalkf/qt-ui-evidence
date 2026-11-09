"""Qt evidence helpers; Qt is loaded only when capture is requested."""
from importlib.metadata import version

__version__ = version('qt-ui-evidence')


def capture(root, widgets, output_dir):
    """Capture in the application's UI thread; requires PySide6."""
    from ._skill.scripts.snapshot import capture as take_snapshot
    return take_snapshot(root, widgets, output_dir)
