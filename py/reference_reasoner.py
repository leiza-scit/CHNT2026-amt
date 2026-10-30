"""A small, independent reference reasoner for the mini-amt axioms.

It is NOT a replacement for the AMT engine. It implements the documented
semantics of the three axiom types used here (see ontology/amt.ttl in the
engine repository) in about sixty lines, so that

  * the diagrams can show what the model derives without needing the engine;
  * step "reason" can cross-check the engine against a second opinion.

Semantics implemented
  InverseAxiom      edge (a -antecedent-> b, w)   =>  (b -inverse-> a, w)
  SubsumptionAxiom  edge (a -subRole-> b, w)      =>  (a -superRole-> b, w)
  RoleChainAxiom    edges e_1..e_n head-to-tail   =>  (first -consequent-> last,
                    logic(w_1..w_n)); several paths to the same pair keep the
                    maximum weight
Only Goedel (min) and Product are supported; anything else raises.
"""
from __future__ import annotations

from math import prod

LOGIC = {"GoedelLogic": min, "ProductLogic": prod}


def reason(model: dict, edges: list[tuple[str, str, str, float]]) -> dict:
    """Return {(role, from, to): {"weight", "inferred", "provenance"}}."""
    state: dict = {(r, a, b): {"weight": w, "inferred": False, "provenance": []}
                   for r, a, b, w in edges}

    def put(key, weight, axiom) -> bool:
        cur = state.get(key)
        if cur is None:
            state[key] = {"weight": weight, "inferred": True, "provenance": [axiom]}
            return True
        if weight > cur["weight"] + 1e-12 and cur["inferred"]:
            cur["weight"] = weight
            changed = True
        else:
            changed = False
        if cur["inferred"] and axiom not in cur["provenance"]:
            cur["provenance"] = sorted(cur["provenance"] + [axiom])
        return changed

    changed = True
    while changed:
        changed = False
        for axiom, ante, inv in model["inverses"]:
            for (r, a, b), e in sorted(state.items()):
                if r == ante:
                    changed |= put((inv, b, a), e["weight"], axiom)
        for axiom, sub, sup in model["subs"]:
            for (r, a, b), e in sorted(state.items()):
                if r == sub:
                    changed |= put((sup, a, b), e["weight"], axiom)
        for axiom, antecedents, consequent, logic in model["chains"]:
            if logic not in LOGIC:
                raise ValueError(f"reference reasoner does not know {logic}")
            paths = [([a, b], [e["weight"]]) for (r, a, b), e in sorted(state.items())
                     if r == antecedents[0]]
            for role in antecedents[1:]:
                paths = [(nodes + [b], ws + [e["weight"]])
                         for nodes, ws in paths
                         for (r, a, b), e in sorted(state.items())
                         if r == role and a == nodes[-1]]
            for nodes, ws in paths:
                changed |= put((consequent, nodes[0], nodes[-1]), LOGIC[logic](ws), axiom)
    return state
