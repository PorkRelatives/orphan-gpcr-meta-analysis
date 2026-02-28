import torch
import numpy as np
import faiss  # A library for efficient similarity search

# --------------------------------------------------------------------------------
# This script builds a FAISS index from the computed Swiss-Prot embeddings.
#
# FAISS (Facebook AI Similarity Search) is a library that allows for incredibly
# fast searching over massive sets of high-dimensional vectors.
#
# This index is what allows us to find the top hits for our orphans in seconds,
# rather than hours.
# --------------------------------------------------------------------------------

# --- Configuration ---
EMBEDDINGS_FILE = "swissprot_embeddings.pt"
INDEX_FILE = "swissprot_faiss.index"
ID_MAP_FILE = "swissprot_id_map.pt"

# --- Load Data ---
print(f"Loading embeddings from {EMBEDDINGS_FILE}...")
embeddings_data = torch.load(EMBEDDINGS_FILE)

# --- Prepare Data for FAISS ---

# FAISS needs a specific data structure: a NumPy matrix of the vectors
# and a list to map the index back to the UniProt ID.
id_map = list(embeddings_data.keys())
embedding_matrix = np.array([embeddings_data[id].numpy() for id in id_map], dtype='float32')

# The dimension of our vectors (should be 1280 for ESM-2)
dimension = embedding_matrix.shape[1]

print(f"Building FAISS index for {len(id_map)} proteins with dimension {dimension}...")

# --- Build the FAISS Index ---

# We use a simple IndexFlatL2 index. For even larger datasets, more complex
# indices like IndexIVFFlat could be used, but this is a good starting point.
index = faiss.IndexFlatL2(dimension)

# Add all the vectors to the index
index.add(embedding_matrix)

print(f"Index built successfully. Total vectors in index: {index.ntotal}")

# --- Save the Index and ID Map ---

print(f"Saving FAISS index to {INDEX_FILE}...")
faiss.write_index(index, INDEX_FILE)

print(f"Saving ID map to {ID_MAP_FILE}...")
torch.save(id_map, ID_MAP_FILE)

print("\nIndexing complete. The database is now ready for searching.")

