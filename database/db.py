"""
Database Access Layer (DAO) for Hospital Allocation System.
Manages SQLite connection pooling, query execution, transactions, and object mapping.
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "hospital.db")

def get_db_connection():
    """
    Returns a connection to SQLite database with dictionary row factory.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """
    Executes a SELECT query and returns rows as list of dictionaries.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute_statement(statement: str, params: tuple = ()) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE query and returns affected rows count.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(statement, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def execute_many(statement: str, params_list: List[tuple]) -> int:
    """
    Executes a bulk INSERT or UPDATE statement.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(statement, params_list)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def log_system_event(event_type: str, message: str, execution_time_ms: Optional[float] = None):
    """
    Logs system actions and algorithmic execution timing.
    """
    query = "INSERT INTO system_logs (event_type, message, execution_time_ms) VALUES (?, ?, ?)"
    execute_statement(query, (event_type, message, execution_time_ms))
