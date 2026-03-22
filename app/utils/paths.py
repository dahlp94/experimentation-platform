from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schema_dir() -> Path:
    return repo_root() / "sql" / "schema"


def synthetic_data_dir() -> Path:
    d = repo_root() / "data" / "synthetic"
    d.mkdir(parents=True, exist_ok=True)
    return d
