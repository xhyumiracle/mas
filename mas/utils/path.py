from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
def relative_to_root(file_path: str, *subpaths: str):
    return Path(file_path).resolve().relative_to(PROJECT_ROOT).joinpath(*subpaths).as_posix()


def relative_parent_to_root(file_path: str, *subpaths: str):
    return Path(file_path).parent.resolve().relative_to(PROJECT_ROOT).joinpath(*subpaths).as_posix()