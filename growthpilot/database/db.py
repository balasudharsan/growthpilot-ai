import json
import logging
import os
import pathlib
import sqlite3
from typing import Any


logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL and DATABASE_URL.startswith(("postgresql", "postgres")))
PLACEHOLDER = "%s" if IS_POSTGRES else "?"
DB_PATH = pathlib.Path(__file__).resolve().parent / "growthpilot.db"


def get_connection():
    if IS_POSTGRES:
        import psycopg2

        return psycopg2.connect(DATABASE_URL)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def init_db() -> None:
    try:
        logger.info(f"Initialising database: {'PostgreSQL' if IS_POSTGRES else 'SQLite'}")
        conn = get_connection()
        try:
            if IS_POSTGRES:
                conn.autocommit = True

            cursor = conn.cursor()
            if IS_POSTGRES:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS business_inputs (
                        id SERIAL PRIMARY KEY,
                        payload_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reports (
                        id SERIAL PRIMARY KEY,
                        input_id INTEGER,
                        report_json TEXT NOT NULL,
                        pdf_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS business_inputs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        payload_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        input_id INTEGER,
                        report_json TEXT NOT NULL,
                        pdf_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                conn.commit()
            logger.info("Database initialised successfully")
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"init_db failed: {e}")
        raise


def save_input(payload: dict[str, Any]) -> int:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO business_inputs (payload_json)
                VALUES ({PLACEHOLDER})
                {"RETURNING id" if IS_POSTGRES else ""}
                """,
                (json.dumps(payload, ensure_ascii=True),),
            )
            row = cursor.fetchone() if IS_POSTGRES else None
            conn.commit()
            return int(row[0] if IS_POSTGRES else cursor.lastrowid)
    except Exception:
        logger.exception("Saving business input failed")
        raise


def save_report(input_id: int, report: dict[str, Any], pdf_path: str) -> int:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO reports (input_id, report_json, pdf_path)
                VALUES ({PLACEHOLDER}, {PLACEHOLDER}, {PLACEHOLDER})
                {"RETURNING id" if IS_POSTGRES else ""}
                """,
                (input_id, json.dumps(report, ensure_ascii=True), pdf_path),
            )
            row = cursor.fetchone() if IS_POSTGRES else None
            conn.commit()
            return int(row[0] if IS_POSTGRES else cursor.lastrowid)
    except Exception:
        logger.exception("Saving report failed")
        raise
