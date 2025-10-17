import os
import pandas as pd
import time
from datetime import datetime
import re

# Define base directory as the script's location
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Works in normal script execution
except NameError:
    BASE_DIR = os.getcwd()  # Works in interactive mode (Shift + Enter in VS Code)

# Paths using relative directories
DOWNLOADS_FOLDER = os.path.join(BASE_DIR, "ASSETS", "CHAMELEON TESTS", "RETURNS")
TRACKING_FILE = os.path.join(BASE_DIR, "ASSETS", "CHAMELEON TESTS", "EXPERIMENT STRUCTURE", "Chameleon_Experiment_Results.csv")

# Load tracking CSV
df = pd.read_csv(TRACKING_FILE)

def extract_filename_details(filename):
    """Extracts harmonization details from Chameleon's filename format using melody and allNotesImportant."""
    pattern = r"^(?P<melody>[^_]+)(?:_allnotes)?(?:_(?P<style>[^_]+))?(?:_grp0_(?P<vl>[^_]+))?"
    match = re.match(pattern, filename)
    
    if match:
        details = match.groupdict()
        return {
            "Melody": details["melody"],
            "allNotesImportant": "True" if "_allnotes" in filename else "False",
            "Style": details["style"],
            "VL": details["vl"]
        }
    return None

def monitor_chameleon_outputs():
    """Monitors the downloads folder for new Chameleon files and updates tracking CSV."""
    print("Monitoring downloads folder for new Chameleon files... (Press CTRL + C to stop)")
    processed_files = set()
    
    while True:
        files = os.listdir(DOWNLOADS_FOLDER)
        new_files = [f for f in files if f.endswith(".xml") and f not in processed_files]

        for file in new_files:
            print(f"Detected file: {file}")
            details = extract_filename_details(file)
            if details:
                print(f"Extracted details: {details}")
                experiment_id = find_matching_experiment(details)
                if experiment_id:
                    append_attempt_to_csv(experiment_id, file)
                    processed_files.add(file)
                else:
                    print(f"No matching experiment found in CSV for details: {details}")
                    print("Possible matching entries:")
                    print(df[(df["Melody"] == details["Melody"])][["Experiment ID", "allNotesImportant", "Style", "VL"]])
            else:
                print("Filename does not match expected pattern.")
        
        time.sleep(5)  # Check every 5 seconds

def find_matching_experiment(details):
    """Finds the first matching experiment case, even if it was previously completed."""
    details["allNotesImportant"] = details["allNotesImportant"] == "True"  # Convert to boolean
    
    for index, row in df.iterrows():
        if (
            row['Melody'].strip().lower() == details['Melody'].strip().lower() and 
            row['allNotesImportant'] == details['allNotesImportant'] and
            row['Style'].strip().lower() == details['Style'].strip().lower() and
            row['VL'].strip().lower() == details['VL'].strip().lower()
        ):
            return row['Experiment ID']
    return None

def append_attempt_to_csv(experiment_id, filename):
    """Appends new attempts for an experiment rather than replacing existing records."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    attempt_col = f"Attempt_{timestamp}"
    
    if attempt_col not in df.columns:
        df[attempt_col] = ""
    
    df.loc[df['Experiment ID'] == experiment_id, attempt_col] = filename
    df.to_csv(TRACKING_FILE, index=False)
    print(f"Appended attempt for Experiment ID {experiment_id}: {filename}")

if __name__ == "__main__":
    monitor_chameleon_outputs()