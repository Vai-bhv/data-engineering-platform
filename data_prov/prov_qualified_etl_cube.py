#!/usr/bin/env python3
"""
Provenance document generator for ETL, Data Cube creation, and Visualizations
using PROV-O with qualified and expanded terms.
"""
import sys
import logging
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, XSD, PROV, FOAF

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Namespaces
NS = Namespace("https://ksi.mff.cuni.cz/~guptava/232-NDBI046/prov#")
DATA = Namespace("https://ksi.mff.cuni.cz/~guptava/232-NDBI046/data/")
SCRIPT = Namespace("https://ksi.mff.cuni.cz/~guptava/232-NDBI046/scripts/")
VIS = Namespace("https://ksi.mff.cuni.cz/~guptava/232-NDBI046/visualizations/")
RES = Namespace("https://ksi.mff.cuni.cz/~guptava/232-NDBI046/resources/")


def create_prov_data() -> Graph:
    """
    Build the provenance graph and return it.
    """
    g = Graph()

    # Bind common prefixes
    g.bind("prov", PROV)
    g.bind("foaf", FOAF)
    g.bind("xsd", XSD)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("ns", NS)
    g.bind("data", DATA)
    g.bind("script", SCRIPT)
    g.bind("vis", VIS)
    g.bind("res", RES)

    create_entities(g)
    create_agents(g)
    create_activities(g)

    return g


def create_entities(g: Graph) -> None:
    """
    Declare all provenance Entities: datasets, scripts, and visual artifacts.
    """
    # Raw datasets
    g.add((DATA.akris_csv, RDF.type, PROV.Entity))
    g.add((DATA.akris_csv, RDFS.label, Literal("Raw accreditation CSV", lang="en")))
    g.add((DATA.akris_csv, PROV.atLocation, Literal("data/raw/akris.csv")))

    g.add((DATA.social_csv, RDF.type, PROV.Entity))
    g.add((DATA.social_csv, RDFS.label, Literal("Raw social service CSV", lang="en")))
    g.add((DATA.social_csv, PROV.atLocation, Literal("data/raw/social_service.csv")))

    g.add((DATA.rpss_json, RDF.type, PROV.Entity))
    g.add((DATA.rpss_json, RDFS.label, Literal("Raw RPSS JSON", lang="en")))
    g.add((DATA.rpss_json, PROV.atLocation, Literal("data/raw/rpss.json")))

    # Transformed datasets
    g.add((DATA.akris_transformed_csv, RDF.type, PROV.Entity))
    g.add((DATA.akris_transformed_csv, RDFS.label, Literal("Transformed accreditation CSV", lang="en")))
    g.add((DATA.social_transformed_csv, RDF.type, PROV.Entity))
    g.add((DATA.social_transformed_csv, RDFS.label, Literal("Transformed social service CSV", lang="en")))
    g.add((DATA.rpss_transformed_csv, RDF.type, PROV.Entity))
    g.add((DATA.rpss_transformed_csv, RDFS.label, Literal("Transformed RPSS CSV", lang="en")))
    g.add((DATA.joined_csv, RDF.type, PROV.Entity))
    g.add((DATA.joined_csv, RDFS.label, Literal("Joined dataset CSV", lang="en")))

    # Data cube output
    g.add((RES.data_cube_trig, RDF.type, PROV.Entity))
    g.add((RES.data_cube_trig, RDFS.label, Literal("RDF Data Cube TriG file", lang="en")))

    # Visualization outputs
    g.add((VIS.program_distribution_png, RDF.type, PROV.Entity))
    g.add((VIS.program_distribution_png, RDFS.label, Literal("Program distribution bar chart", lang="en")))
    g.add((VIS.social_stats_png, RDF.type, PROV.Entity))
    g.add((VIS.social_stats_png, RDFS.label, Literal("Social service statistics bar chart", lang="en")))
    g.add((VIS.rpss_distribution_png, RDF.type, PROV.Entity))
    g.add((VIS.rpss_distribution_png, RDFS.label, Literal("RPSS distribution line chart", lang="en")))

    # Script artifacts
    g.add((SCRIPT.extract, RDF.type, PROV.Entity))
    g.add((SCRIPT.extract, RDFS.label, Literal("extract.py script", lang="en")))
    g.add((SCRIPT.transform, RDF.type, PROV.Entity))
    g.add((SCRIPT.transform, RDFS.label, Literal("transform.py script", lang="en")))
    g.add((SCRIPT.load, RDF.type, PROV.Entity))
    g.add((SCRIPT.load, RDFS.label, Literal("load.py script", lang="en")))
    g.add((SCRIPT.cube, RDF.type, PROV.Entity))
    g.add((SCRIPT.cube, RDFS.label, Literal("cube_dataset.py script", lang="en")))
    g.add((SCRIPT.visualize, RDF.type, PROV.Entity))
    g.add((SCRIPT.visualize, RDFS.label, Literal("visualize.py script", lang="en")))
    g.add((SCRIPT.validate, RDF.type, PROV.Entity))
    g.add((SCRIPT.validate, RDFS.label, Literal("check-well-formed.py script", lang="en")))


def create_agents(g: Graph) -> None:
    """
    Declare provenance Agents: person, organization, software.
    """
    # Author
    g.add((NS.GUPTAV, RDF.type, PROV.Person))
    g.add((NS.GUPTAV, FOAF.givenName, Literal("Vaibhav Gupta, Ph.D.", lang="cs")))
    g.add((NS.GUPTAV, FOAF.mbox, URIRef("mailto:vaibhavgupta853@matfyz.cuni.cz")))
    g.add((NS.GUPTAV, FOAF.homepage, Literal("https://ksi.mff.cuni.cz/~guptava/", datatype=XSD.anyURI)))

    # Organization
    g.add((NS.MFF_UK, RDF.type, PROV.Organization))
    g.add((NS.MFF_UK, FOAF.name, Literal("Mathematics & Physics Faculty, Charles University", lang="en")))
    g.add((NS.MFF_UK, FOAF.homepage, Literal("https://www.mff.cuni.cz/", datatype=XSD.anyURI)))

    # Apache Airflow
    g.add((NS.ApacheAirflow, RDF.type, PROV.SoftwareAgent))
    g.add((NS.ApacheAirflow, FOAF.name, Literal("Apache Airflow", lang="en")))

    # Python runtime
    g.add((NS.Python3, RDF.type, PROV.SoftwareAgent))
    g.add((NS.Python3, FOAF.name, Literal("Python 3", lang="en")))


def create_activities(g: Graph) -> None:
    """
    Declare ETL, Data Cube creation, and Visualization activities,
    including qualifiedUsage and qualifiedAssociation.
    """
    # --- ETL Workflow Activity ---
    etl = NS.ETLWorkflow
    g.add((etl, RDF.type, PROV.Activity))
    g.add((etl, PROV.startedAtTime, Literal("2024-04-01T00:00:00", datatype=XSD.dateTime)))
    g.add((etl, PROV.endedAtTime, Literal("2024-04-01T00:10:00", datatype=XSD.dateTime)))

    # qualifiedUsage of raw CSV and script
    usage_raw = BNode()
    g.add((usage_raw, RDF.type, PROV.Usage))
    g.add((usage_raw, PROV.entity, DATA.akris_csv))
    g.add((usage_raw, PROV.hadRole, Literal("raw dataset", lang="en")))
    g.add((etl, PROV.qualifiedUsage, usage_raw))

    usage_script = BNode()
    g.add((usage_script, RDF.type, PROV.Usage))
    g.add((usage_script, PROV.entity, SCRIPT.extract))
    g.add((usage_script, PROV.hadRole, Literal("extract script", lang="en")))
    g.add((etl, PROV.qualifiedUsage, usage_script))

    # qualifiedAssociation with Apache Airflow
    assoc = BNode()
    g.add((assoc, RDF.type, PROV.Association))
    g.add((assoc, PROV.agent, NS.ApacheAirflow))
    g.add((assoc, PROV.hadPlan, SCRIPT.extract))
    g.add((etl, PROV.qualifiedAssociation, assoc))

    # --- Data Cube Creation Activity ---
    cube_act = NS.DataCubeCreation
    g.add((cube_act, RDF.type, PROV.Activity))
    g.add((cube_act, PROV.startedAtTime, Literal("2024-04-01T00:10:00", datatype=XSD.dateTime)))
    g.add((cube_act, PROV.endedAtTime, Literal("2024-04-01T00:12:00", datatype=XSD.dateTime)))

    usage_cube_script = BNode()
    g.add((usage_cube_script, RDF.type, PROV.Usage))
    g.add((usage_cube_script, PROV.entity, SCRIPT.cube))
    g.add((usage_cube_script, PROV.hadRole, Literal("data cube script", lang="en")))
    g.add((cube_act, PROV.qualifiedUsage, usage_cube_script))

    assoc_cube = BNode()
    g.add((assoc_cube, RDF.type, PROV.Association))
    g.add((assoc_cube, PROV.agent, NS.Python3))
    g.add((assoc_cube, PROV.hadPlan, SCRIPT.cube))
    g.add((cube_act, PROV.qualifiedAssociation, assoc_cube))

    # --- Visualization Activity ---
    viz = NS.VisualizationGeneration
    g.add((viz, RDF.type, PROV.Activity))
    g.add((viz, PROV.startedAtTime, Literal("2024-04-01T00:12:00", datatype=XSD.dateTime)))
    g.add((viz, PROV.endedAtTime, Literal("2024-04-01T00:15:00", datatype=XSD.dateTime)))

    usage_viz_script = BNode()
    g.add((usage_viz_script, RDF.type, PROV.Usage))
    g.add((usage_viz_script, PROV.entity, SCRIPT.visualize))
    g.add((usage_viz_script, PROV.hadRole, Literal("visualization script", lang="en")))
    g.add((viz, PROV.qualifiedUsage, usage_viz_script))

    assoc_viz = BNode()
    g.add((assoc_viz, RDF.type, PROV.Association))
    g.add((assoc_viz, PROV.agent, NS.Python3))
    g.add((assoc_viz, PROV.hadPlan, SCRIPT.visualize))
    g.add((viz, PROV.qualifiedAssociation, assoc_viz))

    # Generated outputs
    for entity, activity in [
        (DATA.akris_transformed_csv, etl),
        (DATA.social_transformed_csv, etl),
        (DATA.rpss_transformed_csv, etl),
        (DATA.joined_csv, etl),
        (RES.data_cube_trig, cube_act),
        (VIS.program_distribution_png, viz),
        (VIS.social_stats_png, viz),
        (VIS.rpss_distribution_png, viz)
    ]:
        g.add((entity, RDF.type, PROV.Entity))
        g.add((entity, PROV.wasGeneratedBy, activity))


def main():
    if len(sys.argv) != 2:
        logging.error("Usage: python prov_qualified_etl_cube.py <output_file.trig>")
        sys.exit(1)
    g = create_prov_data()
    g.serialize(destination=sys.argv[1], format="trig")
    logging.info(f"Provenance document written to {sys.argv[1]}")


if __name__ == "__main__":
    main()
