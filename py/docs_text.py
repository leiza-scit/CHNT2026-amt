"""Prose of the documentation pages. Tables and derivations are generated in step_docs.py.

British English. Keep sentences short: the pages are read by archaeologists who
review the model, not by reasoner developers.
"""

REPO = "https://github.com/leiza-scit/CHNT2026-amt"      # planned home of the repository
BLOB = REPO + "/blob/main/"

STATUS = """> **Status: draft for archaeological review.** The namespace is a placeholder. The weights follow the
> rule of the source paper (see Weights). The logic operator (product) and the role names are proposals,
> except `hasType` / `isTypeOf`, which were agreed with Allard Mees. Three real chains from the CHNT data
> are modelled (see Chains)."""

INDEX_INTRO = """A deliberately small [AMT](http://academic-meta-tool.xyz/) domain model for one chain:

    [Potform] -- [InformationCarrier] -- [ProductionCentre] -- [Actor]

The model asserts three kinds of links (a carrier has a type, a carrier is attributed to a centre,
an actor works at a centre). A role-chain reasoner derives the links that follow from them: which
potforms are associated with which centres, which carriers with which actors, which potforms with
which actors. Each derived link can be read from both ends."""

IDEA = """| Rule | Reads as |
|---|---|
| `[Potform]>>[ProductionCentre]` | a carrier of this type is attributed to that centre |
| `[InformationCarrier]>>[Actor]` | the carrier is attributed to a centre at which the actor worked |
| `[Potform]>>[Actor]` | a carrier of this type is attributed to a centre at which the actor worked |"""

WHY_INVERSES = """AMT composes edges head to tail: the target of one edge must be the source of the next. The
chain runs Potform, InformationCarrier, ProductionCentre, Actor. Of the three links that the source
data asserts, only one points along that chain:

| Asserted role | Points | Along the chain? |
|---|---|---|
| `hasType` | InformationCarrier to Potform | no, against it |
| `hasProductionCentre` | InformationCarrier to ProductionCentre | yes |
| `worksAt` | Actor to ProductionCentre | no, against it |

Without inverses nothing composes: the first rule starts at a Potform, but no asserted edge leaves a
Potform. `hasType` therefore gets its inverse `isTypeOf` (agreed with Allard Mees), and `worksAt` gets
`hasWorker`. Every rule uses at least one inverse. The derived roles get inverses too, so that an
association can be asked from either end: "which centres go with this potform?" and "which potforms
go with this centre?"."""

CAVEATS = """1. **An association, not an attribution.** `carrierToActor` says that the actor worked at the
   centre to which the carrier is attributed. It does not say that the actor made the carrier. Both
   have time intervals in the source model; the chain does not compare them.
2. **Several paths keep the best one.** When more than one path leads to the same pair, AMT keeps the
   maximum weight. A potform with many carriers at one centre gets the weight of the best single
   carrier, not a weight that grows with the number of carriers.
3. **The third rule is written over the base roles.** `potformToActor` is `isTypeOf o hasProductionCentre
   o hasWorker`, not `potformToCentre o hasWorker`. For the associative operators (Goedel, Product,
   Einstein, Hamacher) both give the same degree; for the n-ary geometric mean they do not."""

WEIGHTS_ANSWER = """**Yes, for inverse roles the weight is the same in both directions.** If a carrier is of a potform
with degree 0.9, then the potform is the type of that carrier with degree 0.9. This is how AMT defines
an inverse, and it is also what the statement means."""

WEIGHTS_WHY = """1. **It is the rule of the AMT ontology.** The `amt:InverseRule` states: *"Add an edge (b -inverse-> a)
   with weight w."* The inverse edge copies the weight of its antecedent.
2. **It is the same statement.** An AMT edge is a statement about a pair with a degree of truth, read as
   a fuzzy relation. The inverse of a fuzzy relation is its transpose with the same membership degrees.
   `Carrier hasType Potform (0.9)` and `Potform isTypeOf Carrier (0.9)` are one statement read from two
   ends. If the two degrees differed, they would not be inverses but two different statements.
3. **The derived roles behave the same way.** All six fuzzy-logic operators of AMT (Goedel, Product,
   Lukasiewicz, Einstein, Geometric mean, Hamacher) are symmetric in their arguments. A chain read
   backwards uses the same weights, so `potformToCentre` and `centreToPotform` carry the same degree,
   and so do the other two pairs."""

WEIGHTS_BREAK = """The symmetry holds because the weight is a degree of truth. Other quantities look like weights
and are **not** all symmetric. Apart from the first row they should not be stored in `amt:weight`:

| Quantity | Example | Same in both directions? | Where it belongs |
|---|---|---|---|
| Degree of truth or certainty of the statement | the attribution of a carrier to a centre holds with 0.5 (recorded as uncertain) | yes | `amt:weight` |
| Conditional share | 40 % of the carriers of a potform are attributed to a centre, but only 10 % of that centre's carriers are of this potform | no | a separate measure on the pair |
| Normalised alternatives | a carrier has two possible centres, weights 0.5 and 0.5 so that they sum to 1 | no: the sum is taken per source node, so the inverse edges would sum differently | normalise when reading, or keep as a separate measure |
| Number of supporting carriers | twelve carriers support the association of a potform with a centre | yes, but it is a count, not a degree | a separate measure; see the open point below |"""

WEIGHTS_RULES = """1. **Assert one direction only.** Assert the roles in the direction of the source data (`hasType`,
   `hasProductionCentre`, `worksAt`) and let the inverse axioms create the other direction. If both
   directions are asserted with different weights, the data contradicts itself.
2. **Take the weight from the rule.** `py/weights.py` computes it from the source string. AND keeps the
   full weight for every entity (1.0, or 0.5 with a question mark); OR shares it (one over the number of
   alternatives, one more with a question mark). Nothing is normalised afterwards.
3. **Put shares and counts elsewhere.** If the question "how many carriers" or "what fraction" matters,
   compute it as its own measure on the pair, in the direction in which it is asked.
4. **Check the symmetry.** A consistency check (a SPARQL query on the reasoned graph) can report every
   pair of inverse edges whose weights differ. It should return nothing."""

WEIGHTS_OPEN = """The rule reads a question mark as one more possibility: "A or B?" gives one third to A, one third to B
and leaves one third to "neither". "A and B?" gives one half to each, because under AND both hold and the
question mark is the only doubt. Whether that is what the archaeologist means by a question mark is an
open question (see the Review page). The weight stays symmetric under inversion either way."""

REVIEW_INTRO = """These are the points where the archaeological reading decides the model. Each question says what
is proposed and what would change if the answer is no."""

REVIEW_QUESTIONS = [
    ("Is \"associated with\" the right reading of the three `>>` roles?",
     "`carrierToActor` says only that the actor worked at the centre to which the carrier is attributed.",
     "If it should read as an attribution, the chain needs more evidence than a shared centre (for example "
     "the actor's period). If it stays an association, the role names should avoid any implication of authorship."),
    ("Should time enter the chain?",
     "Carrier and actor both have time intervals in the source model. At present the chain ignores them.",
     "An overlap of the two intervals can become one more link in the chain, with its own degree."),
    ("What does the weight mean: a possibility degree or a probability?",
     "A degree of truth per statement, computed by the rule of the source paper (see the Weights page).",
     "If alternatives must sum to 1, the weights become directional and shares move into a separate measure."),
    ("Is `actorToPotform` a useful reading?",
     "It is the forms attested at the centre where the actor worked: a candidate repertoire, not the actor's own.",
     "If it misleads, drop the role and its inverse axiom; the other two associations are unaffected."),
    ("Does one potform with many carriers at a centre need more than the best path?",
     "No: AMT keeps the best single path.",
     "If the number of carriers should count, it becomes a separate measure next to the weight."),
    ("Are the role names acceptable?",
     "`hasType` / `isTypeOf` are agreed. `hasProductionCentre`, `worksAt`, `hasWorker` and the six derived "
     "names are proposals.",
     "Renaming touches only the ontology; the documentation is generated from it."),
    ("Is it right to collapse ActorEntity and Actor into one concept?",
     "Yes for this model: the chain only needs the person who works at a centre.",
     "If the stamp name (ActorEntity) must stay distinct from the person (Actor), one more concept and "
     "one more link enter the chain."),
    ("Is the carrier-centre link asserted (M1) or derived from the actor (M2)?",
     "M1: asserted, as in the data export. In the data the centre string belongs to the potter: every one of "
     "the 1,375 potters in the centre exports has exactly one, and the carriers compared (1,072 potters) share "
     "identical edges. The source paper says the carrier-centre relation follows from the potter-centre relation.",
     "M2 asserts only the carrier-potter link (crisp) and derives the carrier-centre link. That removes the "
     "double counting of the same doubt (see question 9) and needs a certain stamp attribution, which the "
     "2,777 carriers with an uncertain potter name do not have."),
    ("Which logic operator: product or Goedel?",
     "Product, as in the role-chain axioms of the source paper. Under M1 a statement that is inherited from "
     "the actor enters the chain twice: for Ve- i the carrier-actor degree is 0.25 under product and 0.5 under Goedel.",
     "Goedel (minimum) avoids the double count but ignores how many doubtful steps a chain has. M2 avoids it "
     "under both operators."),
    ("Is a question mark one more possibility?",
     "Yes, as in the paper: \"A or B?\" gives one third to A and B and leaves one third to \"neither\".",
     "If the question mark should not take a share from the alternatives, \"A or B?\" would be 0.5 each and "
     "could no longer be told from \"A or B\"; the rule and the FW type would have to change."),
    ("Which patterns occur on which relation?",
     "As listed on the Weights page. For the carrier-centre relation only the question mark is listed, but "
     "the exports also carry AND and OR there (inherited from the actor).",
     "If the carrier-centre relation is derived (M2) the inherited patterns disappear from it."),
    ("Are combined forms such as 18/31 one type?",
     "Yes (source paper, figure 6): a slash joins two numbers into one type, an OR separates alternatives. "
     "Generic forms such as \"dish or bowl?\" are modelled like any other alternative.",
     "If a generic form should be a class of its own, the possibilities would be counted differently."),
    ("What about centre strings that name more entities than the model has nodes?",
     "The weight is computed from the whole string; an entity without a centre node gets no edge. This happens "
     "in 9,033 of 45,685 centre strings of the exports (regions, groups, centres missing in the mapping); every "
     "one of the 95,819 existing centre edges carries the weight the rule gives.",
     "Creating nodes for regions and groups would close the gap and needs a decision on their class."),
    ("Does the hextuple have to keep the order and spelling of the source string?",
     "No. The round trip from the hextuples back to the string is lossless except for the order of the "
     "entities and the spelling; weight, FW type and the number of edges decide the pattern.",
     "If the order matters, the original string becomes a seventh element or a property of the statement."),
]

