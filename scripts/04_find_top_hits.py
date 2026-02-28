import torch
import faiss
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------------
# This is the final script in the pipeline.
#
# It takes the embeddings for our 20 orphan GPCRs and uses the pre-built
# FAISS index to find the top 5 most similar proteins from the entire
# Swiss-Prot database for each orphan.
#
# The output of this script is the final, human-readable table of predictions.
# --------------------------------------------------------------------------------

# --- Configuration ---
ORPHAN_EMBEDDINGS_FILE = "embeddings.pt"
INDEX_FILE = "swissprot_faiss.index"
ID_MAP_FILE = "swissprot_id_map.pt"
TOP_K = 5  # Number of top hits to find for each orphan

# --- Load All Necessary Data ---

print("Loading all necessary files...")

# Load the FAISS index
index = faiss.read_index(INDEX_FILE)

# Load the ID map that links index positions to UniProt IDs
id_map = torch.load(ID_MAP_FILE)

# Load our orphan GPCR embeddings
orphan_embeddings_data = torch.load(ORPHAN_EMBEDDINGS_FILE)

# Load the metadata to get the proper names
target_df = pd.read_csv("target20.csv", sep='\t', header=None, names=['Receptor', 'PDB_ID', 'DOI', 'Year', 'Key_Mystery'])
receptor_names = {f"{row['PDB_ID']}_A": row['Receptor'] for index, row in target_df.iterrows()}

print("Data loaded. Starting search...")

# --- Perform the Search ---

results = {}

# Iterate through each of our orphan GPCRs
for orphan_key, orphan_embedding in orphan_embeddings_data.items():
    if orphan_key not in receptor_names:
        continue

    # Prepare the query vector
    query_vector = orphan_embedding.numpy().reshape(1, -1).astype('float32')

    # Perform the search against the index
    # D = distances, I = indices of the top K hits
    distances, indices = index.search(query_vector, TOP_K)

    # Get the UniProt IDs of the top hits
    top_hits = [id_map[i] for i in indices[0]]
    
    # Store the results
    receptor_name = receptor_names[orphan_key]
    results[receptor_name] = top_hits


# --- Print Results in a Readable Table ---

print("\n--- AI-Predicted Functional Relatives ---")
print("{:<15} | {:<25} | {:<70}".format("Orphan Receptor", "Top Predicted Relative", "UniProt URL"))
print("-" * 115)

for receptor, hits in results.items():
    top_hit_id = hits[0] # For simplicity, we'll focus on the single best hit
    # The ID format from UniProt is like 'sp|P0C6S8|..._HUMAN', we just need the P0C6S8 part
    accession_id = top_hit_id.split('|')[1]
    url = f"https://www.uniprot.org/uniprot/{accession_id}"
    
    print("{:<15} | {:<25} | {:<70}".format(receptor, accession_id, url))

print("\nSearch complete.")

