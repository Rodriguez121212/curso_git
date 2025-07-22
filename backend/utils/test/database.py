"""Database utils for test fixtures."""
import os
import pathlib
from typing import Any, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

SQLITE_DATABASE_URL = "sqlite:///.{db_url}/{db_name}"


class MockDatabase:
    """Class to manage a mock databas."""

    def __init__(self, db_name: str, path: str, Base: Any):
        """Mock Database constructor.

        Arguments:
            db_name -- database name
            path -- path
            Base -- Declarative base class.
        """
        self.sql_file = f"{path}/{db_name}"
        self.delete_sqlite()
        working_path = str(pathlib.Path().resolve())
        db_url = path.replace(working_path, "")
        self.engine = create_engine(
            SQLITE_DATABASE_URL.format(db_url=db_url, db_name=db_name),
            connect_args={"check_same_thread": False},
        )
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def load_rows(self, Model: Any, data: List[Dict[str, Any]]) -> None:
        """Load rows into the Mock Database.

        Arguments:
            Model -- Model database used to insert the data
            data -- list object of each item in the table.
        """
        with Session(self.engine) as session:
            session.add_all([Model(**row) for row in data])
            session.commit()

    def delete_sqlite(self) -> None:
        """Clean the SQLite database file used as Mock Database."""
        if pathlib.Path(self.sql_file).exists():
            os.remove(self.sql_file)

    def __del__(self) -> None:
        """Finalize Mockdatabase by deleting SQLite DB file."""
        self.delete_sqlite()
