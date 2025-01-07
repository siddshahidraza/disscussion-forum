import streamlit as st
import os
from langchain import PromptTemplate, LLMChain
from langchain.llms import Ollama
from langchain.memory import ConversationBufferMemory
from better_profanity import profanity
import re

# Load profane words for moderation
profanity.load_censor_words()

# Custom moderation chain
class CustomModerationChain:
    def run(self, input_text):
        if profanity.contains_profanity(input_text):
            return {"flagged": True, "reason": "Contains inappropriate content."}
        return {"flagged": False}

# Set up the LLaMA model using Ollama in LangChain
llm = Ollama(model="llama3.2")

# Initialize memory for conversation context
memory = ConversationBufferMemory(memory_key="chat_history")

# Define the prompt template for feedback generation
feedback_template = """Provide specific and constructive feedback on the student's response about "{topic}".

Student Response:
{student_response}

Response Length: {word_count} words

Ensure that your feedback:
- Highlights strengths
- Identifies areas for improvement, specifically if the student is off-topic
- Provides actionable suggestions to help the student stay on-topic

Make sure that your feedback is concise and under {word_limit} words.

Feedback:
"""

# Create prompt template instances for feedback
feedback_prompt = PromptTemplate(
    input_variables=["topic", "student_response", "word_count", "word_limit"],
    template=feedback_template
)

# Create LLMChain instance for feedback generation
feedback_chain = LLMChain(llm=llm, prompt=feedback_prompt)

# Initialize the moderation chain for content filtering
moderation_chain = CustomModerationChain()

# Function to limit feedback to a specific word count
def limit_feedback(feedback, word_limit=None):
    if word_limit is None:
        return feedback
    feedback_words = feedback.split()
    if len(feedback_words) > word_limit:
        feedback_words = feedback_words[:word_limit]
    return " ".join(feedback_words)

# Improved function to extract feedback sections more flexibly
def extract_section(feedback, section_name):
    # General pattern to look for each section
    section_pattern = r"(?i)" + re.escape(section_name) + r":\s*(.*?)(?=\n\S|$)"
    match = re.search(section_pattern, feedback, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    else:
        # Provide a default message if the section is missing
        return f"Feedback for {section_name} is not clearly available. Here's a general suggestion: Keep focusing on improving this part."

# Adjust the feedback display for sections that are less structured
def format_feedback_box(feedback, box_title, background_color, text_color):
    # Remove duplicate or improperly nested tags
    sanitized_feedback = re.sub(r"(?i)<div.*?>|</div>", "", feedback).strip()
    
    # Create a styled feedback box
    return f"""
    <div style="
        border-radius: 10px; 
        background-color: {background_color}; 
        color: {text_color}; 
        padding: 15px; 
        margin-bottom: 20px; 
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        font-family: Arial, sans-serif;
    ">
        <h4 style="margin-top: 0; text-align: center;">{box_title}</h4>
        <p style="text-align: justify; margin: 10px 0;">{sanitized_feedback}</p>
    </div>
    """

# Adjust feedback for Option 2 in a paragraph format
def format_feedback_paragraph(feedback):
    # Extract structured sections
    strengths = extract_section(feedback, "Strengths")
    areas_for_improvement = extract_section(feedback, "Areas for Improvement")
    actionable_suggestions = extract_section(feedback, "Actionable Suggestions")
    
    # Return a paragraph-style feedback
    return f"""
    Your response shows that {strengths}. However, {areas_for_improvement}. To improve, {actionable_suggestions}.
    """

# Streamlit app setup
st.title("Discussion Forum")

# Add external CSS file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# User type selection for Teacher or Student role
user_type = st.radio("Select user type:", ("Teacher", "Student"))

if user_type == "Teacher":
    st.header("Teacher Dashboard")

    # Add new topic functionality
    new_topic = st.text_input("Add a new discussion topic:")
    if st.button("Add Topic"):
        if new_topic:
            if 'topics' not in st.session_state:
                st.session_state.topics = []
            st.session_state.topics.append(new_topic)
            st.success(f"Topic added: {new_topic}")

    # Word limit input for feedback
    word_limit = st.number_input("Enter the word limit for feedback (default is 100):", min_value=0, step=1, value=100)

    # Display existing topics and generate feedback for student responses
    if 'topics' in st.session_state and st.session_state.topics:
        st.subheader("Existing Topics:")
        for topic in st.session_state.topics:
            st.write(f"**{topic}**")
            if 'responses' in st.session_state and topic in st.session_state.responses:
                st.write("Student Responses:")
                for idx, response in enumerate(st.session_state.responses[topic]):
                    st.text_area(f"Response {idx + 1}", response, height=100, disabled=True)
                    button_key = f"feedback_button_{topic}_{idx}"
                    if st.button(f"Generate Feedback for '{topic}'", key=button_key):
                        word_count = len(response.split())

                        # Generate two feedback versions
                        feedback_1 = feedback_chain.run(
                            topic=topic,
                            student_response=response,
                            word_count=word_count,
                            word_limit=word_limit
                        )
                        feedback_2 = feedback_chain.run(
                            topic=topic,
                            student_response=response,
                            word_count=word_count,
                            word_limit=word_limit
                        )

                        # Limit feedback
                        limited_feedback_1 = limit_feedback(feedback_1, word_limit)
                        limited_feedback_2 = limit_feedback(feedback_2, word_limit)

                        # Format feedback into styled boxes
                        formatted_feedback_1 = format_feedback_box(limited_feedback_1, "Feedback Option 1", "#F1F8FF", "#0E2A47")
                        formatted_feedback_2 = format_feedback_paragraph(limited_feedback_2)

                        # Display both feedback options side by side
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("### Feedback Option 1:")
                            st.markdown(formatted_feedback_1, unsafe_allow_html=True)
                        
                        with col2:
                            st.write("### Feedback Option 2:")
                            st.markdown(formatted_feedback_2)

                        # Persist feedback selection
                        selected_feedback_key = f"selected_feedback_{topic}_{idx}"
                        if selected_feedback_key not in st.session_state:
                            st.session_state[selected_feedback_key] = "Feedback Option 1"

                        selected_feedback = st.radio(
                            "Select the best feedback:",
                            ("Feedback Option 1", "Feedback Option 2"),
                            key=selected_feedback_key
                        )

                        # Finalize feedback and share with the student
                        feedback_result_key = f"feedback_result_{topic}_{idx}"
                        if st.button("Finalize Feedback"):
                            if selected_feedback == "Feedback Option 1":
                                st.session_state[feedback_result_key] = formatted_feedback_1
                            elif selected_feedback == "Feedback Option 2":
                                st.session_state[feedback_result_key] = formatted_feedback_2
                            st.success("Feedback has been finalized and shared with the student!")
            st.markdown("---")

elif user_type == "Student":
    st.header("Student Dashboard")

    # Display topics and allow students to submit responses
    if 'topics' in st.session_state and st.session_state.topics:
        selected_topic = st.selectbox("Select a topic:", st.session_state.topics)
        student_response = st.text_area("Your response:")

        # Display character count for response guidance
        st.write(f"Character count: {len(student_response)}")

        if st.button("Submit Response"):
            if not student_response.strip():
                st.error("Please enter a response before submitting.")
            else:
                # Check moderation for inappropriate content
                moderation_result = moderation_chain.run(student_response)
                if moderation_result['flagged']:
                    st.error("Your response has been flagged for inappropriate content.")
                else:
                    if 'responses' not in st.session_state:
                        st.session_state.responses = {}
                    if selected_topic not in st.session_state.responses:
                        st.session_state.responses[selected_topic] = []
                    st.session_state.responses[selected_topic].append(student_response)
                    st.success("Response submitted successfully!")

        # Show feedback from teacher
        feedback_result_key = f"feedback_result_{selected_topic}_0"
        if feedback_result_key in st.session_state:
            st.write("Feedback from Teacher:")
            st.markdown(st.session_state[feedback_result_key])
