import torch
import esm
import os
from Bio import SeqIO
import time

# --------------------------------------------------------------------------------
# This script computes the ESM-2 embeddings for the entire Swiss-Prot database.
#
# WARNING: This is an extremely computationally intensive task.
# - It requires a machine with a powerful NVIDIA GPU and sufficient VRAM.
# - It will take MANY HOURS or even DAYS to complete.
# - It will generate a very large output file (many gigabytes).
#
# This script is designed to be resumable. If it is stopped, it will reload
# the already computed embeddings and continue where it left off.
# --------------------------------------------------------------------------------

# --- Configuration ---
FASTA_FILE = "uniprot_sprot.fasta"
EMBEDDINGS_OUTPUT_FILE = "swissprot_embeddings.pt"
CHECKPOINT_INTERVAL = 1000  # Save progress every 1000 sequences

# --- GPU and Model Setup ---

if not torch.cuda.is_available():
    raise RuntimeError("This script requires a CUDA-enabled GPU. Please run on a suitable machine.")

print("Loading ESM-2 model...")
model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
model.eval()  # Disable dropout
model = model.cuda() # Move model to GPU
batch_converter = alphabet.get_batch_converter()
print("Model loaded successfully to GPU.")


# --- Load Existing Embeddings (for resuming) ---

if os.path.exists(EMBEDDINGS_OUTPUT_FILE):
    print(f"Loading existing embeddings from {EMBEDDINGS_OUTPUT_FILE} to resume...")
    embeddings = torch.load(EMBEDDINGS_OUTPUT_FILE)
    processed_ids = set(embeddings.keys())
    print(f"Found {len(processed_ids)} already processed sequences.")
else:
    embeddings = {}
    processed_ids = set()


# --- Main Processing Loop ---

print(f"Starting embedding generation for sequences in {FASTA_FILE}...")
start_time = time.time()
sequences_processed_this_run = 0

for i, seq_record in enumerate(SeqIO.parse(FASTA_FILE, "fasta")):
    seq_id = seq_record.id
    
    # Skip sequences that have already been processed
    if seq_id in processed_ids:
        continue

    # Prepare the data for the model
    sequence = str(seq_record.seq)
    data = [(seq_id, sequence)]
    batch_labels, batch_strs, batch_tokens = batch_converter(data)
    batch_tokens = batch_tokens.cuda()

    # Extract embeddings
    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33])
    token_representations = results["representations"][33]

    # Generate the sequence representation (and move to CPU for storage)
    sequence_representation = token_representations[0, 1 : len(sequence) + 1].mean(0).to("cpu")
    embeddings[seq_id] = sequence_representation
    sequences_processed_this_run += 1

    # --- Checkpointing Logic ---
    if sequences_processed_this_run % CHECKPOINT_INTERVAL == 0:
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"  - Processed {sequences_processed_this_run} new sequences in {elapsed:.2f}s. Total processed: {len(embeddings)}. Saving checkpoint...")
        torch.save(embeddings, EMBEDDINGS_OUTPUT_FILE)
        start_time = time.time() # Reset timer for next batch

# --- Final Save ---
print("\nEmbedding generation complete.")
print(f"Saving final embeddings to {EMBEDDINGS_OUTPUT_FILE}...")
torch.save(embeddings, EMBEDDINGS_OUTPUT_FILE)
print("All done.")

