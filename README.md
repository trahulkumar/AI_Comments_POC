# AI Feedback Insights Dashboard

A powerful, interactive dashboard built with Streamlit that leverages Google's Gemini API to automatically analyze user feedback. This tool transforms unstructured comments into actionable insights, providing sentiment analysis, theme extraction, and critical issue identification.

## 🚀 Features

-   **AI-Powered Analysis**: Uses Google Gemini (e.g., `gemini-1.5-flash`, `gemini-1.5-pro`) to deeply understand user feedback.
-   **Model Selection**: Dynamically lists and allows you to choose available Gemini models associated with your API key.
-   **Interactive Visualizations**:
    -   **Sentiment Distribution**: Visual pie charts showing positive, negative, and neutral sentiment.
    -   **Top Themes**: Bar charts highlighting the most frequent topics.
-   **Critical Issue Detection**: Automatically flags high-priority issues that require immediate attention.
-   **Actionable Recommendations**: Generates strategic next steps based on the analysis.
-   **Flexible Data Input**:
    -   Paste feedback directly.
    -   Upload CSV or Text files.
    -   Support for various formats (Standard CSV, Comma-separated, One comment per line).
    -   Robust parsing handles encoding issues and irregular formats.
-   **Exportable Reports**: Download analysis results as a structured JSON file or a formatted text report.
-   **Secure & Efficient**:
    -   API keys are masked and not stored permanently.
    -   Automatic session timeout (5 minutes) clears sensitive data to protect privacy.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/trahulkumar/AI_Comments_POC.git
    cd AI_Comments_POC
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 🔑 Configuration

You need a Google Gemini API key to use this application.
1.  Get your API key from [Google AI Studio](https://aistudio.google.com/).
2.  Enter the key in the application sidebar when prompted.

## ▶️ Usage

1.  **Run the Streamlit app:**
    ```bash
    streamlit run streamlit_dashboard.py
    ```

2.  **Navigate to the local URL** provided in the terminal (usually `http://localhost:8501`).

3.  **Enter your API Key** in the sidebar.

4.  **Input Data**:
    -   **Option A**: Paste a list of comments into the text area.
    -   **Option B**: Upload a CSV or TXT file. You can adjust parsing settings (e.g., skip lines, select specific columns) in the "Upload CSV" tab.

5.  **Click "Analyze Feedback"**.

6.  **Explore Insights**: Review the generated summary, charts, and recommendations.

7.  **Export**: Use the buttons at the bottom to download your report.

## 📂 Project Structure

-   `streamlit_dashboard.py`: The main application entry point, handling the UI and user interaction.
-   `feedback_analyzer.py`: Core logic for interacting with the Google Gemini API and processing responses.
-   `requirements.txt`: List of Python dependencies.
-   `list_models.py`: Utility script to check available models via CLI.

## 🛡️ Security Note

This application is designed with security in mind.
-   **Session Timeout**: If the app is left idle for 5 minutes, the session will time out, and all loaded data (feedback and insights) will be cleared from memory.
-   **Data Handling**: Data is processed in-memory and sent to the Gemini API for analysis. It is not persisted to any database by this application.
