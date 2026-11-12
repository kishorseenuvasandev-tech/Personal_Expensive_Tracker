
import sqlite3


def connect_db():
    conn = sqlite3.connect("expenses.db")
    return conn


def create_table():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_name TEXT,
            category TEXT,
            amount REAL
        )
    """)

    # Check whether expense_date column already exists
    cursor.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in cursor.fetchall()]

    # Add date column if it does not exist
    if "expense_date" not in columns:
        cursor.execute("""
            ALTER TABLE expenses
            ADD COLUMN expense_date TEXT
        """)

    # Set today's date for existing expenses without a date
    cursor.execute("""
        UPDATE expenses
        SET expense_date = DATE('now', 'localtime')
        WHERE expense_date IS NULL
    """)

    conn.commit()
    conn.close()
