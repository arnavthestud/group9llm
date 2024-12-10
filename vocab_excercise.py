import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlite3
from authentication import is_logged_in, get_current_user_id
from gamification import update_user_stats, get_user_level



# Check login status
current_user_id = get_current_user_id()
if not is_logged_in():
    st.error("Please log in to access this page.")
    st.stop()
st.markdown("""
    <style>
    .main-title {
        font-size: 40px;
        font-weight: 700;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .sub-title {
        font-size: 28px;
        font-weight: 600;
        color: #333;
        margin-top: 30px;
        margin-bottom: 15px;
        border-bottom: 2px solid #1e88e5;
        padding-bottom: 10px;
    }
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
    .main-header {
        font-size: 48px;
        font-weight: bold;
        color: #4CAF50; /* Change this color as needed */
    }
    .sub-header {
        font-size: 36px;
        color: #333333; /* Change this color as needed */
    }
    .main-title {
        font-size: 40px;
        font-weight: 700;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }    
    .question-text {
        font-size: 20px;
        margin: 15px 0;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
   .score-container {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        margin-bottom: 30px;  /* Add margin at the bottom */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    /* ... (other score-related styles) ... */

    .button-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .score-title {
        font-size: 28px;
        font-weight: 600;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 20px;
    }
    .score-section {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .score-section-title {
        font-size: 22px;
        font-weight: 600;
        color: #333;
        margin-bottom: 10px;
        border-bottom: 2px solid #1e88e5;
        padding-bottom: 5px;
    }
    .score-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    .total-score {
        font-size: 24px;
        font-weight: 700;
        color: #1e88e5;
        text-align: center;
        margin-top: 20px;
    }
            
    </style>
""", unsafe_allow_html=True)

# ... (Keep the existing styles and other imports)

# Modify the database initialization function

def init_db():
    conn = sqlite3.connect('generated_items.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (item TEXT, type TEXT, user_id TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Modify the fetch_random_item function to include user_id
def fetch_random_item(item_type, user_id):
    conn = sqlite3.connect('generated_items.db')
    c = conn.cursor()
    c.execute("SELECT item FROM items WHERE type=? AND user_id=? ORDER BY RANDOM() LIMIT 1", (item_type, user_id))
    item = c.fetchone()
    conn.close()
    return item[0] if item else None

# Modify the reset_session_state function
def reset_session_state():
    keys_to_reset = [
        'current_word', 'current_idiom', 'word_meaning_evaluated', 'word_sentence_evaluated',
        'idiom_meaning_evaluated', 'idiom_sentence_evaluated', 'word_meaning_feedback',
        'word_sentence_feedback', 'idiom_meaning_feedback', 'idiom_sentence_feedback',
        'word_meaning_answer', 'word_sentence_answer', 'idiom_meaning_answer', 'idiom_sentence_answer',
        'word_meaning_score', 'word_sentence_score', 'idiom_meaning_score', 'idiom_sentence_score',
        'stats_updated'  # Add this new key
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            if key.endswith('_evaluated'):
                st.session_state[key] = False
            elif key.endswith('_score'):
                st.session_state[key] = None
            elif key == 'stats_updated':
                st.session_state[key] = False  # Reset the stats update flag
            else:
                st.session_state[key] = None

# Initialize session state
for key in ['current_word', 'current_idiom', 'word_meaning_evaluated', 'word_sentence_evaluated', 
            'idiom_meaning_evaluated', 'idiom_sentence_evaluated', 'word_meaning_feedback', 
            'word_sentence_feedback', 'idiom_meaning_feedback', 'idiom_sentence_feedback',
            'word_meaning_answer', 'word_sentence_answer', 'idiom_meaning_answer', 'idiom_sentence_answer',
            'stats_updated']:  # Add 'stats_updated' to the initialization
    if key not in st.session_state:
        if key.endswith('_evaluated'):
            st.session_state[key] = False
        elif key == 'stats_updated':
            st.session_state[key] = False  # Initialize the stats update flag
        else:
            st.session_state[key] = None
@st.cache_resource
def get_llm():
    return ChatGroq(
        model_name="llama3-8b-8192",
        api_key="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",
        temperature=0.7,
        request_timeout=10
    )

llm = get_llm()

# Define the evaluation prompt template
evaluation_prompt_template = PromptTemplate(
    input_variables=["item", "user_answer", "question_type"],
    template="""You are an English teacher. Evaluate the following user response for {question_type}. Your response should be similar to an English teacher:
    Task: {item}
    User's answer: {user_answer}

    Provide a comprehensive evaluation including:
    1. Accuracy: How correct is the answer?
    2. Clarity: How well-expressed is the answer?
    3. Completeness: Does the answer cover all necessary aspects?

    Format your response as follows:
    User's answer: [Repeat the user's answer]
    Evaluation:
     - Accuracy: [Comment on accuracy]
     - Clarity: [Comment on clarity]
     - Completeness: [Comment on completeness]
    
    Overall assessment: [Provide a brief, constructive overall assessment]
    Score: [X/10]
    
    Note:-
    Make sure you follow the format exactly as it is including the indentation and spaces.
    Make sure your evaluation isnt very strict."""
)

parser = StrOutputParser()
def extract_score(feedback_text):
    for line in feedback_text.split("\n"):
        if "Score:" in line:
            return line.split(":")[1].strip()
    return "N/A"

evaluation_chain = evaluation_prompt_template | llm | parser

# Title of the Streamlit app
st.markdown('<h1 class="main-title">Vocab Arena</h1>', unsafe_allow_html=True)

init_db()

# Fetch random word and idiom for practice
if st.session_state.current_word is None:
    st.session_state.current_word = fetch_random_item("word", current_user_id)
    st.session_state.word_meaning_evaluated = False
    st.session_state.word_sentence_evaluated = False
    st.session_state.word_meaning_feedback = None
    st.session_state.word_sentence_feedback = None

if st.session_state.current_idiom is None:
    st.session_state.current_idiom = fetch_random_item("idiom", current_user_id)
    st.session_state.idiom_meaning_evaluated = False
    st.session_state.idiom_sentence_evaluated = False
    st.session_state.idiom_meaning_feedback = None
    st.session_state.idiom_sentence_feedback = None

# ... (Keep the existing feedback parsing and display functions)
def parse_feedback(feedback_text):
    feedback_parts = {
        "User's Answer": "",
        "Accuracy": "",
        "Clarity": "",
        "Completeness": "",
        "Overall Assessment": "",
        "Score": ""
    }

    current_key = None
    for line in feedback_text.split("\n"):
        if "User's answer:" in line:
            current_key = "User's Answer"
            feedback_parts[current_key] = line.replace("User's answer:", "").strip()
        elif "Accuracy:" in line:
            current_key = "Accuracy"
            feedback_parts[current_key] = line.replace("Accuracy:", "").strip()
        elif "Clarity:" in line:
            current_key = "Clarity"
            feedback_parts[current_key] = line.replace("Clarity:", "").strip()
        elif "Completeness:" in line:
            current_key = "Completeness"
            feedback_parts[current_key] = line.replace("Completeness:", "").strip()
        elif "Overall assessment:" in line:
            current_key = "Overall Assessment"
            feedback_parts[current_key] = line.replace("Overall assessment:", "").strip()
        elif "Score:" in line:
            current_key = "Score"
            feedback_parts[current_key] = line.replace("Score:", "").strip()
        elif current_key:
            feedback_parts[current_key] += f" {line.strip()}"

    return feedback_parts

def display_feedback(feedback_text):
    if feedback_text:
        feedback_parts = parse_feedback(feedback_text)
        
        # Use Streamlit's expander to collapse feedback sections
        with st.expander("View Feedback", expanded=False):
            # Display each part of the feedback with appropriate formatting
            
            st.markdown(f":white_check_mark: **Accuracy:** {feedback_parts['Accuracy']}")
            st.markdown(f":bulb: **Clarity:** {feedback_parts['Clarity']}")
            st.markdown(f":memo: **Completeness:** {feedback_parts['Completeness']}")
            st.markdown(f"**Overall Assessment:** {feedback_parts['Overall Assessment']}")
            st.markdown(f"**Score:** {feedback_parts['Score']}")
# Word practice section
if st.session_state.current_word:
    # ... (Keep the existing word practice UI)
    # Main header
    st.markdown(f'<h2 class="sub-title">{"Word Practice"}</h2>', unsafe_allow_html=True)

    # Subheader
    st.markdown(f'<div class="question-text">{"What does the word " + st.session_state.current_word + " mean? Please provide its meaning and use it in a sentence."}</div>', unsafe_allow_html=True)
    word_col1, word_col2 = st.columns(2)

    with word_col1:
        
        user_word_meaning = st.text_input("Meaning:", key="word_meaning_input", 
                                          disabled=st.session_state.word_meaning_evaluated,
                                          value=st.session_state.word_meaning_answer or "")
        if st.button("Evaluate Word Meaning", disabled=st.session_state.word_meaning_evaluated):
            if user_word_meaning:
                with st.spinner("Evaluating your response..."):
                    evaluation_response = evaluation_chain.invoke({
                        "item": f"Provide the meaning of the word '{st.session_state.current_word}'",
                        "user_answer": user_word_meaning,
                        "question_type": "Word Definition"
                    })
                    st.session_state.word_meaning_feedback = evaluation_response
                    st.session_state.word_meaning_evaluated = True
                    st.session_state.word_meaning_answer = user_word_meaning
                    st.session_state.word_meaning_score = extract_score(evaluation_response)
                    st.rerun()
            else:
                st.warning("Please provide an answer to evaluate.")

    with word_col2:
        
        user_word_sentence = st.text_input("Sentence:", key="word_sentence_input", 
                                           disabled=st.session_state.word_sentence_evaluated,
                                           value=st.session_state.word_sentence_answer or "")
        if st.button("Evaluate Word Sentence", disabled=st.session_state.word_sentence_evaluated):
            if user_word_sentence:
                with st.spinner("Evaluating your response..."):
                    evaluation_response = evaluation_chain.invoke({
                        "item": f"Use the word '{st.session_state.current_word}' in a sentence",
                        "user_answer": user_word_sentence,
                        "question_type": "Sentence Usage"
                    })
                    st.session_state.word_sentence_feedback = evaluation_response
                    st.session_state.word_sentence_evaluated = True
                    st.session_state.word_sentence_answer = user_word_sentence
                    st.session_state.word_sentence_score = extract_score(evaluation_response)
                    st.rerun()
            else:
                st.warning("Please provide a sentence to evaluate.")
    
    with word_col1:
        if st.session_state.word_meaning_feedback:
            display_feedback(st.session_state.word_meaning_feedback)

    with word_col2:
        if st.session_state.word_sentence_feedback:
            display_feedback(st.session_state.word_sentence_feedback)

# Idiom practice section
if st.session_state.current_idiom:
    # ... (Keep the existing idiom practice UI)
    # Main header
    st.markdown(f'<h2 class="sub-title">{"Idiom Practice"}</h2>', unsafe_allow_html=True)

    # Subheader
    st.markdown(f'<div class="question-text">{"What does the idiom " + st.session_state.current_idiom + " mean? Please provide its meaning and use it in a sentence."}</div>', unsafe_allow_html=True)
    word_col1, word_col2 = st.columns(2)

    idiom_col1, idiom_col2 = st.columns(2)

    with idiom_col1:
        
        user_idiom_meaning = st.text_input("Meaning:", key="idiom_meaning_input", 
                                           disabled=st.session_state.idiom_meaning_evaluated,
                                           value=st.session_state.idiom_meaning_answer or "")
        if st.button("Evaluate Idiom Meaning", disabled=st.session_state.idiom_meaning_evaluated):
            if user_idiom_meaning:
                with st.spinner("Evaluating your response..."):
                    evaluation_response = evaluation_chain.invoke({
                        "item": f"Provide the meaning of the idiom '{st.session_state.current_idiom}'",
                        "user_answer": user_idiom_meaning,
                        "question_type": "Idiom Definition"
                    })
                    st.session_state.idiom_meaning_feedback = evaluation_response
                    st.session_state.idiom_meaning_evaluated = True
                    st.session_state.idiom_meaning_answer = user_idiom_meaning
                    st.session_state.idiom_meaning_score = extract_score(evaluation_response)
                    st.rerun()
            else:
                st.warning("Please provide an answer to evaluate.")

    with idiom_col2:
        
        user_idiom_sentence = st.text_input("Sentence:", key="idiom_sentence_input", 
                                            disabled=st.session_state.idiom_sentence_evaluated,
                                            value=st.session_state.idiom_sentence_answer or "")
        if st.button("Evaluate Idiom Sentence", disabled=st.session_state.idiom_sentence_evaluated):
            if user_idiom_sentence:
                with st.spinner("Evaluating your response..."):
                    evaluation_response = evaluation_chain.invoke({
                        "item": f"Use the idiom '{st.session_state.current_idiom}' in a sentence",
                        "user_answer": user_idiom_sentence,
                        "question_type": "Sentence Usage"
                    })
                    st.session_state.idiom_sentence_feedback = evaluation_response
                    st.session_state.idiom_sentence_evaluated = True
                    st.session_state.idiom_sentence_answer = user_idiom_sentence
                    st.session_state.idiom_sentence_score = extract_score(evaluation_response)
                    st.rerun()
            else:
                st.warning("Please provide a sentence to evaluate.")

    with idiom_col1:
        if st.session_state.idiom_meaning_feedback:
            display_feedback(st.session_state.idiom_meaning_feedback)

    with idiom_col2:
        if st.session_state.idiom_sentence_feedback:
            display_feedback(st.session_state.idiom_sentence_feedback)
# Get user's level
user_level = get_user_level(current_user_id)
# st.write(f"Your current level: {user_level}")
# ... (keep existing LLM and evaluation chain setup) ...

# Display scores after all questions have been answered
if (st.session_state.word_meaning_evaluated and st.session_state.word_sentence_evaluated and
    st.session_state.idiom_meaning_evaluated and st.session_state.idiom_sentence_evaluated):
    
    total_score = sum([float(score.split('/')[0]) for score in [
        st.session_state.word_meaning_score,
        st.session_state.word_sentence_score,
        st.session_state.idiom_meaning_score,
        st.session_state.idiom_sentence_score
    ] if score != 'N/A'])
    
    # Create HTML for score display
    score_html = f"""
    <div class="score-container">
        <div class="score-title">Your Scores</div>
        <div class="score-section">
            <div class="score-section-title">Word Practice</div>
            <div class="score-item">
                <span>Word Meaning:</span>
                <span>{st.session_state.word_meaning_score}</span>
            </div>
            <div class="score-item">
                <span>Word Sentence:</span>
                <span>{st.session_state.word_sentence_score}</span>
            </div>
        </div>
        <div class="score-section">
            <div class="score-section-title">Idiom Practice</div>
            <div class="score-item">
                <span>Idiom Meaning:</span>
                <span>{st.session_state.idiom_meaning_score}</span>
            </div>
            <div class="score-item">
                <span>Idiom Sentence:</span>
                <span>{st.session_state.idiom_sentence_score}</span>
            </div>
        </div>
        <div class="total-score">Total Score: {total_score}/40</div>
    </div>
    """
    
    # Display the score HTML
    st.markdown(score_html, unsafe_allow_html=True)

    # Update user stats only if they haven't been updated for this attempt
    if not st.session_state.stats_updated:
        new_level = update_user_stats(current_user_id, exercise_attempt=True, exercise_score=total_score)
        st.session_state.stats_updated = True  # Set the flag to indicate stats have been updated
        if new_level > user_level:
            st.success(f"Congratulations! You've reached level {new_level}!")

    # Add a container for the button
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    if st.button("Attempt again"):
        reset_session_state()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ... (keep the rest of the code) ...
def user_has_items(user_id):
    conn = sqlite3.connect('generated_items.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM items WHERE user_id=?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

# Check if the user has any items before starting the exercise
if not user_has_items(current_user_id):
    st.warning("You haven't learned any words or idioms yet. Please visit the Vocab Vault to generate some vocabulary first.")
    st.stop()