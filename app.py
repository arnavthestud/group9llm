import streamlit as st
from authentication import init_auth_db, login, register, is_logged_in, logout, get_current_user_id
from gamification import init_gamification_db, get_user_level, get_user_stats

# Initialize the authentication and gamification databases
init_auth_db()
init_gamification_db()

custom_css = """
<style>
    /* General styles */
    body {
        font-family: 'Arial', sans-serif;
    }
    .main-title {
        font-size: 40px;
        font-weight: 700;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab"] {
        background-color: #1e88e5;
        color: white;
        border: 1px solid #1e88e5;
        border-radius: 5px;
        padding: 10px;
        margin-right: 5px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #0056b3;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #0056b3;
        color: white;
    }

    /* Sidebar styling */
    .css-18e3th9 {
        background-color: #f0f8ff;
    }
    .css-1aumxhk {
        color: #333;
    }
    .css-1aumxhk:hover {
        color: #4CAF50;
    }

    /* Button styling */
    .stButton>button {
        background-color: #1e88e5;
        color: white;
        font-size: 18px;
        font-weight: 500;
        padding: 10px 25px;
        border-radius: 25px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    .stButton>button:hover {
        background-color: #1565c0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    /* Page container styling */
    .main-container {
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar user stats styling */
    .user-stats {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .user-level {
        font-size: 24px;
        font-weight: bold;
        color: #1e88e5;
        margin-bottom: 10px;
    }
    .stat-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .stat-label {
        font-weight: 500;
        color: #555;
    }
    .stat-value {
        font-weight: bold;
        color: #333;
    }
    .level-bar-container {
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 15px;
        margin-top: 10px;
        margin-bottom: 15px;
        overflow: hidden;
    }
    .level-bar {
        height: 30px;
        background-color: #1e88e5;
        text-align: center;
        line-height: 20px;
        color: white;
        transition: width 0.5s ease-in-out;
    }
</style>
"""

# Apply the custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

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

def calculate_level_progress(points):
    level = calculate_level(points)
    if level == 1:
        progress = points / 100
    elif level == 2:
        progress = (points - 100) / 150
    elif level == 3:
        progress = (points - 250) / 150
    elif level == 4:
        progress = (points - 400) / 200
    elif level == 5:
        progress = (points - 600) / 250
    elif level == 6:
        progress = (points - 850) / 300
    elif level == 7:
        progress = (points - 1150) / 350
    elif level == 8:
        progress = (points - 1500) / 400
    elif level == 9:
        progress = (points - 1900) / 450
    else:
        progress = 1  # Max level reached
    return level, min(progress, 1) 

# Apply the custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Check if the user is logged in, if not, show login/register page
if not is_logged_in():
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        login()
    with tab2:
        register()
else:
    # Get current user ID and level
    current_user_id = get_current_user_id()
    user_level = get_user_level(current_user_id)
    user_stats = get_user_stats(current_user_id)

    # Display user stats in the sidebar
    with st.sidebar:
        if user_stats is not None:
            points = user_stats.get('points', 0)
            level, progress = calculate_level_progress(points)
            
            st.markdown(f"<div class='user-level'>Level {level}</div>", unsafe_allow_html=True)
            
            # Add the level progress bar
            progress_percentage = int(progress * 100)
            st.markdown(f"""
            <div class='level-bar-container'>
                <div class='level-bar' style='width: {progress_percentage}%;'>
                </div>
            </div>
        """, unsafe_allow_html=True)
            for stat, value in user_stats.items():
                st.markdown(f"<div class='stat-item'><span class='stat-label'>{stat.replace('_', ' ').title()}:</span> <span class='stat-value'>{value}</span></div>", unsafe_allow_html=True)
        else:
            st.write("User stats not available")
        st.markdown("</div>", unsafe_allow_html=True)

    # Your existing app code here
    proficiency_test = st.Page(
        page="proficiency_test.py",
        title="Diagnostic_test", 
    )
    vocab_ex = st.Page(
        page="daily_word_idiom.py",
        title="Daily Vocabulary Training",
    )
    vocab_test = st.Page(
        page="vocab_excercise.py",
        title="Vocabulary Exercise",
    )
    
    # tense_ex = st.Page(
    #     page="present_simple.py",
    #     title="SIMPLE PRESENT TENSE",
    # )
    tense_ex2 = st.Page(
        page="present_tense.py",
        title="PRESENT TENSE",
    )
    # tense_ex3 = st.Page(
    #     page="present_perfect.py",
    #     title="PERFECT PRESENT TENSE",
    # )
    # tense_ex4 = st.Page(
    #     page="present_perfect_continuous.py",
    #     title="PERFECT CONTINUOUS PRESENT TENSE",
    # )
    pg = st.navigation({
        "PROFICIENCY TEST": [proficiency_test],
        "VOCABULARY": [vocab_ex, vocab_test],
        "TENSES":[tense_ex2]
        # "TENSES": [tense_ex,tense_ex2,tense_ex3,tense_ex4]
    })

    

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        logout()

    pg.run()