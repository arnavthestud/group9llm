import streamlit as st
import yaml
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from authentication import is_logged_in, get_current_user_id, get_proficiency, update_user_progress
from gamification import update_user_stats, get_user_level
from langgraph.graph import END, StateGraph
from typing import TypedDict
from PIL import Image
import io

# Load configuration from YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load all configurations
def load_all_configs():
    return {
        "Simple Present": load_config('present_simple.yaml'),
        "Present Continuous": load_config('present_continuous.yaml'),
        "Present Perfect": load_config('present_perfect.yaml'),
        "Present Perfect Continuous": load_config('present_perfect_continuous.yaml')
    }

# Define the State
class State(TypedDict):
    user_question: str
    context: str
    transformed_question: str
    relevance: str
    abstracted_principles: str
    final_answer: str

# Template definitions
transform_question_template = PromptTemplate(
    input_variables=["question", "context"],
    template="""
    Original: {question}
    Context: {context}
    Improve the question in 20 words or less. Fix grammar, clarify, and align with the topic. Do not change the meaning of the question.:
    Improved:
    """
)

def transform_question(state):
    question = state['user_question']
    context = state['context']
    transformed = model.predict(transform_question_template.format(question=question, context=context))
    return {"transformed_question": transformed}

relevance_check_template = PromptTemplate(
    input_variables=["context", "user_question"],
    template="""
    Context: {context}
    Question: {user_question}
    Is this relevant to the context or is it a question pertaining to english language? Answer 'Yes' or 'No' and explain in 10 words or less:
    """
)
def check_relevance(state):
    context = state['context']
    user_question = state['user_question']
    relevance = model.predict(relevance_check_template.format(context=context, user_question=user_question))
    return {"relevance": relevance}

# abstract_principles_template = PromptTemplate(
#     input_variables=["transformed_question", "context"],
#     template="""
#     Question: {transformed_question}
#     Context: {context}
#     List 2-3 key language principles relevant to this question. Max 30 words total:
#     1.
#     2.
#     3.
#     """
# )
abstract_principles_template = PromptTemplate(
    input_variables=["transformed_question", "context"],
    template="""
    Given the transformed question: {transformed_question}, and the context: {context},

    Your tasks are:

    - Identify the underlying principles, laws, or key details relevant to this question, extracting them from the context if present, or using your own knowledge if not.
    - Abstract the question to determine the main concept that needs to be addressed.

    Then, provide a list of 2-3 key language principles relevant to this question, using no more than 30 words in total. Only output the list; do not include any explanations or additional text:

    1.
    2.
    3.
    """
)

def abstract_principles(state):
    transformed_question = state['transformed_question']
    context = state['context']
    principles = model.predict(abstract_principles_template.format(transformed_question=transformed_question, context=context))
    return {"abstracted_principles": principles}

# final_reasoning_template = PromptTemplate(
#     input_variables=["abstracted_principles", "transformed_question"],
#     template="""
#     Question: {transformed_question}
#     Principles: {abstracted_principles}
#     Answer the question concisely. Include a brief example. Max 50 words:
#     """
# )
final_reasoning_template = PromptTemplate(
    input_variables=["abstracted_principles", "transformed_question"],
    template="""
    Now using the following principles: {abstracted_principles}, apply them to reason out the answer for the question: {transformed_question}.
    
    Answer the question concisely. Max 50 words:
    """
        )
def final_reasoning(state):
    abstracted_principles = state['abstracted_principles']
    transformed_question = state['transformed_question']
    answer = model.predict(final_reasoning_template.format(abstracted_principles=abstracted_principles,
                                                           transformed_question=transformed_question))
    return {"final_answer": answer}

# Tool functions
def transform_question(state):
    question = state['user_question']
    context = state['context']
    transformed = model.predict(transform_question_template.format(question=question, context=context))
    return {"transformed_question": transformed}

def check_relevance(state):
    context = state['context']
    user_question = state['user_question']
    relevance = model.predict(relevance_check_template.format(context=context, user_question=user_question))
    return {"relevance": relevance}

def abstract_principles(state):
    transformed_question = state['transformed_question']
    context = state['context']
    principles = model.predict(abstract_principles_template.format(transformed_question=transformed_question, context=context))
    return {"abstracted_principles": principles}

def final_reasoning(state):
    abstracted_principles = state['abstracted_principles']
    transformed_question = state['transformed_question']
    answer = model.predict(final_reasoning_template.format(abstracted_principles=abstracted_principles, transformed_question=transformed_question))
    return {"final_answer": answer}

# Build the graph
def build_graph():
    workflow = StateGraph(State)
    workflow.add_node("transform", transform_question)
    workflow.add_node("check_relevance", check_relevance)
    workflow.add_node("abstract", abstract_principles)
    workflow.add_node("reason", final_reasoning)
    workflow.add_edge("transform", "check_relevance")
    workflow.set_entry_point("transform")
    workflow.add_conditional_edges(
        "check_relevance",
        lambda x: "Yes" in x["relevance"],
        {True: "abstract", False: END}
    )
    workflow.add_edge("abstract", "reason")
    workflow.add_edge("reason", END)
    return workflow.compile()

# Streamlit UI
st.title("Present Tense Lessons")

# Check login status
if not is_logged_in():
    st.error("Please log in to access this page.")
    st.stop()

current_user_id = get_current_user_id()
user_proficiency = get_proficiency(current_user_id)
user_level = get_user_level(current_user_id)

# User selects the lesson
selected_lesson = st.selectbox("Choose a lesson:", 
                               ["Simple Present", "Present Continuous", "Present Perfect", "Present Perfect Continuous"])

# Load all configs
all_configs = load_all_configs()

# Use the selected config
config = all_configs[selected_lesson]

# Apply custom CSS
st.markdown(config['custom_css'], unsafe_allow_html=True)

# Initialize ChatGroq
model = ChatGroq(
    model_name=config['model']['name'],
    api_key=config['model']['api_key'],
    temperature=config['model']['temperature'],
    request_timeout=config['model']['request_timeout']
)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings()

# Create a text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=config['text_splitter']['chunk_size'],
    chunk_overlap=config['text_splitter']['chunk_overlap']
)

# Load and process the document
with open(config['document']['file_path'], "r") as file:
    raw_text = file.read()

texts = text_splitter.split_text(raw_text)

# Create a vector store
vectorstore = FAISS.from_texts(texts, embeddings)

# Create a retriever
retriever = vectorstore.as_retriever()

# Create the conversational chain for RAG
qa_chain = RetrievalQA.from_chain_type(
    llm=model,
    retriever=retriever
)

# Create the graph
graph = build_graph()

# Initialize session state
if 'current_topic' not in st.session_state:
    st.session_state.current_topic = None
if 'current_subtopic' not in st.session_state:
    st.session_state.current_subtopic = None
if 'completed_subtopics' not in st.session_state:
    st.session_state.completed_subtopics = set()
if 'rag_content' not in st.session_state:
    st.session_state.rag_content = {}
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""

# Load user progress
user_progress = update_user_progress(current_user_id, lesson_name=config['app']['subject'])
st.session_state.completed_subtopics = set(user_progress.get('completed_subtopics', []))

st.subheader("Progress")
total_subtopics = sum(len(subtopics) for subtopics in config['subtopics'].values())
completed_subtopics = len(st.session_state.completed_subtopics)
progress_percentage = completed_subtopics / total_subtopics

st.progress(progress_percentage)
st.write(f"Completed {completed_subtopics} out of {total_subtopics} subtopics")

# Display progress on main screen
progress_cols = st.columns(len(config['topics']))
for i, topic in enumerate(config['topics']):
    with progress_cols[i]:
        all_subtopics_completed = all(subtopic in st.session_state.completed_subtopics 
                                      for subtopic in config['subtopics'][topic])
        
        if all_subtopics_completed:
            st.write(f"**✅ {topic}**")
        else:
            st.write(f"**❌ {topic}**")
        
        for subtopic in config['subtopics'][topic]:
            if subtopic in st.session_state.completed_subtopics:
                st.write(f"- ✅ {subtopic}")
            else:
                st.write(f"- ❌ {subtopic}")

st.markdown("---")

# Display main topic selectbox
st.subheader("Choose a topic:")
selected_topic = st.selectbox("Select a topic", [""] + config['topics'], key="topic_selectbox")

st.session_state.current_topic = selected_topic
st.session_state.current_subtopic = None

# Display subtopic selectbox if a main topic is selected
if st.session_state.current_topic:
    st.subheader(f"{st.session_state.current_topic} - Subtopics:")
    selected_subtopic = st.selectbox("Select a subtopic", [""] + config['subtopics'][st.session_state.current_topic], key="subtopic_selectbox")
    
    if selected_subtopic:
        st.session_state.current_subtopic = selected_subtopic

# Display content for the selected subtopic
if st.session_state.current_subtopic:
    st.subheader(st.session_state.current_subtopic)
    
    # Retrieve content for the current subtopic if not already in session state
    if st.session_state.current_subtopic not in st.session_state.rag_content:
        query = f"Provide information about {st.session_state.current_subtopic} in {config['app']['subject']}"
        result = qa_chain.run(query)
        print("subtopic: "+query)
        print("retrieved content : ")
        print(result)
        st.session_state.rag_content[st.session_state.current_subtopic] = result
    
    # Display the RAG-retrieved content
    st.markdown(f'<div class="content-text">{st.session_state.rag_content[st.session_state.current_subtopic]}</div>', unsafe_allow_html=True)
    
    # Mark subtopic as completed
    if st.session_state.current_subtopic not in st.session_state.completed_subtopics:
        st.session_state.completed_subtopics.add(st.session_state.current_subtopic)
        update_user_progress(current_user_id, lesson_name=config['app']['subject'], completed_subtopic=st.session_state.current_subtopic)
        
        # Check if all subtopics for the current topic are completed
        if all(subtopic in st.session_state.completed_subtopics for subtopic in config['subtopics'][st.session_state.current_topic]):
            st.success(f"Congratulations! You've completed all subtopics for {st.session_state.current_topic}!")
            
        # Check if all topics are completed
        if all(subtopic in st.session_state.completed_subtopics for topic in config['topics'] for subtopic in config['subtopics'][topic]):
            st.success(f"Congratulations! You've completed the entire {config['app']['subject']} lesson!")
            new_level = update_user_stats(current_user_id, lesson_completed=True)
            if new_level > user_level:
                st.success(f"You've reached level {new_level}!")

# User query section
st.subheader("Ask a question:")

def handle_question_submit():
    st.session_state.question_submitted = True

user_question = st.text_input("Enter your question here:", key="user_question", on_change=handle_question_submit)

if 'question_submitted' not in st.session_state:
    st.session_state.question_submitted = False

if st.session_state.question_submitted and user_question:
    # Create the context based on the current subtopic and RAG content
    context = f"The user is learning about {config['app']['subject']}, specifically about {st.session_state.current_subtopic}. Here's the relevant information:\n\n{st.session_state.rag_content.get(st.session_state.current_subtopic, '')}"
    
    # Initialize the graph input
    inputs = State(
        user_question=user_question,
        context=context,
        transformed_question="",
        relevance="",
        abstracted_principles="",
        final_answer=""
    )
    
    # Use the LangGraph to process the question
    for output in graph.stream(inputs):
        for key, value in output.items():
            if key == "transform":
                st.markdown(f'<div class="content-text">Transformed Question:\n {value["transformed_question"]}</div>', unsafe_allow_html=True)
            elif key == "check_relevance":
                if "No" in value["relevance"]:
                    st.markdown(f'<div class="content-text">I\'m sorry, but I cannot answer your question as it appears to be unrelated to the current topic. Please ask a question related to {st.session_state.current_subtopic} in {config["app"]["subject"]}.</div>', unsafe_allow_html=True)
                    break
            elif key == "abstract":
                st.markdown(f'<div class="content-text">Abstracted Principles:\n {value["abstracted_principles"]}</div>', unsafe_allow_html=True)
            elif key == "reason":
                st.markdown(f'<div class="content-text">Response:\n {value["final_answer"]}</div>', unsafe_allow_html=True)

    st.session_state.question_submitted = False

st.markdown('</div>', unsafe_allow_html=True)

# Display LangGraph visualization
#st.subheader("LangGraph Visualization")
# mermaid_png = graph.get_graph(xray=True).draw_mermaid_png()
# image = Image.open(io.BytesIO(mermaid_png))
# st.image(image, caption="LangGraph Visualization", use_column_width=True)

st.markdown('</div>', unsafe_allow_html=True)