# mini-amt

A deliberately small AMT domain model for the chain

    [Potform] -- [InformationCarrier] -- [ProductionCentre] -- [Actor]

and the role-chain reasoning on top of it, documented as GitHub Pages in `docs/`.
It is about the **model and its reasoning**, with the weight rule of the source paper
and three real chains from the CHNT data. There are no persistent IRIs yet. This repository is laid out (`main.py`, `py/`,
`ontology/`, `data/`, `docs/`) so that it can move into `CHNT2026-amt` as it is.

![simple view](docs/diagrams/01_simple_model.png)

## The model in one table

| Layer | What | Names |
|---|---|---|
| Concepts | four classes | `Potform`, `InformationCarrier`, `ProductionCentre`, `Actor` |
| Asserted roles | direction of the source data | `hasType` (IC -> Potform), `hasProductionCentre` (IC -> PC), `worksAt` (Actor -> PC) |
| Inverse roles | `amt:InverseAxiom` | `isTypeOf`, `isProductionCentreOf`, `hasWorker` |
| Derived roles (`>>`) | `amt:RoleChainAxiom` | `potformToCentre`, `carrierToActor`, `potformToActor` |
| Derived inverses (`<<`) | `amt:InverseAxiom` | `centreToPotform`, `actorToCarrier`, `actorToPotform` |
| Generic `>>` / `<<` | `amt:SubsumptionAxiom` + inverse | `reaches`, `reachedBy` |

The three rules, as role chains over the roles that point along the chain direction:

    [Potform]>>[ProductionCentre]              = isTypeOf o hasProductionCentre
    [InformationCarrier]>>[Actor]              = hasProductionCentre o hasWorker
    [Potform]>>[Actor]                         = isTypeOf o hasProductionCentre o hasWorker

Two of the three asserted roles point against the chain direction, so every rule
needs at least one inverse. `hasType` / `isTypeOf` was agreed with Allard Mees.
Every role carries a `skos:definition` and a `skos:scopeNote` in the ontology; the
documentation is generated from them.

## Weights and direction

An inverse edge carries the **same** `amt:weight` as its antecedent (the AMT
`InverseRule` copies it), because the weight is the degree of the statement and an
inverse is the same statement read from the other end. All AMT operators are
symmetric, so a derived `>>` and its `<<` carry the same degree too. Shares,
frequencies and normalised alternatives are directional and do not belong in
`amt:weight`. Details: `docs/weights.md`.

## Weights, hextuple and chains

`py/weights.py` computes the weight of a source string by the rule of the source paper,
`amt_weight = 1 / (n_questionmark + n_possibilities)`, and derives the FW type
(`fw:Uncertainty`, `fw:Vagueness`, `fw:FuzzinessWobbliness`) from the pattern of the string
(question mark, AND, OR) for each relation. A statement then is a **hextuple** with the terms of the
[FW ontology](https://github.com/caa-datadragons/FW_Ontology): subject, predicate, object,
`fw:hasDegreeOfConnection` (the same as `amt:weight`), `fw:hasType` and `fw:hasMethod`
(`fw:EqualShareRule`); the source string is kept as `fw:TextEvidence` and linked with `fw:derivedFrom`.
`py/step_chains.py` models three chains from the CHNT data (`data/chains-source.csv`) and runs two
models over them: M1 (this ontology) and M2 (`ontology/variant-b-derived.ttl`, carrier-centre derived
from the actor). It reads its own Turtle back and checks that every statement leads to its string. If
the AMT engine 0.6.0 or newer is installed (`pip install -r requirements.txt`), it also runs the three
models with the engine and compares every edge, type and method included.
`dist/chains-with-model.ttl` can be run with the AMT runner or loaded in the AMT Explorer.
`ontology/fw-implemented-by.ttl` is the one triple (`fw:implementedBy`) that the FW ontology still lacks.

## Run

Windows `cmd`, from the repository root:

    pip install -r requirements.txt

    python main.py

`python main.py --list` shows the steps (`weights`, `reason`, `chains`, `diagrams`, `docs`),
`--only docs` runs one. Output goes to `dist/` (reasoning) and `docs/` (figures and
pages) and is byte-identical from run to run. `docs/` is committed because GitHub
Pages serves it; set Pages to "Deploy from a branch", folder `/docs`.

The `reason` step (toy chain) uses an independent reference reasoner (`py/reference_reasoner.py`,
about sixty lines). If the AMT engine is importable
(`pip install "amt @ git+https://github.com/alpaca-fair-framework/amt-engine.git@v0.6.0"`),
the same step also runs the engine on `dist/mini-amt-with-toy.ttl` and fails if the two disagree on
any edge or weight.

## Placeholders and proposals

* The namespace `mini:` (`http://example.org/mini-amt/`) is not a real IRI.
* The documentation links to the planned home `leiza-scit/CHNT2026-amt`
  (`REPO` in `py/docs_text.py`).
* `amt:logic` of the three role chains is `amt:ProductLogic`, as in the role-chain axioms of
  the source paper. It is a proposal; the toy weights (0.9 / 0.6 / 0.8) are arbitrary.
* `fw:implementedBy` of `fw:EqualShareRule` is not in the FW ontology yet (`ontology/fw-implemented-by.ttl`).
* Role names other than `hasType` / `isTypeOf` are proposals.
* The source model's `ActorEntity` and `Actor` are collapsed into `Actor`.

## Layout

    main.py                    orchestrator (--list, --only, --dry-run)
    requirements.txt
    CHANGELOG.md
    ontology/mini-amt.ttl      the domain model M1, no instances
    ontology/variant-b-derived.ttl   model M2: carrier-centre derived from the actor
    ontology/fw-implemented-by.ttl   the fw:implementedBy triple for fw:EqualShareRule (not read by the code)
    data/toy-chain.ttl         one abstract individual per concept
    data/chains-source.csv     source strings of the three real chains
    data/weight-cases.csv      test cases of the weight rule
    py/                        utils, weights, reference_reasoner, diagram_kit, docs_text, step_*
    docs/                      GitHub Pages: Jekyll shell (source), pages and diagrams (generated)
    dist/                      reasoning output (generated, not committed)
