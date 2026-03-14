
from flask import Flask, request, jsonify
from geminiapi import get_safe_route_recommendation, get_safe_summary
import pandas as pd

app = Flask(__name__)

# Load crime data

df = pd.read_csv("data/crime_2025.csv")
print("Crime data loaded:", df.shape)

df.columns = df.columns.str.upper()


@app.route("/")
def home():
    return "SafeSight Backend Running"


@app.route("/safety")
def safety():

    neighbourhood = request.args.get("neighbourhood")

    incidents = df[df["NEIGHBOURHOOD"].str.lower() == neighbourhood.lower()]

    return jsonify({
        "neighbourhood": neighbourhood,
        "incident_count": len(incidents)
    })


@app.route("/get_safety_summary", methods=["POST"])
def safety_summary():
    """
    Endpoint that receives origin and destination and returns a Gemini-generated summary.
    """
    data = request.json
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return jsonify({"error": "Please provide both an origin and a destination."}), 400

    # Call the Gemini API logic
    result = get_safe_route_recommendation(origin, destination)
    
    return jsonify({"summary": result})

if __name__ == "__main__":
    app.run(debug=True)