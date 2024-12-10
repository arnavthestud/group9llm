import streamlit as st
from langchain.prompts import PromptTemplate
import random
from langchain_groq.chat_models import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
import altair as alt
from langchain import LLMChain
from authentication import update_proficiency, get_proficiency

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f0f2f6;
        color: #333;
    }

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

    .question-text {
        font-size: 20px;
        margin: 15px 0;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .context-box {
        background-color: #e3f2fd;
        border-left: 5px solid #1e88e5;
        padding: 10px;
        margin-bottom: 15px;
        border-radius: 0 8px 8px 0;
    }

    .stRadio > div {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }

    .stRadio > div:hover {
        background-color: #e3f2fd;
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

    .stAlert {
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        font-weight: 500;
    }
    
    .stAlert-success {
        background-color: #c8e6c9;
        color: #1b5e20;
    }

    .stAlert-error {
        background-color: #ffcdd2;
        color: #b71c1c;
    }

    .stAlert-info {
        background-color: #bbdefb;
        color: #0d47a1;
    }

    .results-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-top: 30px;
    }

    .chart-title {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        margin-bottom: 15px;
        text-align: center;
    }
    .custom-success {
    background-color: #d4edda;
    border-left: 5px solid #28a745;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 0 8px 8px 0;
    color: #155724;
}

.custom-error {
    background-color: #f8d7da;
    border-left: 5px solid #dc3545;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 0 8px 8px 0;
    color: #721c24;
}

.custom-info {
    background-color: #cce5ff;
    border-left: 5px solid #0dcaf0;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 0 8px 8px 0;
    color: #004085;
}

    </style>
    """, 
    unsafe_allow_html=True
)

llm = ChatGroq(model_name="llama3-8b-8192", api_key="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", temperature=0.7)

# Updated prompt template for MCQ only
question_prompt = PromptTemplate(
    input_variables=["topic", "subtopic", "difficulty"],
    template="""Generate a multiple-choice question on {topic} (subtopic: {subtopic}) for {difficulty} English language learners. 

    Provide the following:
    1. Question
    2. Correct Answer
    3. Brief Explanation for the correct answer only
    4. Three incorrect options without any explanations

    Format the response as follows:
    Question: [Your multiple-choice question here]
    Correct Answer: [The correct answer]
    Explanation: [Brief explanation for the correct answer only]
    Incorrect Options:
    - [Incorrect option 1]
    - [Incorrect option 2]
    - [Incorrect option 3]

    Note:- 
    1)Do not provide explanations for the incorrect options.
    2)Ensure all content is clear, educational, and appropriate for all ages. Avoid repeating questions.
    3)Please follow the Format provided. Make sure the spacing and indentation is the same in the format.
    4)Please Make sure that the answer is not provided anywhere in the question itself."""
)


parser = StrOutputParser()
question_chain = question_prompt | llm | parser
def determine_cefr_level(percentage):
    if percentage >= 95:
        return "C2 - Proficiency"
    elif percentage >= 80:
        return "C1 - Advanced"
    elif percentage >= 65:
        return "B2 - Upper Intermediate"
    elif percentage >= 50:
        return "B1 - Intermediate"
    elif percentage >= 35:
        return "A2 - Elementary"
    else:
        return "A1 - Beginner"
def parse_response(response):
    print(response)
    result = {
        # 'context': '',
        'question': '',
        'correct_answer': '',
        'explanation': '',
        'incorrect_options': []
    }
    
    current_key = None
    for line in response.split('\n'):
        line = line.strip()
        # if line.startswith('Context:'):
        #     result['context'] = line.split('Context:', 1)[1].strip()
        if line.startswith('Question:'):
            result['question'] = line.split('Question:', 1)[1].strip()
        elif line.startswith('Correct Answer:'):
            result['correct_answer'] = line.split('Correct Answer:', 1)[1].strip()
        elif line.startswith('Explanation:'):
            result['explanation'] = line.split('Explanation:', 1)[1].strip()
        elif line.startswith('Incorrect Options:'):
            current_key = 'incorrect_options'
        elif line.startswith('-') and current_key == 'incorrect_options':
            result['incorrect_options'].append(line.lstrip('- ').strip())

    # Check for minimum required fields
    if result['question'] and result['correct_answer']:
        return result
    else:
        missing = []
        if not result['question']:
            missing.append('question')
        if not result['correct_answer']:
            missing.append('correct answer')
        raise ValueError(f"Missing critical fields: {', '.join(missing)}")




question_prompt_reading = PromptTemplate(
    input_variables=["difficulty"],
    template="""Generate a passage with a difficulty level of {difficulty} for English language learners.

    Provide the following:
    1. A scenario or passage
    2. A comprehension question based on the passage/scenario that requires critical thinking
    3. The correct answer to the question
    4. A brief explanation for the correct answer only

    Format the response as follows:
    Context: [Short scenario or passage, if applicable]
    Question: [A comprehension question that requires the user to think critically and is not straightforward]
    Correct Answer: [Correct Answer to the question]
    Explanation: [Brief explanation for the correct answer only]

    Ensure all content is clear, educational, and appropriate for all ages. Avoid repeating questions. The question should be designed in such a way that it prompts the user to analyze or infer information from the passage rather than providing a direct answer.
    """
)


# Define the rubric
rubric = """
Rubric for Scoring Reading Comprehension Answers:frubric

1. Content Accuracy (0-5 points):
   0 - Completely incorrect or irrelevant
   1 - Mostly incorrect with minor relevant points
   2 - Partially correct, missing several key points
   3 - Mostly correct with some key points missing
   4 - Mostly correct with minor inaccuracies
   5 - Fully correct and comprehensive

2. Comprehension (0-5 points):
   0 - No understanding demonstrated
   1 - Minimal understanding of the passage
   2 - Limited understanding with major gaps
   3 - Good understanding with some gaps
   4 - Very good understanding with minor gaps
   5 - Excellent, thorough understanding of the passage

3. Clarity of Expression (0-5 points):
   0 - Incomprehensible or extremely unclear
   1 - Mostly unclear with significant issues
   2 - Somewhat clear but with notable issues
   3 - Mostly clear with minor issues
   4 - Clear and well-expressed with very minor issues
   5 - Exceptionally clear and well-articulated

4. Language Mechanics (0-5 points):
   0 - Numerous major errors in punctuation, grammar, and spelling
   1 - Many significant errors in punctuation, grammar, and spelling
   2 - Several noticeable errors in punctuation, grammar, and spelling
   3 - Some minor errors in punctuation, grammar, and spelling
   4 - Very few minor errors in punctuation, grammar, and spelling
   5 - Flawless or near-flawless punctuation, grammar, and spelling

Total possible score: 20 points
"""

# Updated comparison prompt
comparison_prompt = PromptTemplate(
    input_variables=["user_answer", "correct_answer", "context", "rubric","question"],
    template="""Evaluate the user's answer based on the provided rubric, context, and correct answer. 
    Provide a score for each criterion, a total score, and detailed feedback.

    Context: {context}
    Question: {question}
    User's answer: {user_answer}
    Correct answer: {correct_answer}

    Rubric:
    {rubric}

    Provide the scores and feedback in the following format:
    Content Accuracy: [score]/5
    Feedback: [Specific feedback on content accuracy]

    Comprehension: [score]/5
    Feedback: [Specific feedback on comprehension]

    Clarity of Expression: [score]/5
    Feedback: [Specific feedback on clarity]

    Language Mechanics: [score]/5
    Feedback: [Specific feedback on punctuation, grammar, and spelling]

    Total Score: [total]/20

    Overall Feedback:
    [Provide a summary of strengths and areas for improvement]

    Remember to consider partial credit."""
)
st.markdown('<h1 class="main-title">English Language Learning Exercise</h1>', unsafe_allow_html=True)

# Initialize session state variables
if "questions" not in st.session_state:
    st.session_state["questions"] = {}
if "shuffled_options" not in st.session_state:
    st.session_state["shuffled_options"] = {}
if "answered_questions" not in st.session_state:
    st.session_state["answered_questions"] = set()
if "correct_answers" not in st.session_state:
    st.session_state["correct_answers"] = 0
if "current_section" not in st.session_state:
    st.session_state["current_section"] = "mcq"
if "reading_score" not in st.session_state:
    st.session_state["reading_score"] = 0

# MCQ generation and display logic from dt1.py

if st.session_state["current_section"] == "mcq":
    cola, colb, colc = st.columns([1,1,1])
    with colb:
        if st.button("START DIAGNOSTIC TEST"):
            st.session_state["answered_questions"] = set()
            st.session_state["correct_answers"] = 0
            with st.spinner("Generating questions..."):
                topics = {
                    "Idioms and expressions": ["Common idioms", "Business idioms", "Idiomatic comparisons"],
                    "Tense": ["Past tenses", "Present tenses", "Future tenses", "Perfect aspects"],
                    "Vocabulary": ["Synonyms", "Antonyms", "Collocations", "Academic words"],
                    "Relative clauses": ["Defining clauses", "Non-defining clauses", "Reduced relative clauses"],
                    "Conjunctions and connectors": ["Coordinating conjunctions", "Subordinating conjunctions", "Transitional phrases"],
                    "Comparatives and superlatives": ["Regular comparisons", "Irregular comparisons", "Idiomatic comparisons"],
                    "Phrasal verbs": ["Common phrasal verbs", "Business phrasal verbs", "Separable vs. inseparable phrasal verbs"],
                    "Articles": ["Definite article 'the'", "Indefinite articles 'a'/'an'", "Omission of articles"],
                    "Modal verbs": ["Ability (can, could)", "Permission (may, might)", "Obligation (must, should)"],
                    "Conditional sentences": ["Zero conditional", "First conditional", "Second conditional", "Third conditional", "Mixed conditionals"],
                    "Direct and indirect speech": ["Statements", "Questions", "Commands and requests"],
                    "Pronouns": ["Subject pronouns", "Object pronouns", "Possessive pronouns", "Relative pronouns"],
                    "Passive voice": ["Present passive", "Past passive", "Future passive", "Passive with modal verbs"],
                    "Prepositions": ["Prepositions of time", "Prepositions of place", "Prepositions of direction"],
                    "Word formation": ["Prefixes", "Suffixes", "Compounding", "Conversion"],
                    "Sentence structure": ["Simple sentences", "Compound sentences", "Complex sentences", "Compound-complex sentences"]
                }

                difficulties = ["beginner", "elementary", "intermediate", "advanced", "expert"]

                for topic, subtopics in topics.items():
                    subtopic = random.choice(subtopics)
                    difficulty = random.choice(difficulties)
                    
                    max_attempts = 3
                    for attempt in range(max_attempts):
                        try:
                            response = question_chain.invoke({
                                "topic": topic, 
                                "subtopic": subtopic,
                                "difficulty": difficulty,
                            })
                            
                            parsed = parse_response(response)
                            
                            st.session_state["questions"][topic] = parsed
                            options = [parsed['correct_answer']] + (parsed.get('incorrect_options', []))
                            if len(options) >= 2:  # Ensure we have at least 2 options
                                random.shuffle(options)
                                st.session_state["shuffled_options"][topic] = options
                                break  # Successfully generated a valid question
                        except ValueError as e:
                            if attempt == max_attempts - 1:
                                st.warning(f"Failed to generate a valid question for {topic} after {max_attempts} attempts: {str(e)}")
                        except Exception as e:
                            if attempt == max_attempts - 1:
                                st.error(f"Unexpected error generating question for {topic}: {str(e)}")

    if "questions" in st.session_state:
        for topic, parsed in st.session_state["questions"].items():
            st.markdown(f'<h2 class="sub-title">{topic.capitalize()}</h2>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="question-text">{parsed["question"]}</div>', unsafe_allow_html=True)
            
            options = st.session_state["shuffled_options"].get(topic, [])
            disabled = topic in st.session_state["answered_questions"]
            selected_answer = st.radio(f"Select the correct answer for {topic}:", options, key=f"{topic}_radio", disabled=disabled, label_visibility="visible")
            
            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                check_answer = st.button(f"Check Answer", key=f"{topic}_check", disabled=disabled)
            
            if check_answer:
                st.session_state["answered_questions"].add(topic)
                if selected_answer == parsed['correct_answer']:
                    st.session_state[f"{topic}_result"] = "correct"
                    st.session_state["correct_answers"] += 1
                else:
                    st.session_state[f"{topic}_result"] = "incorrect"
                st.session_state[f"{topic}_explanation"] = parsed['explanation']

            if topic in st.session_state["answered_questions"]:
                if st.session_state.get(f"{topic}_result") == "correct":
                    st.markdown('<div class="custom-success">✅ Correct!</div>', unsafe_allow_html=True)
                elif st.session_state.get(f"{topic}_result") == "incorrect":
                    st.markdown(f'<div class="custom-error">❌ Incorrect. The correct answer is: {parsed["correct_answer"]}</div>', unsafe_allow_html=True)
                
                if f"{topic}_explanation" in st.session_state:
                    st.markdown(f'<div class="custom-info">ℹ️ Explanation: {st.session_state[f"{topic}_explanation"]}</div>', unsafe_allow_html=True)

            st.markdown("<hr>", unsafe_allow_html=True)
    if len(st.session_state["answered_questions"]) == len(st.session_state["questions"]) and len(st.session_state["answered_questions"]) != 0:
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            if st.button("Proceed to Reading Exercise"):
                st.session_state["current_section"] = "reading"
                st.rerun()
elif st.session_state["current_section"] == "reading":
    llm = ChatGroq(model_name="llama3-8b-8192", api_key="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", temperature=0.7)
    st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

    body {
        font-family: 'Poppins', sans-serif;
        background-color: #f0f2f6;
        color: #333;
    }

    .context-box, .question-box, .answer-box, .evaluation-box, .explanation-box {
        font-family: 'Poppins', sans-serif;
        font-size: 16px;
        line-height: 1.6;
        padding: 20px;
        margin-bottom: 25px;
        border-radius: 0 12px 12px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .main-title {
        font-size: 40px;
        font-weight: 700;
        color: #1e88e5;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .context-box {
        background-color: #e3f2fd;
        border-left: 5px solid #1e88e5;
    }

    .question-box {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        font-size: 18px;
        font-weight: 500;
    }

    .answer-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }

    .evaluation-box {
        background-color: #f3e5f5;
        border-left: 5px solid #9c27b0;
    }

    .explanation-box {
        background-color: #e1f5fe;
        border-left: 5px solid #03a9f4;
    }

    .box-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 10px;
        color: #333;
    }

    .box-content {
        font-size: 16px;
        font-weight: 400;
    }

    /* New button styles */
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

    
    </style>
    """, 
    unsafe_allow_html=True
)
    st.subheader("Reading Comprehension Exercise")
    
    if 'context' not in st.session_state:
        st.session_state.context = ""
        st.session_state.question = ""
        st.session_state.correct_answer = ""
        st.session_state.explanation = ""
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = ""
    if 'evaluation' not in st.session_state:
        st.session_state.evaluation = ""
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

    # Randomly select difficulty level
    difficulty_levels = ["easy", "medium", "hard", "very hard"]
    selected_difficulty = random.choice(difficulty_levels)

    # Generate new content when the button is pressed
    if st.button("Generate New Question", key="generate_new_question"):
        st.session_state.submitted = False
        st.session_state.user_answer = ""
        st.session_state.evaluation = ""
        # Generate passage and question
        chain = LLMChain(llm=llm, prompt=question_prompt_reading)
        response = chain.run(difficulty=selected_difficulty)
        print(response)
        
        # Parse the response
        st.session_state.context = response.split("Context:")[1].split("Question:")[0].strip()
        st.session_state.question = response.split("Question:")[1].split("Correct Answer:")[0].strip()
        st.session_state.correct_answer = response.split("Correct Answer:")[1].split("Explanation:")[0].strip()
        st.session_state.explanation = response.split("Explanation:")[1].strip()

    # Display passage and question
    if st.session_state.context:
        st.markdown(f'<div class="context-box"><div class="box-title">Context:</div><div class="box-content">{st.session_state.context}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="question-box"><div class="box-title">Question:</div><div class="box-content">{st.session_state.question}</div></div>', unsafe_allow_html=True)

        # User input for the answer
        if not st.session_state.submitted:
            user_answer = st.text_input("Your answer:", key="user_answer_input")
            submit_button = st.button("Submit Answer", key="submit_answer")
        else:
            user_answer = st.text_input("Your answer:", value=st.session_state.user_answer, disabled=True)
            submit_button = st.button("Submit Answer", key="submit_answer", disabled=True)

        if submit_button and not st.session_state.submitted:
            if user_answer:
                st.session_state.submitted = True
                st.session_state.user_answer = user_answer
                # Use LLM to compare answers using the rubric
                comparison_chain = LLMChain(llm=llm, prompt=comparison_prompt)
                comparison_response = comparison_chain.run(
                    user_answer=user_answer, 
                    correct_answer=st.session_state.correct_answer, 
                    context=st.session_state.context,
                    question=st.session_state.question,
                    rubric=rubric
                )
                print(comparison_response)
                
                st.session_state.evaluation = comparison_response
                
                # # Extract the total score from the evaluation
                total_score_line = [line for line in st.session_state.evaluation.split('\n') if line.startswith("Total Score:")][0]
                st.session_state.reading_score = float(total_score_line.split(':')[1].split('/')[0].strip())
            else:
                st.warning("Please enter your answer before submitting.")

        # Display the answer, correct answer, explanation, and evaluation if available
        if st.session_state.submitted:
            st.markdown(f'<div class="answer-box"><div class="box-title">Your Answer:</div><div class="box-content">{st.session_state.user_answer}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="answer-box"><div class="box-title">Sample Correct Answer:</div><div class="box-content">{st.session_state.correct_answer}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="explanation-box"><div class="box-title">Explanation:</div><div class="box-content">{st.session_state.explanation}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="evaluation-box"><div class="box-title">Evaluation:</div><div class="box-content">{st.session_state.evaluation}</div></div>', unsafe_allow_html=True)
            
            if st.button("View Final Results"):
                st.session_state["current_section"] = "results"
                st.rerun()

# Results Section
elif st.session_state["current_section"] == "results":
    st.markdown(
    """
    <style>
    .score-container {
        font-size: 20px;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-top: 20px;
    }
    .chart-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .cefr-level {
        font-size: 24px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-top: 30px;
        padding: 10px;
        border: 2px solid #1E88E5;
        border-radius: 10px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)
    st.subheader("Final Results")
    
    mcq_score = st.session_state["correct_answers"]
    mcq_total = len(st.session_state["questions"])
    mcq_percentage = (mcq_score / mcq_total) * 100
    
    reading_score = st.session_state["reading_score"]
    reading_total = 20  # Assuming the total score for reading exercise is 20
    reading_percentage = (reading_score / reading_total) * 100
    
    total_score = mcq_score + reading_score
    total_possible = mcq_total + reading_total
    total_percentage = (total_score / total_possible) * 100
    
    # Determine CEFR level
    cefr_level = determine_cefr_level(total_percentage)
    
    # Display scores with custom CSS class
    st.markdown(f'<div class="score-container">MCQ Score: {mcq_score}/{mcq_total} ({mcq_percentage:.1f}%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="score-container">Reading Exercise Score: {reading_score}/{reading_total} ({reading_percentage:.1f}%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="score-container">Total Score: {total_score}/{total_possible} ({total_percentage:.1f}%)</div>', unsafe_allow_html=True)
    
    # Display CEFR level
    st.markdown(f'<div class="cefr-level">Your CEFR Level: {cefr_level}</div>', unsafe_allow_html=True)

    # Display chart (keep the existing chart code)
    df = pd.DataFrame({
        'Category': ['MCQ', 'Reading'],
        'Score': [mcq_score, reading_score],
        'Total': [mcq_total, reading_total]
    })

    chart = alt.Chart(df).mark_bar().encode(
        x='Category',
        y='Score',
        color='Category',
        tooltip=['Category', 'Score', 'Total']
    ).properties(
        title='Exercise Results',
        width=300,
        height=300
    )

    # Add a container for the chart with CSS class
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if 'username' in st.session_state:
        update_proficiency(st.session_state['username'], cefr_level)
    #     st.success(f"Your proficiency level ({cefr_level}) has been stored in your profile.")
    # else:
    #     st.warning("You need to be logged in to save your proficiency level.")

    # Display the user's previous proficiency level, if available
    # if 'username' in st.session_state:
    #     previous_proficiency = get_proficiency(st.session_state['username'])
    #     if previous_proficiency:
    #         st.info(f"Your previous proficiency level was: {previous_proficiency}")

# st.markdown('<p style="text-align: center; color: #888; margin-top: 30px;">Powered by Groq and LangChain</p>', unsafe_allow_html=True)

# if st.button("Show Session State"):
#     st.write("Session State Variables:")
#     st.write(st.session_state)