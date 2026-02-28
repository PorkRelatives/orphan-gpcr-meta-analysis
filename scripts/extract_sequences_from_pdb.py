import os
from Bio.PDB import PDBParser, MMCIFParser
from Bio.PDB.PDBExceptions import PDBConstructionWarning
import warnings

warnings.simplefilter('ignore', PDBConstructionWarning)

PDB_FILES_DIR = "pdb_files"
FASTA_FILE = "sequences.fasta"

sequences = {}

def get_sequence(structure):
    sequence = ""
    for model in structure:
        for chain in model:
            for residue in chain:
                if "CA" in residue:
                    sequence += residue.get_resname()
    return sequence

for filename in os.listdir(PDB_FILES_DIR):
    pdb_id = filename.split('.')[0]
    filepath = os.path.join(PDB_FILES_DIR, filename)
    
    if pdb_id in sequences:
        continue

    try:
        if filename.endswith(".pdb"):
            parser = PDBParser()
            structure = parser.get_structure(pdb_id, filepath)
            
            for model in structure:
                for chain in model:
                    seq = ""
                    for residue in chain:
                        if residue.get_id()[0] == ' ':
                            seq += residue.get_resname()
                    if len(seq) > 0:
                        sequences[f"{pdb_id}_{chain.id}"] = seq

        elif filename.endswith(".cif"):
            parser = MMCIFParser()
            structure = parser.get_structure(pdb_id, filepath)
            for model in structure:
                for chain in model:
                    seq = ""
                    for residue in chain:
                         if residue.get_id()[0] == ' ':
                            seq += residue.get_resname()
                    if len(seq) > 0:
                        sequences[f"{pdb_id}_{chain.id}"] = seq

    except Exception as e:
        print(f"Error processing {filename}: {e}")

with open(FASTA_FILE, "w") as f:
    for seq_id, sequence in sequences.items():
        f.write(f">{seq_id}\n")
        f.write(f"{sequence}\n")

print(f"Extracted {len(sequences)} sequences to {FASTA_FILE}")
