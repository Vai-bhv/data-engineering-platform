# DCAT Data Catalog Metadata

This project creates a DCAT (Data Catalog Vocabulary) description for a dataset based on the Course Accreditation fact table and its RDF Data Cube.
It also executes two meaningful SPARQL queries over the generated catalog.


## System Requirements

- Python 3.8+
- rdflib library


## Installation Instructions
1. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate

2. Install required libraries:
    pip install ir requirements.txt

## Description of Script Files

1.  dcat_catalog.py

Purpose: Generates a DCAT catalog (catalog.ttl) describing:
    dcat:Catalog resource containing:
        One dcat:Dataset
            Two dcat:Distribution resources:
                The original CSV (fact table export)
                The RDF Data Cube (Turtle format)
Inputs: No external input files needed. All RDF data is created inside the script itself.
Outputs: catalog.ttl – A valid RDF Turtle file that includes:
    Technical metadata (access URLs, file types, media types, etc.)
    Provenance metadata (creator, issued date, contact points, attribution)
    Domain metadata (keywords, themes, temporal and spatial coverage)
    Business metadata (license, access rights, update frequency)
Usage Example: python3 dcat_catalog.py catalog.ttl
Summary of metadata created:
    Technical: accessService, accessURL, downloadURL, byteSize, mediaType, format, endpointDescription, endpointURL
    Provenance: contactPoint, creator, issued, modified, created, wasGeneratedBy, qualifiedAttribution
    Domain: title, description, keywords, themes, spatial, temporal coverage, spatialResolutionInMeters, temporalResolution
    Business: accrualPeriodicity, accessRights, license

2. query_catalog.py
Purpose: Executes two SPARQL queries over the generated catalog.
Inputs: catalog.ttl (generated from dcat_catalog.py)
Outputs: Console output showing:
    Query 1: Temporal coverage of the dataset (startDate → endDate)
    Query 2: List of all distributions, their byteSize and file format
Usage Example: python3 query_catalog.py catalog.ttl
Summary of SPARQL Queries: 
Temporal Coverage Query: Retrieves the starting and ending dates of the dataset's validity.
Distribution Details Query: Lists each distribution’s file size (byteSize) and file format (format)

3. Generated Output Files
catalog.ttl: RDF Turtle file containing the full DCAT description of the dataset, distributions, and metadata.

