import pandas as pd
import os

def get_crime_stats_for_location(location: str) -> dict:
    """
    Searches the Vancouver crime CSV for a specific neighborhood and returns a summary.
    """
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'data', 'crime_2025.csv')
    
    try:
        df = pd.read_csv(csv_path)
        # Standardize columns to match your CSV (TYPE, NEIGHBOURHOOD, etc.)
        df.columns = df.columns.str.upper()
        
        # Search logic: find rows where the neighbourhood matches the user input
        # Note: We use .str.contains to be flexible if a user types "Downtown" vs "Central Business District"
        matches = df[df['NEIGHBOURHOOD'].str.contains(location, case=False, na=False)]
        
        if matches.empty:
            return {"message": f"No specific crime records found for {location} in our 2025 dataset."}

        # Create a helpful summary for Gemini to interpret
        stats = {
            "neighborhood": location,
            "total_incidents": len(matches),
            "common_incidents": matches['TYPE'].value_counts().head(3).to_dict(),
            "recent_years": matches['YEAR'].unique().tolist()
        }
        return stats
        
    except Exception as e:
        return {"error": f"Data access error: {str(e)}"}