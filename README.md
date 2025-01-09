
# Discussion Forum with Feedback Generation

This project is a **Streamlit-based discussion forum application** designed for teachers and students. It features real-time student response feedback generation using the **LLaMA 3.2 model** powered by **Ollama**, along with content moderation to ensure responses are appropriate.



## Features

- **Role-Based Access**: 
  - **Teacher Dashboard**: Add topics, view student responses, and generate feedback.
  - **Student Dashboard**: Submit responses to topics and view teacher feedback.

- **Feedback Generation**: 
  - Generates constructive and concise feedback on student responses.
  - Includes options for multiple feedback formats.

- **Content Moderation**:
  - Detects and flags inappropriate content using the `better-profanity` library.

- **Word Limit Control**:
  - Customizable word limit for feedback generation.

- **Custom Styling**:
  - Supports an external CSS file (`style.css`) for UI customization.

---

## Installation

Follow these steps to set up and run the application:

### Prerequisites

- **Python 3.9 or later**
- **Ollama installed** for running the LLaMA 3.2 model locally.
- **Streamlit** for building the web app.

### Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/discussion-forum.git
   cd discussion-forum
