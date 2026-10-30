"""The degree of connection and the FW type of a vague or uncertain source string.

Rule of the source paper (Thiery, Mees, Tolle and Wigg-Wolf 2021, section 4):

    amt_weight = 1 / (n_questionmark + n_possibilities)

    no AND or OR   n_possibilities = 1
    AND            n_possibilities = 1   (all entities hold; each gets the full weight)
    OR             n_possibilities = the number of entities between the ORs
    '?'            n_questionmark  = 1   (one question mark per statement, wherever it stands)

The weight is stored with two decimals, as in the paper (one in three is 0.33).
A string that mixes AND and OR is not covered by the rule and raises ValueError.

Hextuple. An AMT statement is a reified quadruple (subject, predicate, object, weight). The FW
ontology (http://w3id.org/fw_ontology/) adds two more elements: fw:hasType, the kind of
imprecision (one of the individuals fw:Uncertainty, fw:Vagueness, fw:FuzzinessWobbliness), and
fw:hasMethod, how the weight was obtained (here fw:EqualShareRule, which describes this very rule).
The source string itself is kept as fw:TextEvidence (fw:sourceString) and linked with
fw:derivedFrom; the entities of one string share one evidence node.

    statement                  FW type (fw:hasType)                     pattern
    -------------------------  ---------------------------------------  -------
    no ?, no AND, no OR        none: AMT reads a missing type as        certain
                               fw:Vagueness (the default)
    ? only                     fw:Uncertainty                           q
    OR (several), no ?         fw:Vagueness                             or
    AND (several), no ?        fw:Vagueness                             and
    ? with OR                  fw:FuzzinessWobbliness                   q+or
    ? with AND                 fw:FuzzinessWobbliness                   q+and

Which patterns occur is a property of the relation, not of the string. CONTEXTS lists, per
relation, the patterns the data owners expect; anything else is flagged (`listed` is False).

Standalone: python py/weights.py   (self-test: cases, hextuple type, lossless round trip)
"""
from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mini_amt_utils import DIST, ROOT  # noqa: E402

CASES = ROOT / "data" / "weight-cases.csv"

FW = "http://w3id.org/fw_ontology/"                      # namespace of the FW ontology
UNCERTAINTY, VAGUENESS, FUZZINESS_WOBBLINESS = "Uncertainty", "Vagueness", "FuzzinessWobbliness"
FW_TYPE = {"q": UNCERTAINTY, "or": VAGUENESS, "and": VAGUENESS,
           "q+or": FUZZINESS_WOBBLINESS, "q+and": FUZZINESS_WOBBLINESS}
FW_METHOD = "EqualShareRule"                              # fw:EqualShareRule in the FW ontology
# fw:implementedBy of fw:EqualShareRule: where the rule is implemented and tested
IMPLEMENTED_BY = "https://github.com/leiza-scit/CHNT2026-amt/blob/main/py/weights.py"

# patterns expected per relation (domain--range), as stated by the data owners
CONTEXTS = {
    "informationcarrier--potform":          {"or", "q", "q+or"},
    "actor--productioncentre":              {"or", "and", "q+and", "q"},
    "informationcarrier--productioncentre": {"q"},
}

SPLIT = re.compile(r"\s+(?:and|or)\s+")


@dataclass(frozen=True)
class Statement:
    text: str
    entities: tuple[str, ...]
    connective: str        # "", "and" or "or"
    n_questionmark: int
    n_possibilities: int

    @property
    def weight(self) -> float:
        return round(1 / (self.n_questionmark + self.n_possibilities), 2)

    @property
    def pattern(self) -> str:
        if len(self.entities) < 2 and not self.n_questionmark:
            return "certain"
        core = self.connective or ""
        return "q" + ("+" + core if core else "") if self.n_questionmark else core

    @property
    def fw_type(self) -> str | None:
        """The local name of the fw:hasType individual; None for a certain statement (AMT default: Vagueness)."""
        return FW_TYPE.get(self.pattern)


def parse(text: str) -> Statement:
    """Split a source string into its entities and count question mark and possibilities."""
    q = 1 if "?" in text else 0
    bare = " ".join(text.replace("?", " ").split())
    has_and, has_or = bool(re.search(r"\sand\s", bare)), bool(re.search(r"\sor\s", bare))
    if has_and and has_or:
        raise ValueError(f"AND and OR in one statement is not covered by the rule: {text!r}")
    entities = tuple(p.strip() for p in SPLIT.split(bare) if p.strip())
    connective = "and" if has_and else "or" if has_or else ""
    return Statement(text, entities, connective, q, len(entities) if has_or else 1)


def listed(st: Statement, context: str) -> bool:
    """Is the pattern of this statement one the data owners expect for the relation?"""
    return st.pattern == "certain" or st.pattern in CONTEXTS[context]


def edges_for(text: str, context: str) -> list[dict]:
    """One hextuple payload per entity: what the weight, fw:hasType, fw:hasMethod and the evidence must carry."""
    st = parse(text)
    return [{"entity": e, "weight": st.weight, "type": st.fw_type, "method": FW_METHOD, "source": text,
             "pattern": st.pattern, "listed": listed(st, context)} for e in st.entities]


def reconstruct(edges: list[dict]) -> str:
    """Rebuild the source string from the edges of one statement, without the evidence.

    Only weight, type and the number of edges are used. Lost on the way, and therefore not
    reproduced: the order of the entities (they come back sorted) and the exact spelling. This is
    the counter-check for the evidence node, which keeps the string exactly (see step chains).
    """
    n, w, t = len(edges), edges[0]["weight"], edges[0]["type"]
    names = sorted(e["entity"] for e in edges)
    if n == 1:
        return names[0] + ("?" if w == 0.5 else "")
    candidates = []                                       # (connective, question mark)
    for q in (0, 1):
        if round(1 / (q + 1), 2) == w:
            candidates.append(("and", q))
        if round(1 / (q + n), 2) == w:
            candidates.append(("or", q))
    candidates = [c for c in candidates if FW_TYPE[("q+" if c[1] else "") + c[0]] == t]
    if len(candidates) != 1:
        raise ValueError(f"cannot reconstruct {n} edges with weight {w} and type {t}: {candidates}")
    connective, q = candidates[0]
    return f" {connective} ".join(names) + ("?" if q else "")


def selftest() -> list[dict]:
    """Check every case of data/weight-cases.csv (weight, type, pattern, round trip); raise on a failure."""
    rows = []
    with CASES.open(encoding="utf-8", newline="") as fh:
        for case in csv.DictReader(fh):
            st = parse(case["text"])
            got = (st.weight, len(st.entities), st.fw_type or "", st.pattern)
            want = (float(case["weight"]), int(case["entities"]), case["fw_type"], case["pattern"])
            if got != want:
                raise AssertionError(f"{case['text']!r}: got {got}, expected {want} ({case['source']})")
            if not listed(st, case["context"]) and case["listed"] == "yes":
                raise AssertionError(f"{case['text']!r}: pattern {st.pattern} not listed for {case['context']}")
            back = parse(reconstruct(edges_for(case["text"], case["context"])))
            same = (back.weight, back.fw_type, sorted(back.entities), back.connective) == \
                   (st.weight, st.fw_type, sorted(st.entities), st.connective)
            if not same:
                raise AssertionError(f"round trip changed {case['text']!r} into {back.text!r}")
            rows.append({**case, "n_questionmark": st.n_questionmark, "n_possibilities": st.n_possibilities})
    # the claim behind the round trip: for a known number of edges, weight and type are never ambiguous
    for n in range(2, 51):
        keys = [(round(1 / (q + (n if c == "or" else 1)), 2), FW_TYPE[("q+" if q else "") + c])
                for c in ("and", "or") for q in (0, 1)]
        assert len(set(keys)) == 4, f"weight and type do not separate the four patterns for {n} edges"
    return rows


def main() -> int:
    rows = selftest()
    DIST.mkdir(exist_ok=True)
    with (DIST / "weight-cases.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["text", "context", "entities", "n_questionmark", "n_possibilities", "weight",
                    "pattern", "fw_type", "listed", "source"])
        w.writerows([[r["text"], r["context"], r["entities"], r["n_questionmark"], r["n_possibilities"],
                      r["weight"], r["pattern"], r["fw_type"], r["listed"], r["source"]] for r in rows])
    print(f"weight rule: {len(rows)} cases agree (weight, FW type, pattern, lossless round trip)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
