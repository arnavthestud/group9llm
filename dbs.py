import sqlite3
import pandas as pd
from tabulate import tabulate

def view_all_users():
    conn = sqlite3.connect('users.db')
    query = "SELECT * FROM users"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No users found in the database.")
    else:
        print("Users in the database:")
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

def save_to_csv():
    conn = sqlite3.connect('users.db')
    query = "SELECT * FROM users"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No users found in the database. CSV file not created.")
    else:
        csv_filename = "users_database.csv"
        df.to_csv(csv_filename, index=False)
        print(f"Database contents saved to {csv_filename}")

def main():
    while True:
        print("\n1. View all users")
        print("2. Save users to CSV")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            view_all_users()
        elif choice == '2':
            save_to_csv()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()