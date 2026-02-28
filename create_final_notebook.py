
import nbformat as nbf

# Create a new notebook object
nb = nbf.v4.new_notebook()

# The repository URL you provided
repo_url = "https://github.com/PorkRelatives/orphan-gpcr-meta-analysis.git"
repo_name = "orphan-gpcr-meta-analysis"

# -------------------
# Cell 1: Introduction (Markdown)
# -------------------
intro_text = f"""# Orphan GPCR Similarity Search Pipeline

This notebook executes the complete, end-to-end bioinformatics pipeline for predicting the function of 20 orphan GPCRs by finding their closest relatives in the Swiss-Prot database.

**Instructions:**
1.  Ensure your runtime is set to use a **T4 GPU** (`Runtime` -> `Change runtime type`).
2.  Run the cells sequentially.

**Pipeline Steps:**
1.  **Setup**: Clones the GitHub repository and installs all necessary dependencies.
2.  **Data Acquisition**: Downloads the Swiss-Prot database.
3.  **Embedding Computation (The Long Step)**: Computes ESM-2 embeddings for the entire Swiss-Prot database. **This will take many hours.**
4.  **Index & Search**: Builds a FAISS search index and finds the top hits for the 20 orphan GPCRs.
5.  **Results**: Displays the final, readable table of predictions."""
nb['cells'].append(nbf.v4.new_markdown_cell(intro_text))

# -------------------
# Cell 2: Step 1 - Setup and Cloning (Code)
# -------------------
code_setup = f"""# 1. Setup: Clone Repo and Install Dependencies

print(\"Cloning the GitHub repository...\")
!git clone {repo_url}

# Change directory into the repository
import os
os.chdir(repo_name)

print(\"Installing all necessary dependencies...\")
!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -q
!pip install fair-esm biopython requests faiss-cpu -q

print(\"\\nSetup complete. All dependencies are installed.\")"""
nb['cells'].append(nbf.v4.new_code_cell(code_setup))

# -------------------
# Cell 3: Step 2 - Data Acquisition (Code)
# -------------------
code_download = """# 2. Data Acquisition

print(\"Running script to download the Swiss-Prot database...\")
!python scripts/01_download_swissprot.py"""
nb['cells'].append(nbf.v4.new_code_cell(code_download))

# -------------------
# Cell 4: Step 3 - Compute Database Embeddings (Code)
# -------------------
code_compute = """# 3. Compute Database Embeddings (The Long Step)

print(\"\\nStarting the main computation. This will take many hours.\")
print(\"The script is resumable and will save checkpoints periodically.\")

!python scripts/02_compute_database_embeddings.py"""
nb['cells'].append(nbf.v4.new_code_cell(code_compute))

# -------------------
# Cell 5: Step 4 - Build Index (Code)
# -------------------
code_index = """# 4. Build the FAISS Search Index

print(\"\\nComputation complete. Building the FAISS index for efficient search...\")
!python scripts/03_build_search_index.py"""
nb['cells'].append(nbf.v4.new_code_cell(code_index))

# -------------------
# Cell 6: Step 5 - Find Top Hits and Display Results (Code)
# -------------------
code_results = """# 5. Find and Display Top Hits

print(\"\\nIndex built. Searching for the top hits for each orphan GPCR...\")
!python scripts/04_find_top_hits.py"""
nb['cells'].append(nbf.v4.new_code_cell(code_results))


# -------------------
# Write the notebook to a file
# -------------------
with open('Run_Similarity_Search_Pipeline.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Jupyter notebook 'Run_Similarity_Search_Pipeline.ipynb' created successfully.")

