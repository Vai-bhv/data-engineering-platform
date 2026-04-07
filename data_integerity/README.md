# Secure DCAT Catalog for Course Accreditation

This repository extends the DCAT catalog (homework 5) to add SPDX‐checksum integrity, creates a CSR for a signing certificate, signs the catalog, and publishes all data fragments.

## Structure & Usage

### 1. Create Virtual Enviornment
python3 -m venv venv
source venv/bin/activate

### 2. Install requirements 
pip install -r requirements.txt

### 3. Generate CSR  
Run sh csr.sh CZ "Charles University" ksi.mff.cuni.cz 
Outputs: private.key (keep private!) and data-catalog.csr

### 4. Get certificate.crt
Send that data-catalog.csr to authorized personnal to recieve certificate.crt and place it in the directory.

### 5. Extend DCAT catalog with SHA-256 checksums
python3 dcat_catalog_secure.py \
  dcat_catalog.ttl (assignment 5)\
  dataset.csv (assignment3)\
  cube.ttl (assignment3)\
  data-catalog.ttl (output file)

### 6. Sign the catalog
sh sign_cat.sh data-catalog.ttl data-catalog.sha256.sign
Uses private.key + SHA-256 + base64 → data-catalog.sha256.sign

### 7. Publish
Upload all files (except private.key) the web server.
Ensure index.html links to:
    certificate.crt
    data-catalog.ttl
    data-catalog.sha256.sign
    dataset.csv
    cube.ttl


## Files 

### 1. csr.sh
What it does
    Generates a 2048-bit RSA private key (if one doesn’t already exist)
    Creates a Certificate Signing Request (CSR) using that key
Inputs
    Command-line args:
        <C> – Country Name (two-letter code, e.g. CZ)
        <O> – Organization Name (e.g. "Charles University")
        <CN> – Common Name (e.g. ksi.mff.cuni.cz)
Outputs
    private.key – your RSA private key (keep this local!)
    data-catalog.csr – the CSR to send for signing


### 2. sign_cat.sh
What it does
    Computes a SHA-256 hash of your extended catalog TTL
    Signs that hash with your RSA private key
    Encodes the binary signature in Base64
Inputs
    Command-line args:
        <data-catalog.ttl> – the TTL file you want to sign
        <output-signature> – filename for the Base64 signature (e.g. data-catalog.sha256.sign)
File:
    private.key – your RSA private key
Outputs : <output-signature> – a Base64-encoded SHA-256 signature of the TTL (e.g. data-catalog.sha256.sign)

### 3. dcat_catalog_secure.py
What it does
    Loads your original DCAT catalog (Turtle)
    Computes SHA-256 digests of your CSV and TTL distributions
    Injects two spdx:checksum blank-node triples into the graph
    Writes out a new Turtle file
Inputs
    dcat_catalog.ttl – the original DCAT catalog (assignment 5)
    dataset.csv – CSV distribution of the fact table (assignment 3)
    cube.ttl – RDF Data Cube distribution (assignment 3)
Outputs
    data-catalog.ttl – the extended DCAT catalog with SPDX checksums

