from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from geminiapi import get_safe_route_recommendation, get_safe_summary
import pandas as pd
from google import genai
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Load crime data
df = pd.read_csv("data/crime_2025.csv")
df.columns = df.columns.str.upper()
print("Crime data loaded:", df.shape)

# Gemini setup
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/safety")
def safety():
    neighbourhood = request.args.get("neighbourhood", "")

    # Filter by neighbourhood
    incidents = df[df["NEIGHBOURHOOD"].str.upper() == neighbourhood.upper()]

    # Count incident types
    type_counts = incidents["TYPE"].value_counts().head(5).to_dict()

    # Total
    total = len(incidents)

    return jsonify({
        "neighbourhood": neighbourhood,
        "incident_count": total,
        "incident_types": type_counts
    })

@app.route("/gemini")
def gemini():
    start = request.args.get("start", "")
    destination = request.args.get("destination", "")
    start_count = request.args.get("start_count", "unknown")
    dest_count = request.args.get("dest_count", "unknown")
    start_types = request.args.get("start_types", "")
    dest_types = request.args.get("dest_types", "")

    prompt = f"""
    You are SafeSight, a calm, supportive safety assistant for Vancouver, BC.
    
    A user is travelling from {start} to {destination}.
    
    Crime data for {start}:
    - Total incidents: {start_count}
    - Incident types: {start_types}
    
    Crime data for {destination}:
    - Total incidents: {dest_count}
    - Incident types: {dest_types}
    
    Write a calm 4-5 sentence safety briefing covering both areas.
    Focus on practical awareness for a woman travelling alone.
    End with two helpful safety tips.
    """

    try:
        response = client.models.generate_content(
            model="models/gemini-2.0-flash-lite",
            contents=prompt
        )
        return jsonify({"summary": response.text})
    except Exception as e:
        # Fallback summary if API quota is exceeded
        print("GEMINI ERROR:", str(e))
        fallback = f"Based on our data, {start} has recorded {start_count} incidents and {destination} has recorded {dest_count} incidents in 2025. The most common incidents in both areas involve theft and mischief — stay aware of your surroundings, especially in the evening. Tip 1: Stick to well-lit main streets and avoid shortcuts through quiet areas. Tip 2: If you feel unsafe, contact VPD Non-Emergency at 604-717-3321 or SFU Safe Walk at 778-782-7991."
        return jsonify({"summary": fallback})

if __name__ == "__main__":
    app.run(debug=True)