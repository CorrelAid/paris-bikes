from pathlib import Path


def get_data_root() -> Path:
    return Path(__file__).parent.parent / "data"
