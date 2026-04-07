# NDBI046 Provenance Generator

This repository contains a small Python utility that generates a PROV-O provenance document (TriG) describing:

- an **ETL workflow**,  
- a **data cube creation** step,  
- and a **visualization** step  

for the NDBI046 project, reusing all prior data and script artifacts.

---

## System requirements

- **Python** 3.8+  
- **rdflib** (for RDF graph building)  

---

## Installation

# create virtual enviornment
python3 -m venv env
source env/bin/activate

# Install dependencies
pip install -r requiremnets.txt

# Run the file 
python3 prov_qualified_etl_cube.py provenance_output.trig


## Files 

# prov_document.py

What it does
Builds an RDFLib graph using the PROV-O ontology (including qualifiedUsage and qualifiedAssociation) and emits it as TriG.

Inputs
None (uses hard-coded URIs to your data, scripts, visualizations, activities, agents).

Outputs
A TriG file capturing provenance, to the path you supply on the command line.

Explanation of prov_document.py
Namespaces - We declare six custom prefixes (data:, script:, vis:, res:, ns:) plus the standard prov:, foaf:, rdfs:, xsd:.

Entities
    Datasets (raw/transformed CSVs, JSON, final TriG)
    Scripts (extract.py, transform.py, etc.)
    Visualizations (PNG outputs)

Agents
    ns:GUPTAV (a prov:Person)
    ns:MFF_UK (a prov:Organization)
    ns:ApacheAirflow, ns:Python3 (both prov:SoftwareAgent)

Activities
    ns:ETLWorkflow
    ns:DataCubeCreation
    ns:VisualizationGeneration

Qualified terms
    For each activity we create blank-node prov:Usage and prov:Association instances
    We connect them to the activity with prov:qualifiedUsage and prov:qualifiedAssociation

Serialization: Run on the command-line, passing your desired output path (e.g. output/provenance.trig). The script writes valid TriG.

# Output file - provenance_output.trig

Prefix declarations - All of your custom namespaces (data:, script:, vis:, res:, ns:) plus the standard prov:, foaf:, rdfs: and xsd: are bound at the top of the file, so every URI in the triples is written as a readable CURIE.

Entities (prov:Entity)
    Raw data artifacts (data:akris_csv, data:rpss_json, etc.) with prov:atLocation or prov:wasGeneratedBy ns:ETLWorkflow.
    Transformed artifacts (data:akris_transformed_csv, data:joined_csv, …) all linked to the same ns:ETLWorkflow activity.
    Scripts (script:extract, script:transform, script:load, script:cube, script:validate, script:visualize) each typed as prov:Entity.
    Visualizations (vis:program_distribution_png, etc.) typed as prov:Entity and linked to ns:VisualizationGeneration.
    Final cube file (res:data_cube_trig) typed as prov:Entity and linked to ns:DataCubeCreation.

Agents (prov:Agent and sub-classes)
    ns:GUPTAV (a prov:Person) with FOAF properties.
    ns:MFF_UK (a prov:Organization) with FOAF name/homepage.
    ns:ApacheAirflow and ns:Python3 (both prov:SoftwareAgent) with FOAF names.

Activities (prov:Activity)
    ns:ETLWorkflow
        has prov:startedAtTime / prov:endedAtTime
        two qualified usages (one for the extract script, one for the raw CSV) via blank-nodes of type prov:Usage
        one qualified association tying ns:ApacheAirflow to the activity via a blank-node of type prov:Association

    ns:DataCubeCreation
        has its own time stamps
        one qualified usage (the cube_dataset.py script) and one association to ns:Python3

    ns:VisualizationGeneration
        likewise stamps, usage (the visualize.py script) and association to ns:Python3

Qualified terms - prov:qualifiedUsage and prov:qualifiedAssociation are used on each activity to attach extra metadata (prov:hadRole, prov:agent, prov:hadPlan) to the blank-nodes.

TriG syntax
    Although there’s only a single default graph here, it’s serialized with .trig so you can later extend it with named sub-graphs if you wish.
    Any RDF‐aware tool (RDFLib, Apache Jena, TopBraid, etc.) can load provenance.trig and validate it against PROV-O.

In short the output file is your complete, valid PROV-O provenance record of the three main steps—ETL, cube creation, visualizations—linking Entities, Activities, and Agents, and demonstrating qualifiedUsage and qualifiedAssociation.