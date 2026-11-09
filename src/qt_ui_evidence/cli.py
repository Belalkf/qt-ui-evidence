"""Portable comparisons and explicit Codex skill installation."""
import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .compare import compare, read_capture
from .install import install_skill


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version=__version__)
    commands = parser.add_subparsers(dest='command', required=True)
    diff = commands.add_parser('compare', help='Compare measurement JSON; never gives a visual verdict')
    diff.add_argument('before', type=Path)
    diff.add_argument('after', type=Path)
    install = commands.add_parser('install-skill', help='Install skill explicitly; refuse existing paths')
    scope = install.add_mutually_exclusive_group(required=True)
    scope.add_argument('--user', action='store_true', help='Use ~/.agents/skills/qt-ui-evidence')
    scope.add_argument('--project', type=Path, help='Use PROJECT/.agents/skills/qt-ui-evidence')
    args = parser.parse_args(argv)
    try:
        if args.command == 'compare':
            result = compare(read_capture(args.before), read_capture(args.after))
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            base = Path.home() if args.user else args.project
            destination = install_skill(base / '.agents' / 'skills' / 'qt-ui-evidence')
            print('Installed skill:', destination)
            print('Invoke $qt-ui-evidence in Codex. Qt runtime is a separate prerequisite.')
    except (OSError, ValueError) as error:
        print('qt-ui-evidence:', error, file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('Cancelled; inspect any partial installation before retrying.', file=sys.stderr)
        return 130
    return 0
