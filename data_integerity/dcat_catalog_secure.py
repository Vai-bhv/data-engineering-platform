#!/usr/bin/env python3
import sys, hashlib
from rdflib import Graph, Namespace, RDF, Literal, BNode, URIRef
from rdflib.namespace import XSD

# DCAT and SPDX namespaces
DCAT    = Namespace("http://www.w3.org/ns/dcat#")
SPDX    = Namespace("http://spdx.org/rdf/terms#")
BASE    = Namespace("https://ksi.mff.cuni.cz/~guptava/232-NDBI046/resources#")

def add_checksum(g, dist_uri, file_path):
    digest = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
    node = BNode()
    g.add((dist_uri, SPDX.checksum, node))
    g.add((node, RDF.type,      SPDX.Checksum))
    g.add((node, SPDX.algorithm, SPDX.checksumAlgorithm_sha256))
    g.add((node, SPDX.checksumValue,
           Literal(digest, datatype=XSD.hexBinary)))

def main():
    if len(sys.argv) != 5:
        print("Usage: extend_catalog.py <in.ttl> <dataset.csv> <cube.ttl> <out.ttl>")
        sys.exit(1)

    in_ttl, csv_f, cube_f, out_ttl = sys.argv[1:]
    g = Graph()
    g.parse(in_ttl, format="turtle")

    # Bind prefixes
    g.bind("dcat", DCAT)
    g.bind("spdx", SPDX)
    g.bind("base", BASE)

    # Add checksums
    add_checksum(g, BASE.CourseAccreditationCSV,  csv_f)
    add_checksum(g, BASE.CourseAccreditationCube, cube_f)

    g.serialize(destination=out_ttl, format="turtle")
    print(f"✔ Extended catalog written to {out_ttl}")

if __name__ == "__main__":
    main()
