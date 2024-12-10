import sqlite3
from prettytable import PrettyTable

def view_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"\nDatabase: {db_name}")
    print("=" * 50)

    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        print("-" * 30)

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]

        # Create a PrettyTable instance
        pt = PrettyTable()
        pt.field_names = columns

        # Get all rows
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                pt.add_row(row)
            print(pt)
        else:
            print("No data in this table.")

    conn.close()

def main():
    databases = ['users.db', 'gamification.db']

    for db in databases:
        try:
            view_database(db)
        except sqlite3.Error as e:
            print(f"An error occurred while accessing {db}: {e}")

if __name__ == "__main__":
    main()