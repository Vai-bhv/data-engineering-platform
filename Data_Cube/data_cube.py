#!/usr/bin/env python3
import pandas as pd
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SKOS, XSD, QB, DCTERMS

# ——— Namespaces ———
EX     = Namespace("http://example.org/datacube/ontology#")
EXR    = Namespace("http://example.org/datacube/resources/")
SDMX_M = Namespace("http://purl.org/linked-data/sdmx/2009/measure#")
SDMX_D = Namespace("http://purl.org/linked-data/sdmx/2009/dimension#")

def create_concept_schemes(g):
    # Provider concept scheme
    cs = EX.providerScheme
    g.add((cs, RDF.type, SKOS.ConceptScheme))
    g.add((cs, SKOS.prefLabel, Literal("Provider", lang="en")))
    # Program concept scheme
    ps = EX.programScheme
    g.add((ps, RDF.type, SKOS.ConceptScheme))
    g.add((ps, SKOS.prefLabel, Literal("Program", lang="en")))

def create_concepts(g, df):
    # Providers
    for _, row in df[['provider_id','provider_name']].drop_duplicates().iterrows():
        uri = EXR[f"provider/{row.provider_id}"]
        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, SKOS.prefLabel, Literal(row.provider_name)))
        g.add((uri, SKOS.inScheme, EX.providerScheme))
    # Programs
    for _, row in df[['program_id','program_name']].drop_duplicates().iterrows():
        uri = EXR[f"program/{row.program_id}"]
        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, SKOS.prefLabel, Literal(row.program_name)))
        g.add((uri, SKOS.inScheme, EX.programScheme))

def create_dimensions(g):
    dims = []
    # Provider dimension
    pdim = EX.provider
    g.add((pdim, RDF.type,     RDF.Property))
    g.add((pdim, RDF.type,     QB.DimensionProperty))
    g.add((pdim, SKOS.prefLabel, Literal("Provider", lang="en")))
    # SDMX mapping
    g.add((pdim, RDFS.subPropertyOf, SDMX_D.refArea))
    dims.append(pdim)

    # Program dimension
    prdim = EX.program
    g.add((prdim, RDF.type,     RDF.Property))
    g.add((prdim, RDF.type,     QB.DimensionProperty))
    g.add((prdim, SKOS.prefLabel, Literal("Program", lang="en")))
    # SDMX mapping (treat as statistical concept)
    g.add((prdim, RDFS.subPropertyOf, SDMX_D.refStatisticalConcept))
    dims.append(prdim)

    return dims

def create_measures(g):
    measures = []
    m = EX.participantsCount
    g.add((m, RDF.type,     QB.MeasureProperty))
    g.add((m, SKOS.prefLabel, Literal("Participants count", lang="en")))
    # SDMX interoperability
    g.add((m, RDFS.subPropertyOf, SDMX_M.obsValue))
    measures.append(m)
    return measures

def create_structure(g, dims, measures):
    dsd = EX.structure
    g.add((dsd, RDF.type, QB.DataStructureDefinition))
    # dimensions
    for i, dim in enumerate(dims, start=1):
        comp = BNode()
        g.add((dsd, QB.component, comp))
        g.add((comp, QB.dimension, dim))
        g.add((comp, QB.order, Literal(i, datatype=XSD.integer)))
    # measures
    for meas in measures:
        comp = BNode()
        g.add((dsd, QB.component, comp))
        g.add((comp, QB.measure, meas))
    return dsd

def create_dataset(g, dsd):
    ds = EXR.dataset
    g.add((ds, RDF.type, QB.DataSet))
    g.add((ds, RDFS.label, Literal("Course Accreditation Cube", lang="en")))
    g.add((ds, DCTERMS.publisher, Literal("Vaibhav Gupta")))
    g.add((ds, DCTERMS.issued, Literal("2025-04-17", datatype=XSD.date)))
    g.add((ds, DCTERMS.modified, Literal("2025-04-17", datatype=XSD.date)))
    g.add((ds, DCTERMS.title, Literal("Course Accreditation Cube", lang="en")))
    g.add((ds, DCTERMS.license,
           URIRef("https://gitlab.mff.cuni.cz/…/LICENSE")))
    g.add((ds, QB.structure, dsd))
    return ds

def create_observations(g, ds, df):
    for _, row in df.iterrows():
        obs = EXR[f"observation/{row.fact_id}"]
        g.add((obs, RDF.type,       QB.Observation))
        g.add((obs, QB.dataSet,     ds))
        # dimensions
        g.add((obs, EX.provider,    EXR[f"provider/{row.provider_id}"]))
        g.add((obs, EX.program,     EXR[f"program/{row.program_id}"]))
        # measure
        g.add((obs, EX.participantsCount,
               Literal(row.participants_count, datatype=XSD.integer)))

def create_slice(g, ds, dsd, df, provider_id=1):
    sl = EXR[f"slice/provider/{provider_id}"]
    g.add((sl, RDF.type,           QB.Slice))
    g.add((sl, QB.sliceStructure,  dsd))
    g.add((sl, QB.dataSet,         ds))
    for _, row in df[df.provider_id == provider_id].iterrows():
        obs = EXR[f"observation/{row.fact_id}"]
        g.add((sl, QB.observation, obs))

def main():
    # 1) load joined CSV
    df = pd.read_csv('dataset.csv')

    # 2) build graph
    g = Graph()
    g.bind("ex", EX)
    g.bind("exr", EXR)
    g.bind("qb", QB)
    g.bind("skos", SKOS)
    g.bind("sdmx-m", SDMX_M)
    g.bind("sdmx-d", SDMX_D)
    g.bind("dcterms", DCTERMS)

    create_concept_schemes(g)
    create_concepts(g, df)
    dims     = create_dimensions(g)
    measures = create_measures(g)
    dsd      = create_structure(g, dims, measures)
    ds       = create_dataset(g, dsd)
    create_observations(g, ds, df)
    create_slice(g, ds, dsd, df, provider_id=1)

    # 3) serialize
    g.serialize(destination='cube.ttl', format='turtle')
    print("✅ cube.ttl written.")

    # 4) Reminder to run full IC check
    print("👉 Now run: python check‑well‑formed.py cube.ttl  to verify all integrity constraints.")

if __name__ == "__main__":
    main()
