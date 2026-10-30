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

Type and method (hextuple, AMT.engine 0.6.0). An edge may carry an FW type (fw:Uncertainty,
fw:Vagueness, fw:FuzzinessWobbliness; None = not stated, which AMT reads as fw:Vagueness).
  RoleChainAxiom    method = the logic of the axiom; type = the common type of the
                    antecedent edges, or fw:FuzzinessWobbliness if they differ
  InverseAxiom,
  SubsumptionAxiom  no method; type of the source edge
  Equal weights     the path with the smaller (method, type) wins, so that the result
                    does not depend on the order in which paths are found
This part is written from the documented rules, not from the engine's code, so that
step "reason" and step "chains" can compare the two.
"""
from __future__ import annotations

from math import prod

LOGIC = {"GoedelLogic": min, "ProductLogic": prod}

VAGUENESS, FUZZINESS_WOBBLINESS = "Vagueness", "FuzzinessWobbliness"


def effective_type(t: str | None) -> str:
    """The type that counts: the stated one, or the AMT default (vagueness)."""
    return t or VAGUENESS


def combine_types(types) -> str | None:
    """Type of a derived edge from its antecedents (stored form: None = vagueness)."""
    seen = {effective_type(t) for t in types}
    result = next(iter(seen)) if len(seen) == 1 else FUZZINESS_WOBBLINESS
    return None if result == VAGUENESS else result


def reason(model: dict, edges: list[tuple]) -> dict:
    """Return {(role, from, to): {"weight", "type", "method", "inferred", "provenance"}}.

    An edge is (role, from, to, weight) or (role, from, to, weight, type) with the local name
    of the FW type (or None). "method" is the local name of the logic for a role-chain edge.
    """
    state: dict = {}
    for r, a, b, w, *rest in edges:
        state[(r, a, b)] = {"weight": w, "type": rest[0] if rest else None, "method": None,
                            "inferred": False, "provenance": []}

    def put(key, weight, axiom, typ=None, method=None) -> bool:
        cur = state.get(key)
        if cur is None:
            state[key] = {"weight": weight, "type": typ, "method": method,
                          "inferred": True, "provenance": [axiom]}
            return True
        changed = False
        if cur["inferred"]:
            if weight > cur["weight"] + 1e-12:
                cur.update(weight=weight, type=typ, method=method)
                changed = True
            elif abs(weight - cur["weight"]) <= 1e-12 and \
                    (method or "", effective_type(typ)) < (cur["method"] or "", effective_type(cur["type"])):
                # a different type can change what depends on this edge; a different method cannot
                changed = effective_type(typ) != effective_type(cur["type"])
                cur.update(type=typ, method=method)
        if cur["inferred"] and axiom not in cur["provenance"]:
            cur["provenance"] = sorted(cur["provenance"] + [axiom])
        return changed

    changed = True
    while changed:
        changed = False
        for axiom, ante, inv in model["inverses"]:
            for (r, a, b), e in sorted(state.items()):
                if r == ante:
                    changed |= put((inv, b, a), e["weight"], axiom, e["type"])
        for axiom, sub, sup in model["subs"]:
            for (r, a, b), e in sorted(state.items()):
                if r == sub:
                    changed |= put((sup, a, b), e["weight"], axiom, e["type"])
        for axiom, antecedents, consequent, logic in model["chains"]:
            if logic not in LOGIC:
                raise ValueError(f"reference reasoner does not know {logic}")
            paths = [([a, b], [e["weight"]], [e["type"]]) for (r, a, b), e in sorted(state.items())
                     if r == antecedents[0]]
            for role in antecedents[1:]:
                paths = [(nodes + [b], ws + [e["weight"]], ts + [e["type"]])
                         for nodes, ws, ts in paths
                         for (r, a, b), e in sorted(state.items())
                         if r == role and a == nodes[-1]]
            for nodes, ws, ts in paths:
                changed |= put((consequent, nodes[0], nodes[-1]), LOGIC[logic](ws), axiom,
                               combine_types(ts), logic)
    return state
