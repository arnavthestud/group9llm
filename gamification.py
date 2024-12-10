import sqlite3
from datetime import datetime

def init_gamification_db():
    conn = sqlite3.connect('gamification.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                 (user_id TEXT PRIMARY KEY, 
                 vocab_generator_attempts INTEGER DEFAULT 0,
                 exercise_attempts INTEGER DEFAULT 0,
                 total_score INTEGER DEFAULT 0,
                 points INTEGER DEFAULT 0,
                 level INTEGER DEFAULT 1,
                 last_login DATE)''')
    conn.commit()
    conn.close()

def update_user_stats(user_id, vocab_attempt=False, exercise_attempt=False, exercise_score=0, lesson_completed=False):
    conn = sqlite3.connect('gamification.db')
    c = conn.cursor()
    
    # Get current stats
    c.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    stats = c.fetchone()
    
    if stats is None:
        # Initialize user stats if not exist
        c.execute("INSERT INTO user_stats (user_id) VALUES (?)", (user_id,))
        stats = (user_id, 0, 0, 0, 0, 1, None)
    
    vocab_attempts, exercise_attempts, total_score, points, level, last_login = stats[1:]
    
    # Update stats
    if vocab_attempt:
        vocab_attempts += 1
        points += 1
    if exercise_attempt:
        exercise_attempts += 1
        total_score += exercise_score
        points += 1
        if 30 <= exercise_score <= 40:  # Assuming 40 is a perfect score
            points += 10
        elif 25 <= exercise_score < 30:
            points += 5
        elif 15 <= exercise_score < 20:
            if points > 0:
                points -= 1
        elif exercise_score < 15:
            if points > 2:
                points -= 3
    if lesson_completed:
        points += 5  # Reward 5 points for completing a lesson
    
    # Check for daily login bonus
    if last_login is not None:
        last_login = datetime.strptime(last_login, '%Y-%m-%d').date()
    today = datetime.now().date()
    if last_login is None or last_login < today:
        points += 5
    
    # Update level based on points
    level = calculate_level(points)
    
    # Update database
    c.execute("""UPDATE user_stats 
                 SET vocab_generator_attempts = ?, 
                     exercise_attempts = ?, 
                     total_score = ?,
                     points = ?,
                     level = ?,
                     last_login = ?
                 WHERE user_id = ?""", 
              (vocab_attempts, exercise_attempts, total_score, points, level, today, user_id))
    
    conn.commit()
    conn.close()
    
    return level

def calculate_level(points):
    if points <= 100:
        return 1
    elif points <= 250:
        return 2
    elif points <= 400:
        return 3
    elif points <= 600:
        return 4
    elif points <= 850:
        return 5
    elif points <= 1150:
        return 6
    elif points <= 1500:
        return 7
    elif points <= 1900:
        return 8
    elif points <= 2350:
        return 9
    else:
        return 10

def get_user_level(user_id):
    conn = sqlite3.connect('gamification.db')
    c = conn.cursor()
    c.execute("SELECT level FROM user_stats WHERE user_id = ?", (user_id,))
    level = c.fetchone()
    conn.close()
    return level[0] if level else 1

def get_user_stats(user_id):
    conn = sqlite3.connect('gamification.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_stats WHERE user_id = ?", (user_id,))
    stats = c.fetchone()
    conn.close()
    if stats:
        return {
            "vocab_generator_attempts": stats[1],
            "exercise_attempts": stats[2],
            "total_score": stats[3],
            "points": stats[4],
            "level": stats[5]
        }
    return None