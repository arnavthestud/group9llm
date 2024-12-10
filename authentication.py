import streamlit as st
import sqlite3
import hashlib
import datetime as datetime
# Initialize the database
def get_current_user_id():
    if 'username' in st.session_state:
        return st.session_state['username']
    return None

def init_auth_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create the users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, proficiency TEXT)''')
    
    # Check if the proficiency column exists
    c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'proficiency' not in columns:
        # Add the proficiency column if it doesn't exist
        c.execute("ALTER TABLE users ADD COLUMN proficiency TEXT")
    
    conn.commit()
    conn.close()

# Hash the password
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Check if the user exists and the password is correct
def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result is not None

# Add a new user
def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, proficiency) VALUES (?, ?, ?)", (username, hash_password(password), None))
    conn.commit()
    conn.close()

# Update user's proficiency
def update_proficiency(username, proficiency):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET proficiency = ? WHERE username = ?", (proficiency, username))
    conn.commit()
    conn.close()

# Get user's proficiency
def get_proficiency(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT proficiency FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Login page
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_user(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# Registration page
def register():
    st.title("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    if st.button("Register"):
        if new_username and new_password:
            add_user(new_username, new_password)
            st.success("Registration successful! Please log in.")
        else:
            st.error("Please enter both username and password")

# Check if the user is logged in
def is_logged_in():
    return 'logged_in' in st.session_state and st.session_state['logged_in']

# Logout function
def logout():
    st.session_state['logged_in'] = False
    st.session_state.pop('username', None)
    st.success("Logged out successfully!")
    st.rerun()
def update_user_progress(user_id, lesson_name, completed_subtopic=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Check if the progress table exists, if not, create it
    c.execute('''CREATE TABLE IF NOT EXISTS user_progress
                 (user_id TEXT, lesson_name TEXT, completed_subtopic TEXT, 
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 PRIMARY KEY (user_id, lesson_name, completed_subtopic))''')
    
    if completed_subtopic:
        # Insert the new completed subtopic
        c.execute('''INSERT OR REPLACE INTO user_progress (user_id, lesson_name, completed_subtopic, timestamp)
                     VALUES (?, ?, ?, ?)''', (user_id, lesson_name, completed_subtopic, datetime.datetime.now()))
    
    # Get all completed subtopics for this user and lesson
    c.execute("SELECT completed_subtopic FROM user_progress WHERE user_id=? AND lesson_name=?", (user_id, lesson_name))
    completed_subtopics = [row[0] for row in c.fetchall()]
    
    conn.commit()
    conn.close()
    
    return {'completed_subtopics': completed_subtopics}

# Call init_auth_db() at the start of the script
init_auth_db()