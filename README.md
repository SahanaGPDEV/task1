# Iron Lady - AI Leadership Navigator (Task 1)

## Problem Statement
Providing personalized career guidance to thousands of prospective members is a significant challenge. Manual counseling is time-consuming and often cannot address the specific emotional and professional needs of every inquiry immediately. This leads to missed opportunities and lower engagement from women seeking leadership transformation.

## Solution
To solve this, we built **"Asha," the AI Leadership Architect**. Asha simulates a warm, empathetic 1-on-1 counseling session. She analyzes a user's profile instantly and generates a hyper-personalized leadership roadmap, recommending the perfect Iron Lady program while directly addressing the user's career goals and challenges.

## Live Demo
🚀 **[Click here to try the Live App](https://cylonnsd5ury3umdqedrfg.streamlit.app/)**

## Key Features
*   **AI-Personalized Roadmaps**: Uses Groq LPU™ to generate unique, goal-oriented plans in under 2 seconds.
*   **Warm vs. Urgent Tone (A/B Testing)**: Switch between "Supportive Mentor" and "FOMO Sales" modes to test conversion strategies.
*   **Multi-Language Support**: Accessible in English, Hindi, and Kannada for wider reach.
*   **Automated Lead Capture**: Instantly saves user details and preferences to a `leads.csv` file for the sales team.
*   **Smart Fallback**: Robust error handling ensures users get a recommendation even if the AI service is momentarily busy.

## Technology Stack
*   **Streamlit**: For the interactive web interface.
*   **Groq API (Llama-3)**: For lightning-fast AI text generation.
*   **Python**: Core programming language.
*   **Pandas/CSV**: For structured data handling and lead management.

## How to Run Locally

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/SahanaGPDEV/task.git
    cd task
    ```

2.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up Environment Keys**
    *   Create a file named `.env` in the main folder.
    *   Add your Groq API key:
        ```text
        GROQ_API_KEY="gsk_...your_key_here..."
        ```

4.  **Run the App**
    ```bash
    streamlit run app.py
    ```
