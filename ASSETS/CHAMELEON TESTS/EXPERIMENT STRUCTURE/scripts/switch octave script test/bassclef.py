from music21 import converter, stream, clef, metadata
import os

# Define base directory as the script's location
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Works when running as a script
except NameError:
    BASE_DIR = os.getcwd()  # Works when running interactively in VS Code

# Define paths using relative directories
CHAMELEON_RESULTS_FOLDER = BASE_DIR
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Converted")

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def convert_to_bass_clef(input_file, output_file):
    """Converts the harmonic rhythm part of a MusicXML file to bass clef while keeping absolute pitch the same."""
    score = converter.parse(input_file)
    detected_parts = [part.partName if part.partName else "Unnamed" for part in score.parts]
    print("Detected parts:", detected_parts)  # Debugging step to print part names
    
    # Extract title and unique ID from filename
    filename_base = os.path.basename(input_file)
    file_title = filename_base.split("_")[0]
    file_id = filename_base.split("_")[-1].split(".")[0]  # Extracting the unique identifier
    
    # Set metadata
    score.metadata = metadata.Metadata()
    score.metadata.title = file_title
    score.metadata.composer = "Chameleon"
    score.metadata.movementName = file_id  # Set subtitle as unique ID
    
    for part in score.parts:
        print(f"Checking part: {part.partName if part.partName else 'Unnamed'}")
        if part.partName and 'harmonic  rhythm' in part.partName.lower():  # Identify harmony part
            print(f"Converting part: {part.partName} to Bass Clef")
            
            # Remove existing clef from measure 1 if present
            first_measure = part.measure(1)
            if first_measure:
                existing_clefs = first_measure.getElementsByClass(clef.Clef)
                if existing_clefs:
                    for existing_clef in existing_clefs:
                        first_measure.remove(existing_clef)  # Explicitly remove existing clef
                    print("Removed existing clef in measure 1.")
            
            # Insert the new bass clef at the beginning of the part
            part.insert(0, clef.BassClef())
            
            # Apply the clef at the start of every measure
            for measure in part.getElementsByClass("Measure"):
                measure.insert(0, clef.BassClef())

            print("Bass clef applied to all measures, including measure 1.")
        else:
            print("Skipping part.")
    
    score.write("musicxml", output_file)
    print(f"Converted {os.path.basename(input_file)} -> {os.path.basename(output_file)}")

def process_all_chameleon_results():
    """Iterates through all Chameleon XML files and converts harmony parts to bass clef."""
    for filename in os.listdir(CHAMELEON_RESULTS_FOLDER):
        if filename.endswith(".xml"):
            input_path = os.path.join(CHAMELEON_RESULTS_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            print(f"Processing file: {filename}")
            convert_to_bass_clef(input_path, output_path)
    print(f"All files converted. Output saved to {OUTPUT_FOLDER}")

if __name__ == "__main__":
    process_all_chameleon_results()
