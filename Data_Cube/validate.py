#!/usr/bin/env python3
import sys
from rdflib import Graph
from rdflib.namespace import RDF, QB

def main(path):
    g = Graph()
    g.parse(path, format='turtle')

    # discover declared dims & measures
    dims    = set(g.subjects(RDF.type, QB.DimensionProperty))
    measures= set(g.subjects(RDF.type, QB.MeasureProperty))

    errors = 0
    for obs in g.subjects(RDF.type, QB.Observation):
        preds = set(g.predicates(subject=obs))
        if not (dims & preds):
            print(f"ERROR: Observation {obs} has no dimension triple.")
            errors += 1
        if not (measures & preds):
            print(f"ERROR: Observation {obs} has no measure triple.")
            errors += 1

    if errors == 0:
        print("✅ Validation passed: all observations have at least one dimension and one measure.")
    else:
        print(f"❌ Validation failed with {errors} errors.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_cube.py <cube-file.ttl>")
        sys.exit(1)
    main(sys.argv[1])
