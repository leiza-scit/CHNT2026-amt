# Changelog

All notable changes are recorded here. Each entry says **what** changed and **why**; the German *Warum* lines are the short rationale for the team.

## [0.4.0] - FW terms, evidence, check against AMT.engine 0.6.0

The hextuples use the terms the FW ontology fixed on 2026-10-30 (`caa-datadragons/FW_Ontology`, `15ae05f`); the proposals `amt:type`, `amt:method` and `nfdi_fw:ReciprocalPossibilityWeight` are gone. AMT.engine 0.6.0 reads the result.

### Added
- **Source string as evidence**: every statement points with `fw:derivedFrom` to a `fw:TextEvidence` node holding the string (`fw:sourceString`). The statements of one string share the node. *Warum:* Die Zeichenkette bleibt exakt erhalten (Reihenfolge, Schreibweise); die Rekonstruktion aus Gewicht und Typ ist nur noch die Gegenprobe.
- **Round-trip check** in step `chains`: `dist/chains.ttl` is read back; every statement must lead to its string, and weight, type and method must be the ones the rule gives.
- **Check against AMT.engine 0.6.0** in step `chains`: the three runs (M1 product, M1 Goedel, M2 product) are repeated with the engine and compared edge by edge, type and method included (340 edges agree). It needs 0.6.0 or newer and is skipped with a note otherwise. The SHACL shapes of the engine are run as information: M2 conforms, M1 has four violations (`mini:reaches` and `mini:reachedBy` have no `rdfs:domain` and `rdfs:range`; open, see PRIMER).
- **`dist/chains-with-model.ttl`**: ontology M1 and the data in one file for the AMT runner and the Explorer.
- **Type and method of derived edges** in `py/reference_reasoner.py`, written from the rules of AMT.engine 0.6.0: a role chain gives its logic as method and the common type of its antecedents (`fw:FuzzinessWobbliness` if they differ); an inverse or a subsumption takes the type and has no method; a missing type counts as `fw:Vagueness`.
- Two cases from the FW ontology in `data/weight-cases.csv` (`Lezoux or Vichy ?` = 0.33, `South Gaul?` = 0.5); 17 cases.
- `ontology/fw-implemented-by.ttl`: the triple `fw:EqualShareRule fw:implementedBy <py/weights.py>` that the FW ontology still lacks.

### Changed
- `dist/chains.ttl` writes `fw:hasDegreeOfConnection` (the same as `amt:weight`), `fw:hasType` with the individuals `fw:Uncertainty`, `fw:Vagueness`, `fw:FuzzinessWobbliness`, and `fw:hasMethod fw:EqualShareRule`. A certain statement has no type; AMT reads that as `fw:Vagueness`. *Warum:* So nennt die FW-Ontologie die Begriffe; Karstens AFE-Daten und Mini-AMT sprechen jetzt dieselbe Sprache.
- The type of AND and OR strings is `fw:Vagueness` (was `VagueValue`), of `?` strings `fw:Uncertainty` (was `UncertainValue`), of both `fw:FuzzinessWobbliness`. Which pattern gives which type is unchanged.
- Pages *Weights* and *Chains*, figure 05, `README.md`, `requirements.txt` (the optional engine line points to `alpaca-fair-framework/amt-engine`, tag `v0.6.0`).

### Removed
- `ontology/fw-method-draft.ttl`: the FW ontology has `fw:EqualShareRule`.

## [0.3.0] - Weight rule, hextuple, three real chains

### Added
- **`py/weights.py`**: the weight rule of the source paper, `1 / (n_questionmark + n_possibilities)`, with the FW type (`UncertainValue`, `VagueValue`, `FuzzinessWobblinessValue`) per pattern and relation, and a lossless round trip from edges back to the string. 15 cases in `data/weight-cases.csv`. *Warum:* Die Berechnung ist klar und soll ausführbar festgehalten sein, auch für den späteren Roundtrip mit den AFE-Daten.
- **Hextuple**: every weighted statement carries `amt:type` and `amt:method` besides the four elements of the quadruple (proposal). `ontology/fw-method-draft.ttl` is the draft of the method resource for the FW ontology.
- **Step `chains`**: three real chains from the CHNT data (`data/chains-source.csv`) as hextuples in `dist/chains.ttl`, reasoned under M1 with product and Goedel and under the new model M2 (`ontology/variant-b-derived.ttl`, carrier-centre derived from the actor). The exported centre weights are checked against the rule. *Warum:* Das Modell zeigt jetzt an echten Fällen, was es ableitet, und macht die Doppelzählung bei geerbten Aussagen sichtbar.
- **Docs**: page *Chains*, sections *How the weight is computed* and *From quadruple to hextuple* on the Weights page, figure `05_chains`, seven new review questions (8 to 14).

### Changed
- `amt:logic` of the three role chains is `amt:ProductLogic` (was the placeholder `amt:GoedelLogic`), as in the role-chain axioms of the source paper. *Warum:* Das Paper nutzt ProductLogic; Gödel bleibt als Vergleich im Chains-Lauf.
- The weight conventions on the Weights page now follow the rule (AND keeps the full weight, OR shares it, a question mark counts as one more possibility); the earlier recommendation of un-normalised alternatives is replaced.

## [0.2.0] - Reasoning properties described, inverses for the derived roles, documentation

### Added
- **Inverses of the derived roles** in `ontology/mini-amt.ttl`: `centreToPotform`, `actorToCarrier`, `actorToPotform` and `reachedBy`, each with an `amt:InverseAxiom`. *Warum:* Eine Assoziation muss von beiden Enden fragbar sein ("welche Zentren gehören zu dieser Potform?" und umgekehrt).
- **`skos:definition` and `skos:scopeNote` on every role.** The definition says what the role says, the scope note what it does not say. *Warum:* Allard soll die Rollen archäologisch lesen und beurteilen können; die Grenzen (Assoziation statt Urheberschaft, keine Zeit) stehen direkt an der Rolle.
- **`docs/`** for GitHub Pages in the pattern of QSKOS: `index`, `model`, `vocabulary`, `reasoning`, `weights`, `review`. Generated by `py/step_docs.py` from the ontology and the reasoning, prose in `py/docs_text.py`. *Warum:* Tabellen und Ableitungen können nicht vom Modell abweichen.
- **Weights page** answering whether `amt:weight` is the same in both directions (yes for inverses; shares and normalised alternatives are directional). *Warum:* Das ist die Grundlage für den späteren Degree-Schritt.
- **Review page** with the archaeological questions that decide the model.
- **Figure `04_reasoning_both`**: the derived roles in both directions.

### Changed
- Figures are written to `docs/diagrams/` instead of `img/`. Figure 02 shows the derived inverses.
- The `reason` step now derives 15 edges on the toy chain (was 9): the four new inverses add six.

## [0.1.0] - First model

- Ontology in the AMT vocabulary: four concepts, three asserted roles with inverses, three role chains, subsumption under `reaches`.
- Toy chain, reference reasoner with optional cross-check against the AMT engine, three figures drawn by Python.
