import google.generativeai as genai
import os

# Use the key from the file or environment
api_key = 'AIzaSyAQbD9TfL6G3cdy3FZF1j9WzYUuoi3JO7A'
genai.configure(api_key=api_key)

print("Listing available models:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
