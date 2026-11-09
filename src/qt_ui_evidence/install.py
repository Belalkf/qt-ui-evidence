"""Explicit skill installation; never run automatically during pip install."""
from importlib import resources
from pathlib import Path
import shutil
import tempfile


RESOURCE_FILES = (
    'SKILL.md', 'agents/openai.yaml', 'references/measurements.md',
    'scripts/snapshot.py', 'scripts/text_map.py', 'references/paragraphs.md',
)


def install_skill(destination):
    """Create destination once. Preserve any existing file, directory or link."""
    destination = Path(destination).expanduser()
    source = resources.files('qt_ui_evidence._skill')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Stage beside the target so a resource-read failure leaves it untouched.
    stage = Path(tempfile.mkdtemp(prefix='.qt-ui-evidence-', dir=destination.parent))
    try:
        for relative in RESOURCE_FILES:
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.joinpath(relative).read_bytes())
        destination.mkdir()  # Atomic claim; refuses links and existing directories.
        for relative in RESOURCE_FILES:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(stage / relative, target)
    finally:
        # A partial installation is retained if writing failed or was cancelled.
        shutil.rmtree(stage)
    return destination
