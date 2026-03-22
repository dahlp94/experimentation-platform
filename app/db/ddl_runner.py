from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine


def run_schema_ddl(engine: Engine, schema_directory: Path) -> None:
    sql_files = sorted(schema_directory.glob("*.sql"))
    if not sql_files:
        raise FileNotFoundError(f"No .sql files in {schema_directory}")
    with engine.begin() as conn:
        for path in sql_files:
            stmt = path.read_text(encoding="utf-8")
            conn.execute(text(stmt))
