import google.generativeai as genai
import json
import pandas as pd
from datetime import datetime
import time

class FeedbackAnalyzer:
    def __init__(self, api_key, model_name='gemini-flash-latest'):
        """Initialize the analyzer with your Gemini API key and model name"""
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    @staticmethod
    def list_available_models(api_key):
        """List available Gemini models for the given API key"""
        genai.configure(api_key=api_key)
        models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    models.append(m.name.replace('models/', ''))
        except Exception as e:
            print(f"Error listing models: {e}")
            return ['gemini-flash-latest'] # Fallback
        return models
    
    def analyze_feedback(self, feedback_list):
        """
        Analyze a list of feedback comments using Gemini
        
        Args:
            feedback_list: List of feedback strings or a pandas DataFrame
        
        Returns:
            Dictionary containing insights
        """
        # Convert DataFrame to list if needed
        if isinstance(feedback_list, pd.DataFrame):
            if 'feedback' in feedback_list.columns:
                feedback_text = '\n'.join(feedback_list['feedback'].tolist())
            else:
                feedback_text = '\n'.join(feedback_list.iloc[:, 0].tolist())
        else:
            feedback_text = '\n'.join(feedback_list)
        
        # Create the analysis prompt
        prompt = f"""Analyze the following user feedback comments and provide insights in JSON format only (no markdown, no preamble):

Feedback:
{feedback_text}

Return a JSON object with this exact structure:
{{
  "sentimentDistribution": [
    {{"name": "Positive", "value": <number>}},
    {{"name": "Negative", "value": <number>}},
    {{"name": "Neutral", "value": <number>}}
  ],
  "topThemes": [
    {{"theme": "<theme name>", "count": <number>, "sentiment": "positive|negative|neutral"}}
  ],
  "criticalIssues": [
    {{"issue": "<brief issue>", "priority": "high|medium|low", "mentions": <number>}}
  ],
  "trendingTopics": [
    {{"topic": "<topic>", "mentions": <number>}}
  ],
  "summary": "<brief 2-3 sentence summary>",
  "recommendations": ["<action 1>", "<action 2>", "<action 3>"]
}}"""
        
        # Call Gemini API
        start_time = time.time()
        response = self.model.generate_content(prompt)
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Parse the response
        response_text = response.text
        clean_response = response_text.replace('```json', '').replace('```', '').strip()
        insights = json.loads(clean_response)
        
        # Add metadata
        insights['model_used'] = self.model_name
        insights['generated_at'] = datetime.now().isoformat()
        insights['execution_time'] = round(execution_time, 2)
        
        return insights
    
    def save_insights(self, insights, filename='insights.json'):
        """Save insights to a JSON file"""
        if 'generated_at' not in insights:
            insights['generated_at'] = datetime.now().isoformat()
        with open(filename, 'w') as f:
            json.dump(insights, f, indent=2)
        print(f"Insights saved to {filename}")
    
    def print_insights(self, insights):
        """Print insights in a readable format"""
        print("\n" + "="*60)
        print("FEEDBACK ANALYSIS INSIGHTS")
        print("="*60)
        
        print(f"\n📊 SUMMARY:")
        print(f"{insights['summary']}\n")
        
        print(f"😊 SENTIMENT DISTRIBUTION:")
        for sentiment in insights['sentimentDistribution']:
            print(f"  {sentiment['name']}: {sentiment['value']}")
        
        print(f"\n🎯 TOP THEMES:")
        for i, theme in enumerate(insights['topThemes'][:5], 1):
            print(f"  {i}. {theme['theme']} ({theme['count']} mentions) - {theme['sentiment']}")
        
        print(f"\n🚨 CRITICAL ISSUES:")
        for i, issue in enumerate(insights['criticalIssues'], 1):
            priority_emoji = "🔴" if issue['priority'] == 'high' else "🟡" if issue['priority'] == 'medium' else "🟢"
            print(f"  {priority_emoji} {issue['issue']} [{issue['priority'].upper()}] - {issue['mentions']} mentions")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(insights['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Sample feedback data
    sample_feedback = [
        "The new update is amazing! Love the dark mode feature.",
        "The app crashes when I try to upload large files. Very frustrating.",
        "Customer support was helpful and responsive.",
        "Pricing is too high compared to competitors.",
        "The interface is confusing, hard to find basic features.",
        "Great product overall, but needs better documentation.",
        "Export feature doesn't work properly, keeps timing out.",
        "Love the new dashboard layout! Much cleaner.",
        "Mobile app is slow and buggy.",
        "Feature request: Please add two-factor authentication.",
        "Best tool I've used for project management!",
        "The search function is broken, can't find anything.",
        "Integration with Slack works perfectly.",
        "Loading times are unacceptable, takes forever.",
        "Really impressed with the recent improvements."
    ]
    
    # Initialize analyzer with your API key
    # Replace 'your-api-key' with your actual Gemini API key
    analyzer = FeedbackAnalyzer(api_key='update-here')
    
    # Analyze feedback
    print("Analyzing feedback...")
    insights = analyzer.analyze_feedback(sample_feedback)
    
    # Print results
    analyzer.print_insights(insights)
    
    # Save to file
    analyzer.save_insights(insights)
    
    # Example: Loading from CSV
    # df = pd.read_csv('feedback.csv')
    # insights = analyzer.analyze_feedback(df)