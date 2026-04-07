import sys
import logging
from rdflib import Graph
from rdflib.namespace import DCAT, DCTERMS

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def run_queries(catalog_file: str):
    g = Graph()
    g.parse(catalog_file, format='turtle')

    # Query 1: Temporal coverage
    q1 = '''
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    SELECT ?start ?end WHERE {
      ?ds a dcat:Dataset ;
          dcterms:temporal ?p .
      ?p dcat:startDate ?start ;
         dcat:endDate   ?end .
    }
    '''
    print("1) Temporal coverage:")
    for row in g.query(q1): print(f"   {row.start} → {row.end}")

    # Query 2: Distributions byteSize & format
    q2 = '''
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?dist ?size ?format WHERE {
      ?ds a dcat:Dataset ; dcat:distribution ?dist .
      ?dist dcat:byteSize ?size ; dcterms:format ?format .
    }
    '''
    print("\n2) Distributions:")
    for row in g.query(q2): print(f"   {row.dist}: {row.size} bytes, format={row.format}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        logging.error("Usage: python query_catalog.py <catalog.ttl>")
        sys.exit(1)
    run_queries(sys.argv[1])
