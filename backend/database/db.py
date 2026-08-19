import sqlite3
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "agent.db"


def get_connection():
    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            task TEXT NOT NULL,

            status TEXT,

            generated_code TEXT,

            test_code TEXT,

            execution_result TEXT,

            test_result TEXT,

            review TEXT,

            final_report TEXT,

            retry_count INTEGER DEFAULT 0,

            error TEXT,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()

    connection.close()


def create_run(
    task: str,
    result: dict,
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO runs (
            task,
            status,
            generated_code,
            test_code,
            execution_result,
            test_result,
            review,
            final_report,
            retry_count,
            error
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task,
            result.get("status", ""),
            result.get(
                "generated_code",
                "",
            ),
            result.get(
                "test_code",
                "",
            ),
            result.get(
                "execution_result",
                "",
            ),
            result.get(
                "test_result",
                "",
            ),
            result.get(
                "review",
                "",
            ),
            result.get(
                "final_report",
                "",
            ),
            result.get(
                "retry_count",
                0,
            ),
            result.get(
                "error",
                "",
            ),
        ),
    )

    run_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return run_id


def get_runs():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            task,
            status,
            retry_count,
            created_at
        FROM runs
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_run(
    run_id: int,
) -> Optional[dict]:

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM runs
        WHERE id = ?
        """,
        (run_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)