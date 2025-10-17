import os
import pandas as pd
from music21 import converter, chord

# Define base directory as the script's location
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Works when running as a script
except NameError:
    BASE_DIR = os.getcwd()  # Works when running interactively in VS Code

# Define paths using relative directories
REFERENCE_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "PTIXIAKI", "ASSETS", "CHAMELEON TESTS", "Templates", "Rebetiko", "ORIGINAL", "RebetikoReferenceHarmony.xml"))
CHAMELEON_RESULTS_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "..", "PTIXIAKI", "ASSETS", "CHAMELEON TESTS", "RETURNS"))
OUTPUT_CSV = os.path.join(CHAMELEON_RESULTS_FOLDER, "CAR_results.csv")

def extract_chords_from_xml(file_path):
    """Extracts chords from a MusicXML file and converts them to pitch class sets."""
    score = converter.parse(file_path)
    chord_dict = {}  # Key: (measure, beat), Value: Pitch Class Set
    
    for part in score.parts:
        for measure in part.getElementsByClass("Measure"):
            for element in measure.notes:
                if isinstance(element, chord.Chord):
                    pcs = tuple(sorted(element.pitchClasses))  # Normalize to pitch class set
                    chord_dict[(measure.number, element.offset)] = pcs
    
    return chord_dict

def compute_car(reference_file, chameleon_file):
    """Computes the Chord Accuracy Rate (CAR%) by comparing Chameleon's harmonization with the reference harmony."""

    # Extract chords from both files
    reference_chords = extract_chords_from_xml(reference_file)
    chameleon_chords = extract_chords_from_xml(chameleon_file)

    matched_chords = 0
    total_chords = len(reference_chords)

    print(f"\nProcessing {os.path.basename(chameleon_file)}")
    print(f"Total Chords in Reference: {total_chords}\n")

    for key, ref_chord in reference_chords.items():
        if key in chameleon_chords:
            cham_chord = chameleon_chords[key]
            if ref_chord == cham_chord:  # Compare Pitch Class Sets
                matched_chords += 1
            else:
                print(f"❌ Mismatch at Measure {key[0]}, Beat {key[1]}: Expected {ref_chord}, Got {cham_chord}")

    # Compute CAR%
    car_percentage = (matched_chords / total_chords) * 100 if total_chords > 0 else 0

    print(f"✅ Processed {os.path.basename(chameleon_file)} - CAR% = {car_percentage:.2f}%")
    print(f"Matched Chords: {matched_chords} / {total_chords}\n")
    
    return car_percentage


def process_all_chameleon_results():
    """Iterates through all XML files in the Chameleon results folder and computes CAR%."""
    results = []
    
    if not os.path.exists(CHAMELEON_RESULTS_FOLDER):
        raise FileNotFoundError(f"CHAMELEON_RESULTS_FOLDER not found: {CHAMELEON_RESULTS_FOLDER}")
    
    for filename in os.listdir(CHAMELEON_RESULTS_FOLDER):
        if filename.endswith(".xml"):
            file_path = os.path.join(CHAMELEON_RESULTS_FOLDER, filename)
            car_result = compute_car(REFERENCE_FILE, file_path)
            results.append([filename, car_result])
            print(f"Processed {filename}: CAR% = {car_result:.2f}%")
    
    # Save results to CSV
    df = pd.DataFrame(results, columns=["Filename", "CAR%"])
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Results saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    process_all_chameleon_results()
