import pandas as pd

# Define experiment dimensions
melodies = ["Rebetiko", "Bach Chorale", "Film Theme"]
all_notes_important = [True, False]
styles = ["BachChorales", "Jazz", "Kostka-Payne", "WholeTone", "Epirus", "Fauxbourdon", "ModalChorales", "Organum"]
modes_per_style = {
    "BachChorales": ["[0 2 4 5 7 9 11]", "[0 2 3 5 7 8 10]"],
    "Jazz": ["[0 2 4 5 7 9 11]", "[0 2 3 5 7 8 10]"],
    "Kostka-Payne": ["[0 2 4 5 7 9 11]", "[0 2 3 5 7 8 10]"],
    "WholeTone": ["[0 2 4 6 8 10]"],
    "Epirus": ["[0 3 5 7 10]", "[0 2 3 5 7 10]", "[0 2 5 7 10]", "[0 2 3 5 10]"],
    "Fauxbourdon": ["[0 2 4 5 7 9 11]", "[0 2 3 5 7 9 10]", "[0 1 3 5 7 8 10]"],
    "ModalChorales": ["[0 2 4 6 7 9 11]", "[0 2 3 5 7 9 10]", "[0 2 4 5 7 9 11]", "[0 1 3 5 7 8 10]", "[0 2 4 5 7 9 10]"],
    "Organum": ["[0 2 3 5 7 10]"]
}
blending = [False, True]  # No Blend, Blend
vl_options = ["NoVL", "BBVL"]  # No Voice Leading, Bass-Based Voice Leading

# Generate test cases
rows = []
for melody in melodies:
    for all_notes in all_notes_important:
        for style in styles:
            for mode in modes_per_style[style]:
                for blend in blending:
                    if blend:
                        for blend_style in styles:
                            if blend_style != style:
                                for blend_mode in modes_per_style[blend_style]:
                                    for vl in vl_options:
                                        rows.append([melody, all_notes, style, mode, blend, blend_style, blend_mode, vl, "", "", ""])
                    else:
                        for vl in vl_options:
                            rows.append([melody, all_notes, style, mode, blend, "None", "None", vl, "", "", ""])

# Create DataFrame
columns = ["Melody", "allNotesImportant", "Style", "Mode", "Blend", "Blended Style", "Blended Mode", "VL", "CAR (%)", "CCI (%)", "DR (%)"]
df = pd.DataFrame(rows, columns=columns)

# Save to CSV
output_path = "Chameleon_Experiment_Results.csv"
df.to_csv(output_path, index=False)
print(f"Dataset successfully saved as {output_path}. You can now open it in Excel or any CSV viewer.")