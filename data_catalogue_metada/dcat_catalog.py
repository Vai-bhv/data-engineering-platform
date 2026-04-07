#!/usr/bin/env python3
# dcat_catalog.py
# Generates DCAT catalog with 1 dataset and 2 distributions

import sys
import logging
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, DCAT, DCTERMS, FOAF, PROV, XSD

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Base namespace and authority vocabularies
BASE    = Namespace("https://ksi.mff.cuni.cz/~guptava/232-NDBI046/resources#")
FREQ    = Namespace("https://publications.europa.eu/resource/distribution/frequency/rdf/skos_core/")
CTYPE   = Namespace("https://publications.europa.eu/resource/distribution/file-type/rdf/skos_core/filetypes-skos.rdf#")
COUNTRY = Namespace("https://publications.europa.eu/resource/distribution/country/rdf/skos_core/countries-skos.rdf#")
EUROVOC = Namespace("http://publications.europa.eu/resource/dataset/eurovoc/")

def create_catalog():
    g = Graph()

    # Bind prefixes
    g.bind("base", BASE)
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    g.bind("foaf", FOAF)
    g.bind("prov", PROV)
    g.bind("xsd", XSD)
    g.bind("freq", FREQ)
    g.bind("filetype", CTYPE)
    g.bind("country", COUNTRY)
    g.bind("eurovoc", EUROVOC)

    # Catalog
    catalog = BASE.Catalog
    g.add((catalog, RDF.type, DCAT.Catalog))

    # Dataset
    dataset = BASE.CourseAccreditationDataset
    g.add((catalog, DCAT.dataset, dataset))
    g.add((dataset, RDF.type, DCAT.Dataset))

    # Technical metadata
    service = BASE.SPARQLEndpoint
    g.add((dataset, DCAT.accessService, service))
    g.add((service, RDF.type, DCAT.DataService))
    g.add((service, DCAT.endpointURL, URIRef("https://example.org/sparql")))
    g.add((service, DCAT.endpointDescription, Literal("SPARQL endpoint for course accreditation", lang="en")))

    # Provenance metadata
    contact = BASE.ContactPoint
    g.add((dataset, DCAT.contactPoint, contact))
    g.add((contact, RDF.type, FOAF.Person))
    g.add((contact, FOAF.mbox, URIRef("mailto:vaibhavgupta853@matfyz.cuni.cz")))

    g.add((dataset, DCTERMS.creator, BASE.GUPTAV))
    g.add((dataset, DCTERMS.created, Literal("2025-04-17", datatype=XSD.date)))
    g.add((dataset, DCTERMS.issued, Literal("2025-04-17T10:00:00", datatype=XSD.dateTime)))
    g.add((dataset, DCTERMS.modified, Literal("2025-04-17T12:00:00", datatype=XSD.dateTime)))
    g.add((dataset, PROV.wasGeneratedBy, BASE.ETLWorkflow))

    attribution = BNode()
    g.add((dataset, PROV.qualifiedAttribution, attribution))
    g.add((attribution, RDF.type, PROV.Attribution))
    g.add((attribution, PROV.agent, BASE.GUPTAV))
    g.add((attribution, PROV.hadRole, Literal("creator", lang="en")))

    # Domain metadata
    g.add((dataset, DCTERMS.title, Literal("Course Accreditation Dataset and RDF Data Cube", lang="en")))
    g.add((dataset, DCTERMS.description, Literal("Dataset and Cube about course accreditations in the Czech Republic.", lang="en")))
    
    for kw in ["education", "accreditation", "Czech Republic"]:
        g.add((dataset, DCAT.keyword, Literal(kw, lang="en")))

    for th in ["1158", "4259", "7816"]:
        g.add((dataset, DCAT.theme, EUROVOC[th]))

    g.add((dataset, DCTERMS.spatial, COUNTRY["CZE"]))

    period = BNode()
    g.add((dataset, DCTERMS.temporal, period))
    g.add((period, RDF.type, DCTERMS.PeriodOfTime))
    g.add((period, DCAT.startDate, Literal("2024-01-01", datatype=XSD.date)))
    g.add((period, DCAT.endDate, Literal("2024-12-31", datatype=XSD.date)))

    g.add((dataset, DCAT.spatialResolutionInMeters, Literal("1000", datatype=XSD.decimal)))
    g.add((dataset, DCAT.temporalResolution, Literal("P1Y", datatype=XSD.duration)))

    # Business metadata
    g.add((dataset, DCTERMS.accrualPeriodicity, FREQ["frequency/ANNUAL"]))
    g.add((dataset, DCTERMS.accessRights, Literal("public", lang="en")))
    g.add((dataset, DCTERMS.license, URIRef("https://opensource.org/licenses/MIT")))

    # Distributions
    # CSV
    csv_dist = BASE.CourseAccreditationCSV
    g.add((dataset, DCAT.distribution, csv_dist))
    g.add((csv_dist, RDF.type, DCAT.Distribution))
    g.add((csv_dist, DCAT.accessURL, URIRef("https://example.org/data/dataset.csv")))
    g.add((csv_dist, DCAT.downloadURL, URIRef("https://example.org/data/dataset.csv")))
    g.add((csv_dist, DCAT.mediaType, URIRef("https://www.iana.org/assignments/media-types/text/csv")))
    g.add((csv_dist, DCAT.byteSize, Literal("123456", datatype=XSD.nonNegativeInteger)))
    g.add((csv_dist, DCTERMS.format, CTYPE["file-type/CSV"]))

    # TTL
    ttl_dist = BASE.CourseAccreditationCube
    g.add((dataset, DCAT.distribution, ttl_dist))
    g.add((ttl_dist, RDF.type, DCAT.Distribution))
    g.add((ttl_dist, DCAT.accessURL, URIRef("https://example.org/data/cube.ttl")))
    g.add((ttl_dist, DCAT.downloadURL, URIRef("https://example.org/data/cube.ttl")))
    g.add((ttl_dist, DCAT.mediaType, URIRef("https://www.iana.org/assignments/media-types/text/turtle")))
    g.add((ttl_dist, DCAT.byteSize, Literal("234567", datatype=XSD.nonNegativeInteger)))
    g.add((ttl_dist, DCTERMS.format, CTYPE["file-type/Turtle"]))

    return g

def main():
    if len(sys.argv) != 2:
        logging.error("Usage: python dcat_catalog.py <output_file.ttl>")
        sys.exit(1)
    output_path = sys.argv[1]
    g = create_catalog()
    g.serialize(destination=output_path, format="turtle")
    logging.info(f"DCAT catalog successfully written to {output_path}")

if __name__ == "__main__":
    main()
