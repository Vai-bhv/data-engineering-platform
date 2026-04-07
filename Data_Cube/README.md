# Course Accreditation RDF Data Cube

This repository extracts a joined Fact_CourseAccreditation dataset from PostgreSQL, builds an RDF Data Cube with SKOS and SDMX interoperability, and validates it against core integrity constraints.

---

## System Requirements

- **Operating System:** Linux, macOS, or Windows  
- **Python:** Version 3.8 or higher  
- **PostgreSQL:** Access to `webik.ms.mff.cuni.cz:5432/ndbi046` with credentials:
  - **User:** `use_your_username`
  - **Password:** `use_your_password`
- **Python Packages:**  
  - `pandas`  
  - `sqlalchemy`  
  - `psycopg2-binary`  
  - `rdflib`

---

## Installation

1. **Create and activate a virtual environment:**

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

2.  **Install dependencies:**

pip install -r requirements.txt



## Script Overview

1. **export_from_db.py**
    Input : None (reads directly from the database).
    Output : dataset.csv — one row per accreditation fact, with provider and program labels.
    Purpose : Connects to the PostgreSQL server, runs a JOIN between the fact table and its two dimension tables, and writes out a clean CSV snapshot.
    Key Steps : 1- Uses SQLAlchemy (via create_engine) to connect with credentials.
                2- Executes this SQL:
                    SELECT
                        f.fact_id,
                        p.provider_id,
                        p.name AS provider_name,
                        r.program_id,
                        r.program_name,
                        f.participants_count
                    FROM "29471679_Fact_CourseAccreditation" f
                    JOIN "29471679_Dim_Provider" p  ON f.provider_id = p.provider_id
                    JOIN "29471679_Dim_Program"  r  ON f.program_id  = r.program_id;
                3- Loads result into a pandas DataFrame.
                4- Saves to dataset.csv in the repo root.


2. **data_cube.py**
    Input : dataset.csv (produced by export_from_db.py).
    Output : cube.ttl  — the complete RDF Data Cube in Turtle.
    Purpose : Reads dataset.csv and builds a fully‑featured RDF Data Cube, writing it in Turtle (cube.ttl).
    Features Implemented: 1- Custom Namespaces:
                                ex: for ontology terms (http://example.org/datacube/ontology#)
                                exr: for resource IRIs (http://example.org/datacube/resources/)
                          2- SKOS ConceptSchemes & Concepts:
                                Two schemes (providerScheme, programScheme) with skos:prefLabel.
                                One skos:Concept per unique provider & program, each skos:inScheme.
                          3- Dimensions & Measures:
                                Dimensions: ex:provider, ex:program (both qb:DimensionProperty).
                                Measure: ex:participantsCount (qb:MeasureProperty), sub‑property of SDMX obsValue.
                                Mapped dimensions to SDMX dimension concepts via rdfs:subPropertyOf.
                          4- Data Structure Definition (qb:DSD): 
                                Components for each dimension and the measure.
                          5- DataSet Metadata:
                                dcterms:publisher, issued, modified, title, license.
                          6- Observations:
                                One qb:Observation per row, linking dims & measure.
                          7- qb:Slice:
                                A slice resource selecting all observations for provider ID = 1.


3. **validate.py**
    Inputs: cube.ttl.
    Outputs: Console output: ✔ or ❌ with error details.
    Purpose: Performs a quick check that every qb:Observation in cube.ttl has at least one declared dimension triple and one declared measure triple.
    How It Works:   1- Loads cube.ttl into an RDFLib Graph.
                    2- Collects all properties typed qb:DimensionProperty and qb:MeasureProperty.
                    3- For each qb:Observation, verifies it uses at least one of each; reports any missing.

## USAGE WORKFLOW
# 1) Extract and join data to CSV
python export_from_db.py

# 2) Build the RDF Data Cube
python data_cube.py

# 3) Quick validation
python validate.py cube.ttl

