import requests
import gzip
import os

# -------------------------------------------------------------------
# This script downloads the complete Swiss-Prot annotated protein database
# from the UniProt FTP server.
#
# Swiss-Prot is a high-quality, manually annotated, and non-redundant
# protein sequence database.
# -------------------------------------------------------------------

# URL for the Swiss-Prot database in FASTA format
url = "https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz"

# Define file paths
output_gz_file = "uniprot_sprot.fasta.gz"
output_fasta_file = "uniprot_sprot.fasta"

print(f"Downloading Swiss-Prot database from {url}...")

# Download the file
try:
    response = requests.get(url, stream=True)
    response.raise_for_status() # Raise an exception for bad status codes

    with open(output_gz_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Successfully downloaded {output_gz_file}.")

except requests.exceptions.RequestException as e:
    print(f"Error downloading file: {e}")
    exit()

# Decompress the file
print(f"Decompressing {output_gz_file}...")
try:
    with gzip.open(output_gz_file, 'rb') as f_in:
        with open(output_fasta_file, 'wb') as f_out:
            f_out.write(f_in.read())
    print(f"Successfully decompressed to {output_fasta_file}.")

    # Clean up the compressed file
    os.remove(output_gz_file)
    print(f"Removed temporary file: {output_gz_file}")

except Exception as e:
    print(f"Error decompressing file: {e}")
    exit()

print("\nSwiss-Prot database is ready for processing.")

