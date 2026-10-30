"""Prose of the documentation pages. Tables and derivations are generated in step_docs.py.

British English. Keep sentences short: the pages are read by archaeologists who
review the model, not by reasoner developers.
"""

REPO = "https://github.com/leiza-scit/CHNT2026-amt"      # planned home of the repository
BLOB = REPO + "/blob/main/"

STATUS = """> **Status: draft for archaeological review.** The namespace, the logic operator and all weights
> are placeholders. The role names are proposals, except `hasType` / `isTypeOf`, which were agreed
> with Allard Mees. No real instances are modelled yet."""

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
2. **Keep `amt:weight` un-normalised.** One carrier may have two centres with weight 1.0 each (vague:
   both hold) or 0.5 each (uncertain). `amt:weight` does not have to sum to 1, and it should not be
   forced to.
3. **Put shares and counts elsewhere.** If the question "how many carriers" or "what fraction" matters,
   compute it as its own measure on the pair, in the direction in which it is asked.
4. **Check the symmetry.** A consistency check (a SPARQL query on the reasoned graph) can report every
   pair of inverse edges whose weights differ. It should return nothing."""

WEIGHTS_OPEN = """The reading of the weight is a modelling decision for the degree step, and it is archaeological
before it is technical: is 0.5 on an attribution "possible, but not certain" (a possibility degree)
or "one of two equally likely alternatives" (a probability)? Under the first reading, two alternatives
can both carry 1.0. Under the second, they sum to 1 and the inverse direction cannot be normalised in
the same way. Both readings keep the inverse symmetric as long as the weight is stored un-normalised."""

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
     "A degree of truth per statement, un-normalised (see the Weights page).",
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
]
