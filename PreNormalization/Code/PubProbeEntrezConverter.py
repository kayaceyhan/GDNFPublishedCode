import pandas as pd
import os

# Function to dynamically find the header row index
def find_header_row(file_path):
    """Reads a file line-by-line to find the index of the header row ('FEATURES')."""
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if line.startswith('FEATURES'):
                return i
    return 0

# Define paths
input_folder = '/Users/kayaceyhan/Downloads/Pubs_TXT_Array/' 
output_folder = '/Users/kayaceyhan/Downloads/Nonrounded_Final_Pub_New_Entrez_Arrays/'
probe_to_entrez = pd.read_csv('/Users/kayaceyhan/Downloads/015421_D_AA_20231107.csv')

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Loop through all files
for filename in os.listdir(input_folder):
    if filename.endswith('.txt'):
        file_path = os.path.join(input_folder, filename)

        # 1. Dynamically find the header row index
        header_row_index = find_header_row(file_path)

        # 2. Read the current file
        try:
            g_c_v_data = pd.read_csv(
                file_path,
                sep='\t',
                skiprows=header_row_index,
                header=0,
                skip_blank_lines=True,
                low_memory=False,       # <--- FIX 1: Solves the DtypeWarning
                on_bad_lines='skip'     # <--- FIX 2: Solves the ParserError (skips malformed rows)
            )
        except Exception as e:
            print(f"Skipping {filename} due to read error: {e}")
            continue
        
        # Merge data on ProbeName
        merged_data = g_c_v_data.merge(
            probe_to_entrez,
            how='left',
            left_on='ProbeName',
            right_on='ProbeID',
        )

        # Conversion logic
        merged_data['EntrezName'] = merged_data.apply(
            lambda row: row['EntrezGeneID'] if pd.notna(row['EntrezGeneID']) else row['ProbeName'],
            axis=1
        )

        # Cleanup columns
        merged_data = merged_data.drop(columns=['ProbeID', 'EntrezGeneID'])

        # Define output path
        output_filename = filename.replace('.txt', '.csv')
        output_path = os.path.join(output_folder, f"Nentrez_{output_filename}")

        # Save
        merged_data.to_csv(output_path, index=False)

        print(f"File saved to {output_path}")