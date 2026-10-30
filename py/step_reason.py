"""Step "reason": run the reasoning on the toy chain and write dist/.

Writes
  dist/mini-amt-with-toy.ttl   ontology + toy chain in one file (engine input)
  dist/reasoned-edges.csv      asserted and derived edges with provenance
  dist/reasoning-report.md     the three ">>" derivations, human-readable

If the AMT engine is importable it is run as well and compared edge by edge
with the reference reasoner; a mismatch is an error.
"""
from __future__ import annotations

import csv
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from mini_amt_utils import DIST, ONTOLOGY, TOY, load_graph, local, read_edges, read_model
from reference_reasoner import reason

ENGINE_TOL = 1e-9


def run_engine(merged_path):
    """Return {(role, from, to): weight} from the AMT engine, or None."""
    try:
        from amt import do_reasoning, load_amt
    except ImportError:
        return None
    data = load_amt(str(merged_path))
    result = do_reasoning(data["edges"], data["axioms"])
    return {(local(e["role"]), local(e["from"]), local(e["to"])): e["weight"] for e in result}


def main() -> int:
    DIST.mkdir(exist_ok=True)

    merged = DIST / "mini-amt-with-toy.ttl"
    merged.write_text(ONTOLOGY.read_text(encoding="utf-8") + "\n\n" + TOY.read_text(encoding="utf-8"),
                      encoding="utf-8", newline="\n")

    g = load_graph(ONTOLOGY, TOY)
    model, edges = read_model(g), read_edges(g)
    state = reason(model, edges)

    rows = sorted((k[0], k[1], k[2], f"{v['weight']:.4f}", "derived" if v["inferred"] else "asserted",
                   " ".join(v["provenance"])) for k, v in state.items())
    with (DIST / "reasoned-edges.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["role", "from", "to", "weight", "kind", "axioms"])
        w.writerows(rows)

    lines = ["# Reasoning report (toy chain, reference reasoner)", "",
             "Logic operator of all role chains: placeholder (see ontology).", "",
             "| Derived edge | Weight | Axiom |", "|---|---|---|"]
    for role, a, b, wgt, kind, prov in rows:
        if role in ("potformToCentre", "carrierToActor", "potformToActor", "reaches"):
            lines.append(f"| {a} --{role}--> {b} | {wgt} | {prov.replace(' ', ', ')} |")
    (DIST / "reasoning-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    n_der = sum(1 for v in state.values() if v["inferred"])
    print(f"reference reasoner: {len(edges)} asserted, {n_der} derived edges")

    engine = run_engine(merged)
    if engine is None:
        print("AMT engine not installed - cross-check skipped")
        return 0
    ref = {k: v["weight"] for k, v in state.items()}
    only_ref, only_eng = sorted(set(ref) - set(engine)), sorted(set(engine) - set(ref))
    diff = sorted(k for k in set(ref) & set(engine) if abs(ref[k] - engine[k]) > ENGINE_TOL)
    if only_ref or only_eng or diff:
        print("MISMATCH engine vs reference")
        for label, items in (("only in reference", only_ref), ("only in engine", only_eng), ("weight differs", diff)):
            for k in items:
                print(f"  {label}: {k}")
        return 1
    print(f"AMT engine agrees with the reference reasoner on all {len(ref)} edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
