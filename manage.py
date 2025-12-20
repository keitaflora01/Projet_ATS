#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    try:
        from django.core.management import execute_from_command_line  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(  # noqa: TRY003
            "Couldn't import Django. Are you sure it's installed and "  # noqa: EM101
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?",
        ) from exc

    # Ensure the project root is on sys.path so package imports like
    # `ats.users` resolve correctly. Previously this appended the
    # interior `ats` directory which broke imports.
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path))

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
