import sqlite3
from tabulate import tabulate

def view_all_user_stats():
    conn = sqlite3.connect('gamification.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM user_stats")
    users = c.fetchall()
    
    headers = ["User ID", "Vocab Attempts", "Exercise Attempts", "Total Score", "Points", "Level", "Last Login"]
    
    print(tabulate(users, headers=headers, tablefmt="grid"))
    
    conn.close()

def view_user_stats(user_id):
    conn = sqlite3.connect('gamification.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    
    if user:
        headers = ["User ID", "Vocab Attempts", "Exercise Attempts", "Total Score", "Points", "Level", "Last Login"]
        print(tabulate([user], headers=headers, tablefmt="grid"))
    else:
        print(f"No user found with ID: {user_id}")
    
    conn.close()

def main():
    while True:
        print("\n1. View all user stats")
        print("2. View specific user stats")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            view_all_user_stats()
        elif choice == '2':
            user_id = input("Enter user ID: ")
            view_user_stats(user_id)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()