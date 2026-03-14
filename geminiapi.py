import os
from flask.cli import load_dotenv
import google.generativeai as genai
load_dotenv()
from crime_data import get_crime_stats_for_location # We will assume this exists in crime_data.py

# 1. Configure the API Key
# Make sure to set this in your environment variables or a .env file
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# 2. Define the Function (The "Tool" for Gemini)
def fetch_local_crime_data(location: str) -> dict:
    """
    Fetches crime statistics and recent incidents for a given location in Vancouver.
    
    Args:
        location: The street address, neighborhood, or intersection in Vancouver.
    """
    # This calls your logic in crime_data.py to search the CSV
    return get_crime_stats_for_location(location)

# 3. System Instruction (Prompt Engineering)
# This dictates the persona, safety guardrails, and formatting for the output.
SYSTEM_PROMPT = """
You are SafeSight, a safety-focused routing assistant for Vancouver, BC. 
Your goal is to help users navigate safely by analyzing local crime data, suggesting safe routes, 
and providing helpful local resources.

Instructions:
1. Always use the `fetch_local_crime_data` tool to check the crime data for the user's origin and destination.
2. Provide a clear, balanced safety summary. Be honest about risks but avoid fear-mongering. 
3. Recommend safe routing practices (e.g., sticking to main arterial roads, well-lit streets).
4. Always provide 2-3 helpful safety resources (e.g., Vancouver Police Non-Emergency line, transit security numbers).
5. Format your response cleanly using markdown headings and bullet points.
"""

# 4. Initialize the Model
# We use gemini-1.5-flash as it is fast and excellent for function calling and text generation.
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[fetch_local_crime_data],
    system_instruction=SYSTEM_PROMPT
)

# 5. The Main Execution Function
def get_safe_route_recommendation(origin: str, destination: str) -> str:
    """
    Starts a chat session, passes the user's request, and returns the AI's safety recommendation.
    """
    try:
        # enable_automatic_function_calling=True allows Gemini to automatically 
        # pause, run your python function, inject the data, and resume generating the answer.
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        user_prompt = (
            f"I am currently at {origin} and I need to walk to {destination}. "
            f"Can you give me a crime summary for these areas, recommend a safe approach, "
            f"and provide safety resources?"
        )
        
        response = chat.send_message(user_prompt)
        return response.text
        
    except Exception as e:
        return f"Sorry, I encountered an error while fetching the safety route: {str(e)}"