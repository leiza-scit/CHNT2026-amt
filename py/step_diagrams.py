"""Step "diagrams": draw the figures into docs/diagrams/ (SVG + PNG).

  01_simple_model     classes, properties (asserted + inverse), red reasoning arcs
  02_full_semantics   roles with domain/range, InverseAxiom, RoleChainAxiom
                      (ordered antecedents), SubsumptionAxiom
  03_toy_reasoning    the same picture on the abstract toy chain, with weights
  04_reasoning_both   the derived roles in both directions: >> above, << below

Everything that has a name in the ontology is read from the ontology; only the
positions are fixed here. A name missing from the ontology raises KeyError
rather than drawing something silently different.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from diagram_kit import RED, arrow, legend, new_canvas, node, save  # noqa: E402
from mini_amt_utils import ONTOLOGY, TOY, load_graph, read_edges, read_model  # noqa: E402
from reference_reasoner import reason  # noqa: E402

CHAIN = ["Potform", "InformationCarrier", "ProductionCentre", "Actor"]   # chain direction
XS = [2.4, 8.2, 14.0, 19.8]
LANE = 0.3


def chain_figure(model, *, instances=None, weights=None, title, stem, legend_items, inverse_arcs=False):
    """Shared layout of figures 1, 3 and 4.

    instances:    {concept: (label, sub)} to draw ovals instead of class boxes.
    weights:      {(role, from_concept): value} appended to the labels.
    inverse_arcs: also draw the inverse of every derived role below the boxes.
    """
    y0 = 5.3 if inverse_arcs else 3.7
    height = 10.6 if inverse_arcs else 9.0
    fig, ax = new_canvas(15.5, 6.2 * height / 9.0, (-0.4, 22.6), (0.0, height))
    ax.text(0.0, height - 0.5, title, fontsize=14, fontweight="bold", va="center")
    boxes = {}
    for concept, x in zip(CHAIN, XS):
        if instances:
            label, sub = instances[concept]
            boxes[concept] = node(ax, x, y0, 3.3, 1.7, label, "instance", shape="oval", sub=sub)
        else:
            boxes[concept] = node(ax, x, y0, 3.5, 1.2, concept, "class", size=11)

    def side(concept, facing, dy):
        """Point on the left/right edge of a node, `facing` the other node."""
        b = boxes[concept]
        return (b["right"][0] + 0.1 if facing == "right" else b["left"][0] - 0.1, y0 + dy)

    def w(role, concept):
        return f"  {weights[(role, concept)]:.2f}" if weights else ""

    derived = {cons for _, _, cons, _ in model["chains"]}

    # asserted role on the upper lane, its inverse on the lower lane
    for _, ante, inv in model["inverses"]:
        if ante in derived or ante == "reaches":
            continue
        d, r = model["roles"][ante]["domain"], model["roles"][ante]["range"]
        d_faces = "right" if CHAIN.index(d) < CHAIN.index(r) else "left"
        r_faces = "left" if d_faces == "right" else "right"
        arrow(ax, side(d, d_faces, LANE), side(r, r_faces, LANE), ante + w(ante, d),
              label_dy=0.3, boxed=False, size=9.5)
        arrow(ax, side(r, r_faces, -LANE), side(d, d_faces, -LANE), inv + w(inv, r),
              label_dy=-0.3, dashed=True, boxed=False, size=9.5, lw=1.5)

    # red reasoning arcs. Inner arcs leave/arrive on the inner corners, the
    # longest (outer) arc on the outer corners; labels sit at different
    # positions along their arcs so that they never collide.
    inverse_of = {ante: inv for _, ante, inv in model["inverses"]}
    for _, ante, cons, _ in model["chains"]:
        d, r = model["roles"][cons]["domain"], model["roles"][cons]["range"]
        i, j = CHAIN.index(d), CHAIN.index(r)
        outer = j - i >= 3
        s_off, e_off = (-0.9, 0.9) if outer else (0.9, -0.9)
        rad = -0.28 if outer else -0.22
        t = 0.5 if outer else (0.3 if i == 0 else 0.7)
        top = boxes[d]["top"][1] + 0.05
        label = f">> {cons}" + w(cons, d) + "\n" + " o ".join(ante)
        arrow(ax, (boxes[d]["top"][0] + s_off, top), (boxes[r]["top"][0] + e_off, top), label,
              color=RED, rad=rad, lw=2.2, size=9, t=t, head=16)
        if inverse_arcs:
            inv = inverse_of[cons]
            bottom = boxes[d]["bottom"][1] - 0.05
            arrow(ax, (boxes[r]["bottom"][0] + e_off, bottom), (boxes[d]["bottom"][0] + s_off, bottom),
                  f"<< {inv}\ninverse of {cons}", color=RED, dashed=True, rad=rad, lw=2.0, size=9,
                  t=1 - t, head=16)

    legend(ax, 0.0, 0.7, legend_items, gap=5.6)
    save(fig, stem)


def figure_full_semantics(model):
    fig, ax = new_canvas(24, 10.2, (-0.2, 40.6), (-0.6, 16.2))
    ax.text(0.0, 15.5, "Mini-AMT - full semantics (AMT vocabulary)", fontsize=15, fontweight="bold", va="center")
    roles = model["roles"]
    inv_roles = {inv for _, _, inv in model["inverses"]}
    chain_roles = {r for _, ante, _, _ in model["chains"] for r in ante}
    longest = max(model["chains"], key=lambda c: len(c[1]))
    row_y = dict(zip(longest[1], (12.0, 8.0, 4.0)))                  # rows follow the 3-step chain
    others = [c for c in model["chains"] if c is not longest]
    top = next(c for c in others if c[1][0] == longest[1][0])       # starts like the long chain: above it
    bottom = next(c for c in others if c is not top)
    der_row = {longest[2]: 8.0, top[2]: 12.0, bottom[2]: 4.0}
    colx = {"back": 3.2, "fwd": 11.2, "rca": 19.6, "der": 28.2, "sup": 36.8}

    for x, head in ((colx["back"], "roles against the chain\n(direction of the source data)"),
                    (colx["fwd"], "roles along the chain\nPotform > Carrier > Centre > Actor"),
                    (colx["rca"], "RoleChainAxiom\n(ordered antecedents)"),
                    (colx["der"], "derived roles (>>)\nand their inverses (<<)"),
                    (colx["sup"], "generic super-role")):
        ax.text(x, 14.3, head, ha="center", va="center", fontsize=10, color="#334155", fontweight="bold")

    pills = {}

    def pill(role, x, y, *, dashed=False, derived=False, h=1.5):
        r = roles[role]
        pills[role] = node(ax, x, y, 5.7, h, role, "role", shape="pill", size=10,
                           sub=f"{r['domain']} -> {r['range']}" if r["domain"] else "no domain / range",
                           dashed=dashed, edge=RED if derived else None, lw=2.6 if derived else 1.6)

    # inverse pairs of the base roles: the forward role defines the row, its
    # partner sits in the backward column
    base = [(a, b, c) for a, b, c in model["inverses"] if b in row_y or c in row_y]
    for _, ante, inv in base:
        fwd, back = (ante, inv) if ante in chain_roles else (inv, ante)
        y = row_y[fwd]
        pill(back, colx["back"], y, dashed=back in inv_roles)
        pill(fwd, colx["fwd"], y, dashed=fwd in inv_roles)
        if ante == back:      # asserted role in the backward column: arrow points right
            arrow(ax, (pills[ante]["right"][0] + 0.08, y), (pills[inv]["left"][0] - 0.08, y), "InverseAxiom", size=8.5)
        else:
            arrow(ax, (pills[ante]["left"][0] - 0.08, y), (pills[inv]["right"][0] + 0.08, y), "InverseAxiom", size=8.5)

    # role chains: the antecedent arrows are numbered in chain order
    for axiom, ante, cons, logic in model["chains"]:
        y = der_row[cons]
        box = node(ax, colx["rca"], y, 6.6, 2.0, "RoleChainAxiom", "axiom", size=9.5,
                   sub=" o ".join(ante) + f"\nlogic: {logic} (placeholder)", sub_size=8)
        for i, role in enumerate(ante):
            dy = (i - (len(ante) - 1) / 2) * 0.7
            arrow(ax, (pills[role]["right"][0] + 0.08, pills[role]["cy"]),
                  (box["left"][0] - 0.08, y + dy), str(i + 1), t=0.2, size=10, lw=1.4)
        pill(cons, colx["der"], y, derived=True)
        arrow(ax, (box["right"][0] + 0.08, y), (pills[cons]["left"][0] - 0.08, y), "consequent", size=8)

    # subsumption under the generic role (arrival points spread on the pill)
    pill("reaches", colx["sup"], 8.0, derived=True)
    for _, sub, sup in model["subs"]:
        spread = (pills[sub]["cy"] - 8.0) / 4 * 0.45
        arrow(ax, (pills[sub]["right"][0] + 0.08, pills[sub]["cy"]),
              (pills[sup]["left"][0] - 0.08, pills[sup]["cy"] + spread),
              "SubsumptionAxiom", size=7.5, t=0.45)

    # inverses of the derived roles sit below their partner
    for _, ante, inv in model["inverses"]:
        if ante in pills and ante not in row_y and inv not in pills:
            pill(inv, pills[ante]["cx"], pills[ante]["cy"] - 1.9, dashed=True, derived=True, h=1.3)
            arrow(ax, (pills[ante]["cx"], pills[ante]["bottom"][1] - 0.04),
                  (pills[inv]["cx"], pills[inv]["top"][1] + 0.04), "InverseAxiom", size=8)

    items = [("asserted role", "role", False, None), ("inverse role (InverseAxiom)", "role", True, None),
             ("derived role (red = reasoning)", "role", False, RED), ("axiom", "axiom", False, None)]
    x = 0.0
    for text, kind, dashed, edge in items:
        node(ax, x + 1.2, 0.7, 2.4, 0.8, "", kind, shape="pill", dashed=dashed, edge=edge,
             lw=2.4 if edge else 1.4)
        ax.text(x + 2.7, 0.7, text, va="center", fontsize=9.5)
        x += 8.6 if len(text) < 20 else 9.8
    ax.text(0.0, -0.3, "Roles show domain -> range. Degrees (amt:weight) and the logic operator are placeholders; "
            "their calculation is decided later.", fontsize=8.5, color="#475569", va="center")
    save(fig, "02_full_semantics")


def main() -> int:
    g = load_graph(ONTOLOGY, TOY)
    model = read_model(g)
    for name in CHAIN:
        model["concepts"][name]                       # KeyError if the ontology lost a concept

    chain_figure(
        model, title="Mini-AMT - simple view: classes, properties, reasoning",
        stem="01_simple_model",
        legend_items=[("solid", "asserted property"), ("dashed", "inverse (InverseAxiom)"),
                      ("red", "derived by role chain (>>)"), ("class", "class (Concept)")])

    state = reason(model, read_edges(g))
    names = ("Potform", "Carrier", "Centre", "Actor")
    instances = {c: (f"{n} 1", c) for c, n in zip(CHAIN, names)}
    holder = {c: f"{n}_1" for c, n in zip(CHAIN, names)}
    weights = {(role, next(c for c, n in holder.items() if n == a)): e["weight"]
               for (role, a, b), e in state.items()}
    chain_figure(
        model, instances=instances, weights=weights,
        title="Toy chain: what the reasoning derives (degrees: placeholder logic)",
        stem="03_toy_reasoning",
        legend_items=[("solid", "asserted, with weight"), ("dashed", "inverse, same weight"),
                      ("red", "derived, weight by logic"), ("instance", "individual")])

    chain_figure(
        model, inverse_arcs=True, title="Reasoning properties in both directions: >> and <<",
        stem="04_reasoning_both",
        legend_items=[("solid", "asserted property"), ("dashed", "inverse of an asserted property"),
                      ("red", "derived, forward (>>)"), ("reddashed", "derived, inverse (<<)")])
    figure_full_semantics(model)
    print("wrote docs/diagrams/01_simple_model, 02_full_semantics, 03_toy_reasoning, 04_reasoning_both (.svg + .png)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
