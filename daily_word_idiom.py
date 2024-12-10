import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlite3
import random
import pandas as pd
from authentication import is_logged_in, get_current_user_id, get_proficiency
from gamification import update_user_stats, get_user_level

# ... (keep existing imports and functions) ...
# ... [previous imports and functions remain unchanged] ...
current_user_id = get_current_user_id()
def save_to_session(word_data, idiom_data):
    st.session_state['last_word'] = word_data
    st.session_state['last_idiom'] = idiom_data

def load_from_session():
    return st.session_state.get('last_word'), st.session_state.get('last_idiom')

# ... [rest of your code remains unchanged] ...
def init_db():
    conn = sqlite3.connect('generated_items.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (item TEXT, type TEXT, user_id TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
# Function to manage items in the database
def manage_db_items(user_id, item=None, item_type=None, max_items=1000):
    conn = sqlite3.connect('generated_items.db')
    c = conn.cursor()
    
    if item and item_type:
        c.execute("INSERT INTO items (item, type, user_id) VALUES (?, ?, ?)", (item, item_type, user_id))
        conn.commit()
    
    c.execute(f"SELECT item FROM items WHERE type=? AND user_id=? ORDER BY timestamp DESC LIMIT {max_items}", (item_type, user_id))
    items = [row[0] for row in c.fetchall()]
    
    conn.close()
    return items

# Function to get a subset of items
def get_item_subset(items, max_subset=50):
    return random.sample(items, min(len(items), max_subset))
# Initialize the LLM
llm = ChatGroq(
    model_name="llama3-8b-8192",
    api_key="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",
    temperature=0.8,
    request_timeout=10
)

# Define the prompt templates
prompt_template_word = PromptTemplate(
    input_variables=["difficulty", "existing_words"],
    template="""Generate a random {difficulty} word along with its meaning and usage in a sentence. 
    The word should not be any of the following: {existing_words}
    Format your response as follows:
    Word: [word]
    Meaning: [meaning]
    Usage: [sentence using the word]
    Do not include any additional text or explanations."""
)

prompt_template_idiom = PromptTemplate(
    input_variables=["difficulty", "existing_idioms"],
    template="""Generate a random {difficulty} idiom/metaphor/figure of speech along with its meaning and usage in a sentence. 
    The idiom should not be any of the following: {existing_idioms}
    Format your response as follows:
    Idiom: [idiom]
    Meaning: [meaning]
    Usage: [sentence using the idiom]
    Do not include any additional text or explanations."""
)

parser = StrOutputParser()

# Create the chains
question_chain_word = prompt_template_word | llm | parser
question_chain_idiom = prompt_template_idiom | llm | parser

# ... [other functions remain unchanged] ...
# Function to parse the LLM response
def parse_llm_response(response):
    parsed_response = {}
    lines = response.splitlines()
    
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            parsed_response[key.strip()] = value.strip()
    
    return parsed_response

# ... [CSS styles remain unchanged] ...
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
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    h3 {
        color: #34495e;
        margin-top: 2rem;
    }
    .stSelectbox {
        margin-bottom: 2rem;
    }
    .output-box {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)
init_db()

def view_database(user_id):
    conn = sqlite3.connect('generated_items.db')
    words_df = pd.read_sql_query("SELECT item, timestamp FROM items WHERE type='word' AND user_id=? ORDER BY timestamp DESC", conn, params=(user_id,))
    idioms_df = pd.read_sql_query("SELECT item, timestamp FROM items WHERE type='idiom' AND user_id=? ORDER BY timestamp DESC", conn, params=(user_id,))
    conn.close()
    return words_df, idioms_df
# Streamlit UI
st.markdown('<h1 class="main-title">Vocab Vault</h1>', unsafe_allow_html=True)

# Check login status
current_user_id = get_current_user_id()
if not is_logged_in():
    st.error("Please log in to access this page.")
    st.stop()

# Get user's proficiency and level
user_proficiency = get_proficiency(current_user_id)
user_level = get_user_level(current_user_id)

if user_proficiency is None:
    st.warning("Your proficiency level is not set. Please update your profile.")
    user_proficiency = "medium"  # Default to medium if not set

# st.write(f"Your current proficiency level: {user_proficiency}")
# st.write(f"Your current level: {user_level}")

if st.button("Generate"):
    with st.spinner("Generating..."):
        existing_words = manage_db_items(current_user_id, item_type="word")
        existing_idioms = manage_db_items(current_user_id, item_type="idiom")
        
        # Get subsets for the prompts
        word_subset = get_item_subset(existing_words)
        idiom_subset = get_item_subset(existing_idioms)

        # Generate word and idiom using user's proficiency
        word_response = question_chain_word.invoke({
            "difficulty": user_proficiency, 
            "existing_words": ", ".join(word_subset)
        })
        idiom_response = question_chain_idiom.invoke({
            "difficulty": user_proficiency, 
            "existing_idioms": ", ".join(idiom_subset)
        })
        print(word_response)
        print(idiom_response)
        # Parse the responses
        word_data = parse_llm_response(word_response)
        idiom_data = parse_llm_response(idiom_response)

        # Update the database
        manage_db_items(current_user_id, word_data.get('Word', ''), "word")
        manage_db_items(current_user_id, idiom_data.get('Idiom', ''), "idiom")
        
        # Save to session state
        save_to_session(word_data, idiom_data)

        # Update user stats
        new_level = update_user_stats(current_user_id, vocab_attempt=True)
        if new_level > user_level:
            st.success(f"Congratulations! You've reached level {new_level}!")

# ... (keep the rest of the code for displaying words, idioms, and learned items) ...
word_data, idiom_data = load_from_session()

# Display the word and idiom
if word_data:
    st.subheader("Word of the day")
    st.markdown(f"""
    <div class="output-box">
        <p><strong>Word:</strong> {word_data.get('Word', '')}</p>
        <p><strong>Meaning:</strong> {word_data.get('Meaning', '')}</p>
        <p><strong>Usage:</strong> {word_data.get('Usage', '')}</p>
    </div>
    """, unsafe_allow_html=True)

if idiom_data:
    st.subheader("Idiom of the day")
    st.markdown(f"""
    <div class="output-box">
        <p><strong>Idiom:</strong> {idiom_data.get('Idiom', '')}</p>
        <p><strong>Meaning:</strong> {idiom_data.get('Meaning', '')}</p>
        <p><strong>Usage:</strong> {idiom_data.get('Usage', '')}</p>
    </div>
    """, unsafe_allow_html=True)
# if st.button("Show Learned Words and Idioms"):
#     words_df, idioms_df = view_database(current_user_id)
    
#     st.markdown("""
#     <style>
#     .word-idiom-table {
#         font-size: 16px;
#         color: #333;
#         background-color: #f8f9fa;
#         border-radius: 5px;
#         padding: 10px;
#         margin-bottom: 20px;
#     }
#     .word-idiom-table th {
#         background-color: #4CAF50;
#         color: white;
#         padding: 12px;
#         text-align: left;
#     }
#     .word-idiom-table td {
#         padding: 12px;
#         border-bottom: 1px solid #ddd;
#     }
#     .word-idiom-table tr:hover {
#         background-color: #e9ecef;
#     }
#     </style>
#     """, unsafe_allow_html=True)

#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Learned Words")
#         st.markdown(words_df.to_html(index=False, classes='word-idiom-table'), unsafe_allow_html=True)

#     with col2:
#         st.subheader("Learned Idioms")
#         st.markdown(idioms_df.to_html(index=False, classes='word-idiom-table'), unsafe_allow_html=True)