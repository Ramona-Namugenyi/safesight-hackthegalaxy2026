from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# Load crime data
df = pd.read_csv("data/crime_2025.csv")
df.columns = df.columns.str.upper()
print("Crime data loaded:", df.shape)

# Gemini setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY", "YOUR_KEY_HERE"))
model = genai.GenerativeModel("gemini-1.5-flash")

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
    neighbourhood = request.args.get("neighbourhood", "")
    incident_count = request.args.get("incident_count", "unknown")
    incident_types = request.args.get("incident_types", "")

    prompt = f"""
    You are a calm, helpful safety assistant for women and students in Vancouver.
    
    Here is recent crime data for {neighbourhood}:
    - Total incidents: {incident_count}
    - Incident types: {incident_types}
    
    Write a brief 3-4 sentence safety summary. 
    Be calm, not scary. 
    Focus on practical awareness.
    End with one helpful tip.
    """

    response = model.generate_content(prompt)
    return jsonify({"summary": response.text})

if __name__ == "__main__":
    app.run(debug=True)