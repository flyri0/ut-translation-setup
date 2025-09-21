import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """
    Returns the absolute path to a resource, working in both development and onefile mode.
    """
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = Path(__file__).resolve().parents[
            1]

    return base_path / relative_path
