from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
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
    You are a calm, helpful safety assistant for women and students in Vancouver.
    
    A user is travelling from {start} to {destination}.
    
    Crime data for {start}:
    - Total incidents: {start_count}
    - Incident types: {start_types}
    
    Crime data for {destination}:
    - Total incidents: {dest_count}
    - Incident types: {dest_types}
    
    Write a brief 4-5 sentence safety summary covering both areas.
    Be calm, not scary.
    Focus on practical awareness for a woman travelling alone.
    End with two helpful safety tips.
    """

    response = client.models.generate_content(
        model="models/gemini-2.0-flash-lite",
        contents=prompt
    )
    return jsonify({"summary": response.text})

if __name__ == "__main__":
    app.run(debug=True)