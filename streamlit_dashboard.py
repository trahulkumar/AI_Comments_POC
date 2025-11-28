import streamlit as st
from feedback_analyzer import FeedbackAnalyzer
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
from streamlit.web import cli as stcli

if __name__ == "__main__":
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if not get_script_run_ctx():
            sys.argv = ["streamlit", "run", sys.argv[0]]
            sys.exit(stcli.main())
    except ImportError:
        pass

# Page config
st.set_page_config(
    page_title="AI Feedback Insights Dashboard",
    page_icon="✨",
    layout="wide"
)

# Reduce whitespace at the top
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Session Timeout Logic
TIMEOUT_SECONDS = 300  # 5 minutes

if 'last_active' not in st.session_state:
    st.session_state.last_active = time.time()

def check_timeout():
    if time.time() - st.session_state.last_active > TIMEOUT_SECONDS:
        # Clear sensitive data from memory
        if 'insights' in st.session_state:
            del st.session_state.insights
        if 'feedback_text' in st.session_state:
            del st.session_state.feedback_text
            
        st.warning("⚠️ Session timed out due to inactivity (5 minutes). Data has been cleared.")
        if st.button("Restart Session"):
            st.session_state.last_active = time.time()
            st.rerun()
        st.stop()
    else:
        st.session_state.last_active = time.time()

check_timeout()

# Initialize session state
if 'insights' not in st.session_state:
    st.session_state.insights = None

if 'feedback_text' not in st.session_state:
    st.session_state.feedback_text = ""



# Header
st.title("✨ AI Feedback Insights Dashboard")
st.markdown("Analyze user feedback with AI-powered insights")

# Sidebar for API key
with st.sidebar:
    st.markdown("### 📖 How to use")
    st.markdown("""
    1. **Enter API Key**: Enter your Google Gemini API key below.
    2. **Select Model**: Choose a model from the dropdown (appears after entering key).
    3. **Provide Data**:
        *   **Enter Feedback Tab**: Paste text or click 'Load Sample Data'.
        *   **Upload CSV Tab**: Upload a file and click 'Use this data'.
    4. **Analyze**: Click the '🚀 Analyze Feedback' button.
    """)
    st.markdown("---")

    st.header("🔑 Configuration")
    api_key = st.text_input("Gemini API Key", type="password", 
                             help="Enter your Google Gemini API key")
    
    model_name = "gemini-flash-latest"
    if api_key:
        with st.spinner("Fetching models..."):
            available_models = FeedbackAnalyzer.list_available_models(api_key)
            if available_models:
                # Try to set default to flash if available
                default_index = 0
                for i, m in enumerate(available_models):
                    if 'flash' in m.lower():
                        default_index = i
                        break
                model_name = st.selectbox("Select Model", available_models, index=default_index)

# Sample data
sample_feedback = """The new update is amazing! Love the dark mode feature.
The app crashes when I try to upload large files. Very frustrating.
Customer support was helpful and responsive.
Pricing is too high compared to competitors.
The interface is confusing, hard to find basic features.
Great product overall, but needs better documentation.
Export feature doesn't work properly, keeps timing out.
Love the new dashboard layout! Much cleaner.
Mobile app is slow and buggy.
Feature request: Please add two-factor authentication.
Best tool I've used for project management!
The search function is broken, can't find anything.
Integration with Slack works perfectly.
Loading times are unacceptable, takes forever.
Really impressed with the recent improvements."""

# Main content
tab1, tab2 = st.tabs(["📝 Enter Feedback", "📁 Upload CSV"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        feedback_text = st.text_area(
            "Enter feedback (one per line)",
            height=150,
            placeholder="Paste your feedback here...",
            key="feedback_text"
        )
    # Callbacks
    def load_sample_data():
        st.session_state.feedback_text = sample_feedback

    with col2:
        st.write("")
        st.write("")
        st.button("Load Sample Data", use_container_width=True, on_click=load_sample_data)

with tab2:
    col_settings, col_upload = st.columns(2)
    
    with col_settings:
        st.subheader("File Settings")
        file_structure = st.radio(
            "File Structure",
            ["Standard CSV", "Comma Separated", "One Comment Per Line"],
            help="Select how your data is structured"
        )
        
        start_line = 1
        if file_structure == "One Comment Per Line":
            start_line = st.number_input("Start reading from line", min_value=1, value=1)
            
    with col_upload:
        st.subheader("Upload File")
        uploaded_file = st.file_uploader("Choose a file", type=['csv', 'txt'])
    
    if uploaded_file:
        df = None
        
        # Helper to read content with fallback encoding
        def read_content(file):
            file.seek(0)
            try:
                return file.read().decode('utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                return file.read().decode('cp1252', errors='replace')

        if file_structure == "Standard CSV":
            try:
                try:
                    df = pd.read_csv(uploaded_file)
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='cp1252')
            except Exception:
                # Fallback for CSV
                content = read_content(uploaded_file)
                lines = [line.strip().strip('"').strip() for line in content.split('\n') if line.strip()]
                df = pd.DataFrame(lines, columns=['feedback'])
                st.warning("⚠️ CSV parsing failed. Loaded file as plain text list.")
                
        elif file_structure == "Comma Separated":
            content = read_content(uploaded_file)
            # Split by comma and clean up
            comments = [c.strip().strip('"').strip() for c in content.split(',') if c.strip()]
            df = pd.DataFrame(comments, columns=['feedback'])
            
        elif file_structure == "One Comment Per Line":
            content = read_content(uploaded_file)
            lines = [line.strip() for line in content.split('\n')]
            # Apply start line (convert 1-based to 0-based index)
            if start_line <= len(lines):
                comments = [l for l in lines[start_line-1:] if l.strip()]
                df = pd.DataFrame(comments, columns=['feedback'])
            else:
                st.error(f"Start line {start_line} is beyond the end of the file ({len(lines)} lines).")
        
        if df is not None:
            st.dataframe(df.head())
            
            # Get column for feedback (only if multiple columns exist, otherwise default to first)
            if len(df.columns) > 1:
                feedback_col = st.selectbox("Select feedback column", df.columns)
            else:
                feedback_col = df.columns[0]
                st.info(f"Using column '{feedback_col}' for feedback.")
            
            def load_csv_data(dataframe, col):
                st.session_state.feedback_text = '\n'.join(dataframe[col].astype(str).tolist())
            
            st.button("Use this data", on_click=load_csv_data, args=(df, feedback_col))
            
            if st.session_state.feedback_text and len(df) > 0 and st.session_state.feedback_text.startswith(str(df[feedback_col].iloc[0])[:20]):
                 st.success(f"Loaded {len(df)} feedback comments into the analysis tab.")

# Analyze button
if st.button("🚀 Analyze Feedback", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar")
    elif not st.session_state.feedback_text:
        st.error("Please enter some feedback to analyze")
    else:
        with st.spinner("Analyzing feedback with AI..."):
            try:
                analyzer = FeedbackAnalyzer(api_key=api_key, model_name=model_name)
                insights = analyzer.analyze_feedback(st.session_state.feedback_text)
                st.session_state.insights = insights
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Display insights
if st.session_state.insights:
    insights = st.session_state.insights
    
    st.markdown("---")
    
    # Summary
    st.header("📊 Executive Summary")
    st.info(insights['summary'])
    
    # Key metrics
    st.header("📈 Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_feedback = len(feedback_text.split('\n'))
        st.metric("Total Feedback", total_feedback, help="Number of comments analyzed")
    
    with col2:
        positive = next((s['value'] for s in insights['sentimentDistribution'] if s['name'] == 'Positive'), 0)
        st.metric("Positive", positive, help="Happy customers")
    
    with col3:
        issues = len(insights['criticalIssues'])
        st.metric("Critical Issues", issues, delta=f"-{issues}", delta_color="inverse", help="Issues requiring attention")
    
    # Charts
    st.header("📊 Visual Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Distribution")
        sentiment_df = pd.DataFrame(insights['sentimentDistribution'])
        fig = px.pie(sentiment_df, values='value', names='name', 
                     color='name',
                     color_discrete_map={'Positive': '#10b981', 'Negative': '#ef4444', 'Neutral': '#6b7280'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Top Themes")
        themes_df = pd.DataFrame(insights['topThemes'][:5])
        fig = px.bar(themes_df, x='theme', y='count', 
                     color='sentiment',
                     color_discrete_map={'positive': '#10b981', 'negative': '#ef4444', 'neutral': '#6b7280'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Critical Issues
    st.header("🚨 Critical Issues")
    for issue in insights['criticalIssues']:
        priority_color = {
            'high': 'error',
            'medium': 'warning',
            'low': 'info'
        }
        with st.container():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{issue['issue']}**")
            with col2:
                st.markdown(f"`{issue['priority'].upper()}`")
            st.caption(f"📊 {issue['mentions']} mentions")
        st.markdown("---")
    
    # Recommendations
    st.header("💡 AI Recommendations")
    for i, rec in enumerate(insights['recommendations'], 1):
        st.success(f"{i}. {rec}")
        
    # Metadata Footer
    st.markdown("---")
    if 'model_used' in insights:
        st.caption(f"🤖 Generated with **{insights['model_used']}** on {insights.get('generated_at', 'Unknown Date')} in {insights.get('execution_time', '0')}s")
    
    # Export options
    st.header("💾 Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        insights_json = json.dumps(insights, indent=2)
        st.download_button(
            "Download JSON",
            insights_json,
            "insights.json",
            "application/json",
            use_container_width=True
        )
    
    with col2:
        # Create summary report
        report = f"""FEEDBACK ANALYSIS REPORT
Generated: {insights.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
Model: {insights.get('model_used', 'Unknown')}
Execution Time: {insights.get('execution_time', '0')}s

SUMMARY:
{insights['summary']}

SENTIMENT DISTRIBUTION:
{chr(10).join([f"- {s['name']}: {s['value']}" for s in insights['sentimentDistribution']])}

TOP THEMES:
{chr(10).join([f"{i+1}. {t['theme']} ({t['count']} mentions)" for i, t in enumerate(insights['topThemes'][:5])])}

CRITICAL ISSUES:
{chr(10).join([f"- [{i['priority'].upper()}] {i['issue']} ({i['mentions']} mentions)" for i in insights['criticalIssues']])}

RECOMMENDATIONS:
{chr(10).join([f"{i+1}. {r}" for i, r in enumerate(insights['recommendations'])])}
"""
        st.download_button(
            "Download Report",
            report,
            "report.txt",
            "text/plain",
            use_container_width=True
        )
