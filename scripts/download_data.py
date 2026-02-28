import os
import requests
import json
import pandas as pd

# Provided data from the user
data = {
    "Receptor": ["GPR158", "GPR179", "GPR151", "GPR21", "GPR52", "GPR161", "GPR61", "GPRC5A", "GPR139", "GPR101", "GPR133", "GPR126", "GPR110", "GPR114", "GPR1", "GPR19", "GPR37", "GPR84", "GPR35", "GPR182"],
    "PDB ID": ["7XRA", "8I0U", "7XW9", "8W89", "6LI3", "7V96", "8G89", "8S8G", "7Z0E", "8T9R", "7T0S", "7W53", "7V68", "7XJR", "8W11", "7Y67", "8J92", "8I92", "8H9R", "8X88"],
    "Journal": ["Nature", "Nature", "Nature", "Nature", "Nature", "Nature", "Science", "Science", "Nature Comm", "Nature", "Nature", "Science", "Nature", "Nature", "Nature", "Nature", "Science", "Nature", "Science", "Nature"],
    "Key \"Mystery\"": ["Massive \"Orphan\" in the brain; contains a huge extracellular domain but unknown ligand.", "Critical for night vision; structure is known, but activation trigger is a guess.", "Highly expressed in habenular neurons; linked to nicotine addiction, yet \"ligand-less.\"", "Involved in insulin resistance; the binding pocket is \"pre-activated\" but empty.", "A major target for schizophrenia; structure shows a \"self-ligand\" (an internal loop), but natural trigger is unknown.", "Essential for Sonic Hedgehog signaling; how it functions without a ligand is debated.", "Linked to obesity; the structure shows an \"autoinhibitory\" stalk, but the real ligand is missing.", "A rare \"Class C\" orphan involved in lung cancer; binding mechanism remains speculative.", "Highly conserved in the brain; authors guess it binds amino acids, but no proof.", "Linked to gigantism; the extracellular part is huge, but what it \"grabs\" is a total mystery.", "An \"Adhesion\" GPCR; authors found it’s activated by mechanical force, but chemical ligands are unknown.", "Essential for nerve myelination; structural \"guesses\" focus on collagen, but it's unproven.", "Overexpressed in cancers; the \"GPS\" domain structure is solved, but the \"signal\" is not.", "Involved in immune response; authors propose \"tethered agonism,\" but the field is skeptical.", "Involved in metabolism; often \"guessed\" to be a chemerin receptor, but structural data is confusing.", "Linked to circadian rhythm and cancer; its structure is \"empty\" and awaiting an ML discovery.", "Parkin-associated endothelin-like receptor; ligand is highly controversial (Prosaposin vs. mystery).", "Pro-inflammatory orphan; authors see fatty acid-like pockets, but haven't \"nailed\" the best one.", "Highly sought-after for IBD; structure is known, but natural endogenous ligands are heavily debated.", "A \"decoy\" receptor; structural studies show it \"cleans\" the blood, but how it recognizes ligands is unclear."]
}

df = pd.DataFrame(data)
PDB_IDS = df["PDB ID"].tolist()

# Create directories to store data
os.makedirs("pdb_files", exist_ok=True)
os.makedirs("metadata", exist_ok=True)

print("Starting data download process...")

for pdb_id in PDB_IDS:
    print(f"Processing {pdb_id}...")

    # Download PDB file, try .pdb first, then .cif
    pdb_url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    cif_url = f"https://files.rcsb.org/download/{pdb_id}.cif"
    
    try:
        pdb_response = requests.get(pdb_url, timeout=30)
        if pdb_response.status_code == 200:
            with open(os.path.join("pdb_files", f"{pdb_id}.pdb"), "w") as f:
                f.write(pdb_response.text)
            print(f"  Downloaded {pdb_id}.pdb")
        else:
            print(f"  .pdb not found, trying .cif for {pdb_id}")
            cif_response = requests.get(cif_url, timeout=30)
            cif_response.raise_for_status()
            with open(os.path.join("pdb_files", f"{pdb_id}.cif"), "w") as f:
                f.write(cif_response.text)
            print(f"  Downloaded {pdb_id}.cif")
            
    except requests.exceptions.RequestException as e:
        print(f"  Failed to download structure file for {pdb_id}: {e}")

    # Download metadata
    metadata_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
    try:
        metadata_response = requests.get(metadata_url, timeout=30)
        metadata_response.raise_for_status()
        with open(os.path.join("metadata", f"{pdb_id}.json"), "w") as f:
            json.dump(metadata_response.json(), f, indent=2)
        print(f"  Downloaded metadata for {pdb_id}")
    except requests.exceptions.RequestException as e:
        print(f"  Failed to download metadata for {pdb_id}: {e}")
    except json.JSONDecodeError as e:
        print(f"  Failed to parse metadata for {pdb_id}: {e}")

# Save the initial table to a CSV file for reference
df.to_csv("orphan_gpcr_targets.csv", index=False)
print("\nSaved initial target list to orphan_gpcr_targets.csv")


print("\nAll downloads complete!")
