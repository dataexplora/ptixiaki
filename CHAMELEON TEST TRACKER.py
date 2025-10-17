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
    """Extracts details from Chameleon's filename format, distinguishing between blended and non-blended cases."""
    
    print(f"DEBUG: Processing filename: {filename}")  # Debugging output

    # If it's a blended experiment (contains "bl_")
    if "_bl_" in filename:
        pattern = r"(?P<melody>[^_]+)(?:_allnotes)?_bl_(?P<style>[^[]+)\[(?P<mode>[^\]]+)\](?:_D0_)?(?P<blended_style>[^[]+)\[(?P<blended_mode>[^\]]+)\]_grp0_(?P<vl>[^_]+)"
    else:
        pattern = r"(?P<melody>[^_]+)(?:_allnotes)?_(?P<style>[^[]+)\[(?P<mode>[^\]]+)\]_grp0_(?P<vl>[^_]+)"

    match = re.match(pattern, filename)
    
    if match:
        details = match.groupdict()
        print(f"DEBUG: Extracted details: {details}")  # Debugging output
        return {
            "Melody": details["melody"],
            "allNotesImportant": "True" if "_allnotes" in filename else "False",
            "Style": details["style"],
            "Mode": f"[{details['mode']}]",  # Correctly extracts mode
            "Blend": "True" if "_bl_" in filename else "False",
            "Blended Style": details.get("blended_style", "None"),
            "Blended Mode": f"[{details.get('blended_mode', 'None')}]",
            "VL": details["vl"]
        }

    print(f"⚠ DEBUG: Filename does not match expected pattern: {filename}")
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
                    update_status_to_complete(experiment_id)
                    update_timestamp(experiment_id)
                    processed_files.add(file)
                else:
                    print(f"No matching experiment found in CSV for details: {details}")
                    print("Possible matching entries:")
                    print(df[(df["Melody"] == details["Melody"])]
                          [["Experiment ID", "allNotesImportant", "Style", "VL"]])
            else:
                print("Filename does not match expected pattern.")
        
        time.sleep(5)  # Check every 5 seconds

def find_matching_experiment(details):
    """Finds the first matching experiment case by checking all relevant attributes."""
    details["allNotesImportant"] = details["allNotesImportant"] == "True"  # Convert to boolean
    
    matched_rows = df[
        (df["Melody"].str.strip().str.lower() == details["Melody"].strip().lower()) &
        (df["allNotesImportant"] == details["allNotesImportant"]) &
        (df["Style"].str.strip().str.lower() == details["Style"].strip().lower()) &
        (df["Mode"].str.strip() == details["Mode"].strip()) &
        (df["Blend"] == (details["Blend"] == "True")) &
        (df["Blended Style"].str.strip().str.lower() == details["Blended Style"].strip().lower()) &
        (df["Blended Mode"].str.strip() == details["Blended Mode"].strip()) &
        (df["VL"].str.strip().str.lower() == details["VL"].strip().lower())
    ]

    if not matched_rows.empty:
        return matched_rows["Experiment ID"].values[0]  # Return the correct matching Experiment ID
    
    print(f"⚠ No exact match found for details: {details}")
    return None

def append_attempt_to_csv(experiment_id, filename):
    """Stores the filename in the correct column instead of adding a new one."""
    df["filename"] = df["filename"].astype(str)  # Ensure column is string type
    df.loc[df['Experiment ID'] == experiment_id, 'filename'] = filename
    df.to_csv(TRACKING_FILE, index=False)
    print(f"Updated Filename for Experiment ID {experiment_id}: {filename}")


def update_status_to_complete(experiment_id):
    """Updates the Status column of an experiment to 'Complete' when an attempt is logged."""
    df["Status"] = df["Status"].astype(str)  # Ensure column is string type
    df.loc[df['Experiment ID'] == experiment_id, 'Status'] = 'Complete'
    df.to_csv(TRACKING_FILE, index=False)
    print(f"Updated status to 'Complete' for Experiment ID {experiment_id}")


def update_timestamp(experiment_id):
    """Updates the Timestamp column with the current date and time."""
    df["Timestamp"] = df["Timestamp"].astype(str)  # Ensure entire column is string
    df.loc[df['Experiment ID'] == experiment_id, 'Timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(TRACKING_FILE, index=False)
    print(f"Updated timestamp for Experiment ID {experiment_id}")


if __name__ == "__main__":
    monitor_chameleon_outputs()
