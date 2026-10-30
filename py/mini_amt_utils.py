"""Shared paths, namespaces and model readers for mini-amt."""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS
from rdflib.collection import Collection

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology" / "mini-amt.ttl"
TOY = ROOT / "data" / "toy-chain.ttl"
DIST = ROOT / "dist"
DOCS = ROOT / "docs"
IMG = DOCS / "diagrams"

AMT = Namespace("http://academic-meta-tool.xyz/vocab#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def local(iri) -> str:
    """Local name of an IRI (after the last '#' or '/')."""
    return str(iri).split("/")[-1].split("#")[-1]


def load_graph(*paths: Path) -> Graph:
    g = Graph()
    for p in paths:
        g.parse(str(p), format="turtle")
    return g


def read_model(g: Graph) -> dict:
    """Concepts, roles and axioms of the domain model, by local name.

    Everything is sorted so that downstream output is deterministic.
    """
    concepts = {local(c): {"label": str(g.value(c, RDFS.label)), "comment": str(g.value(c, RDFS.comment))}
                for c in g.subjects(RDF.type, AMT.Concept)}
    roles = {}
    for r in g.subjects(RDF.type, AMT.Role):
        dom, rng = g.value(r, RDFS.domain), g.value(r, RDFS.range)
        roles[local(r)] = {
            "label": str(g.value(r, RDFS.label)),
            "domain": local(dom) if dom else None,
            "range": local(rng) if rng else None,
            "definition": str(g.value(r, SKOS.definition) or ""),
            "scope": str(g.value(r, SKOS.scopeNote) or ""),
        }
    inverses = sorted(
        (local(a), local(g.value(a, AMT.antecedent)), local(g.value(a, AMT.inverse)))
        for a in g.subjects(RDF.type, AMT.InverseAxiom)
    )
    chains = sorted(
        (local(a), [local(x) for x in Collection(g, g.value(a, AMT.antecedents))],
         local(g.value(a, AMT.consequent)), local(g.value(a, AMT.logic)))
        for a in g.subjects(RDF.type, AMT.RoleChainAxiom)
    )
    subs = sorted(
        (local(a), local(g.value(a, AMT.subRole)), local(g.value(a, AMT.superRole)))
        for a in g.subjects(RDF.type, AMT.SubsumptionAxiom)
    )
    return {"concepts": concepts, "roles": roles,
            "inverses": inverses, "chains": chains, "subs": subs}


def read_edges(g: Graph) -> list[tuple[str, str, str, float]]:
    """Asserted weighted edges (reified statements carrying amt:weight)."""
    out = []
    for s in g.subjects(AMT.weight, None):
        out.append((local(g.value(s, RDF.predicate)), local(g.value(s, RDF.subject)),
                    local(g.value(s, RDF.object)), float(g.value(s, AMT.weight))))
    return sorted(out)
