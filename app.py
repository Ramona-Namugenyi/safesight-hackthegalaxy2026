
from flask import Flask, request, jsonify
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


if __name__ == "__main__":
    app.run(debug=True)