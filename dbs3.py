import sqlite3
from tabulate import tabulate

def view_all_items():
    conn = sqlite3.connect('generated_items.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    
    headers = ["Item", "Type", "User ID", "Timestamp"]
    
    print(tabulate(items, headers=headers, tablefmt="grid"))
    
    conn.close()

def view_user_items(user_id):
    conn = sqlite3.connect('generated_items.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM items WHERE user_id = ?", (user_id,))
    items = c.fetchall()
    
    if items:
        headers = ["Item", "Type", "User ID", "Timestamp"]
        print(tabulate(items, headers=headers, tablefmt="grid"))
    else:
        print(f"No items found for user ID: {user_id}")
    
    conn.close()

def main():
    while True:
        print("\n1. View all items")
        print("2. View items for a specific user")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            view_all_items()
        elif choice == '2':
            user_id = input("Enter user ID: ")
            view_user_items(user_id)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()