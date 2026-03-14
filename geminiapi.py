import os
from dotenv import load_dotenv
from google import genai
from crime_data import get_crime_stats_for_location

load_dotenv()

# Configure client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
You are SafeSight, a calm, supportive safety-focused assistant for Vancouver, BC.
Your goal is to translate raw crime data into clear, plain-English safety briefings.

Instructions:
1. Provide a Calm Summary: Acknowledge the data factually but avoid alarmist language.
2. If crime rates are low, reassure the user. If higher, suggest specific precautions.
3. Recommend a safe approach (e.g., Stick to the main streets like Broadway).
4. List 2 helpful resources: VPD Non-Emergency (604-717-3321) and Transit Police (604-515-8300).
"""

def get_safe_route_recommendation(origin: str, destination: str) -> str:
    try:
        # Get crime data for both locations
        origin_data = get_crime_stats_for_location(origin)
        dest_data = get_crime_stats_for_location(destination)

        prompt = f"""
        {SYSTEM_PROMPT}

        A user is travelling from {origin} to {destination}.

        Crime data for {origin}:
        - Total incidents: {origin_data.get('total_incidents', 'N/A')}
        - Incident types: {origin_data.get('incident_types', {})}

        Crime data for {destination}:
        - Total incidents: {dest_data.get('total_incidents', 'N/A')}
        - Incident types: {dest_data.get('incident_types', {})}

        Please provide a calm, clear safety briefing for this journey.
        """

        response = client.models.generate_content(
            model="models/gemini-2.0-flash-lite",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def get_safe_summary(location: str) -> str:
    try:
        data = get_crime_stats_for_location(location)

        prompt = f"""
        {SYSTEM_PROMPT}

        Crime data for {location}:
        - Total incidents: {data.get('total_incidents', 'N/A')}
        - Incident types: {data.get('incident_types', {})}

        Please provide a calm, clear safety briefing for this area.
        """

        response = client.models.generate_content(
            model="models/gemini-2.0-flash-lite",
            contents=prompt
        )
        return response.text

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"