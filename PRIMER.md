# PRIMER — Mini-AMT (CHNT2026-amt)

Arbeitsplan für das Repository `leiza-scit/CHNT2026-amt`. Wird in jedem Chat hochgeladen, am Ende des Chats
zurückgeschrieben. Dieses Dokument ist deutsch; alles andere im Repository ist britisches Englisch.

---

## Teil A — Immer gültig

### A1 Ausgangslage

| Was | Wo | Rolle |
|---|---|---|
| Mini-AMT-Ontologie, Reasoning, Docs, Ketten | dieses Repository | Ziel |
| `alpaca-fair-framework/amt-engine`, `alpaca-fair-framework/amt-runner` | GitHub | Engine (0.6.0) und Runner (0.5.0); Quelle für den späteren Viewer; ehemals `n4o-rse` |
| `leiza-scit/CAA2026-amt` | GitHub | Vorbild für Viewer und Docs |
| `caa-datadragons/FW_Ontology` | GitHub | `fw:`-Begriffe: Typ-Individuen, `fw:EqualShareRule`, Evidenz (Stand `15ae05f`) |
| `n4o-rse/oer-001-sparqling-archaeology` (`notebooks_amt`) | GitHub | Vorbild für das Notebook |
| CHNT-Exporte (Samian-Daten, `ct_ic_pc`) | lokal, nicht im Repository | Quelle der Zeichenketten und Gewichte |

**Befunde** (geprüft 2026-10-30):

- Der Zentrums-String ist ein Attribut des **Potters**, nicht des Trägers: alle 1.375 Potter der Zentrums-Exporte
  haben genau einen String, und bei den verglichenen 1.072 Potters haben alle Träger identische Kanten. Das Paper sagt
  dasselbe (Ansatz B „folgt aus“ Ansatz A).
- Die Gewichtsformel des Papers `1 / (n_? + n_Möglichkeiten)` stimmt für **alle 95.819** vorhandenen Zentrumskanten
  in `ct_ic_pc`. 9.033 von 45.685 Zentrums-Strings haben weniger Zentrumsknoten als Entitäten (Regionen, Gruppen,
  fehlende Zuordnung): Lücke in der Abdeckung, kein Gewichtsfehler.
- Potform-Strings tragen im Export keine Gewichte, nur Text. Die Regel gilt dort nach dem Paper (Abb. 6: 0.33).
- Das Paper rechnet die Rollenketten mit `ProductLogic` (Listings 5 und 6). Listing 6 beginnt mit `(PF)` an einer
  Stelle, an der `(AE)` zu erwarten wäre; vermutlich ein Tippfehler.
- Unter Product zählt Modell M1 eine vom Potter geerbte Unsicherheit doppelt: Ve- i, `carrierToActor` 0.25 (Product)
  gegen 0.5 (Gödel).
- 2.777 Träger haben einen unsicheren Potternamen (OR im Namen): die Träger-Potter-Verknüpfung von M2 ist nicht immer scharf.
- **FW-Ontologie angepasst** (`caa-datadragons/FW_Ontology`, Commit `15ae05f`, 2026-10-30), das ändert die Hextupel-Namen:
  `fw:hasDegreeOfConnection` (äquivalent zu `amt:weight`), `fw:hasType` mit **Individuen** `fw:Uncertainty`, `fw:Vagueness`,
  `fw:FuzzinessWobbliness` (Klasse `fw:FW_Type`), `fw:hasMethod` mit `fw:EqualShareRule` (`fw:formula "1 / (n_question + n_possibilities)"`,
  `fw:implementedBy` steht noch aus), und die Quellzeichenkette als `fw:TextEvidence` (`fw:sourceString`) über `fw:derivedFrom`; ein
  Evidenzknoten kann sich die Alternativen eines OR teilen. `fw:UncertainValue` und `fw:VagueValue` sind Unterklassen von
  `fw:FuzzinessWobblinessValue`. Die Beispiele der FW-Ontologie bestätigen die Zuordnung Muster → Typ (`Lezoux or Vichy ?` = 0,33, FW;
  `South Gaul?` = 0,5, Unsicherheit). Die AMT-Logiken stehen dort als `fw:PropagationMethod` (Vorschlag `data/amt-alignment.ttl`, gehört
  in `amt.ttl` der Engine).
- **Engine 0.6.0 ausgeführt** (2026-10-30, S3a): `python main.py` vergleicht die drei Läufe (M1 Product, M1 Gödel, M2 Product, 340 Kanten) mit dem Referenz-Reasoner in Gewicht, Typ und Methode: gleich. Die Engine liest `fw:hasDegreeOfConnection`, `fw:hasType`, `fw:hasMethod` und `fw:derivedFrom` ohne `amt:weight`.
- **SHACL** (Shapes der Engine, `validate_against_shapes`): M2 entspricht den Shapes; **M1 hat vier Verstöße**, alle bei den Oberrollen `mini:reaches` und `mini:reachedBy`: sie haben weder `rdfs:domain` noch `rdfs:range` (die Shapes verlangen je genau eines). Die Oberrolle fasst `potformToCentre`, `carrierToActor` und `potformToActor` zusammen, die verschiedene Concepts verbinden; ein einzelnes Domain/Range gibt es dafür nicht. Der Runner bricht deshalb bei `dist/chains-with-model.ttl` in der Validierung ab. Offen (S9).

### A2 Zielbild

```
CHNT-Strings ──► py/weights.py ──► Hextupel (dist/chains.ttl) ──► Reasoner ──► docs/ (GitHub Pages)
 (data/*.csv)    Gewicht, FW-Typ,     s p o weight type method     M1 / M2        Viewer, Notebook
                 Methode
```

Eigenschaften, die das Ergebnis haben muss:

1. Jedes Gewicht in `dist/` ist aus einer Quellzeichenkette durch `py/weights.py` berechnet; der Selbsttest schlägt bei Abweichung fehl.
2. Aus den Hextupeln lässt sich die Quellzeichenkette bis auf Reihenfolge und Schreibweise zurückbauen (Roundtrip).
3. Docs und Grafiken entstehen nur aus Ontologie, Daten und Reasoning; nichts ist von Hand geschrieben, was daraus folgt.
4. Zwei Läufe von `python main.py` hintereinander ändern keine Datei.

### A3 Querschnittsregeln

- Rohdaten bleiben unverändert und liegen nicht im Repository (nur kleine Auszüge in `data/`).
- Kein `datetime.now()` in Generatoren; Ausgabe ist deterministisch (siehe Abnahme von S3).
- **Zwei Läufe, `git status` bleibt sauber.**
- Netzwerkzugriff nur in einem eigenen Schritt; keiner der heutigen Schritte braucht ihn.
- `main.py` ist der einzige Einstieg; jeder Schritt läuft auch einzeln.
- Kein Chat ändert zwei Schritte gleichzeitig. Lieferung als Patch-ZIP (`patch-zip-delivery`), `PATCH-README.md` nennt den Schritt.
- Befehle für Windows `cmd`, je eine Zeile. Änderungen am Repository nur über Patch-ZIP, nur Quellen.

### A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Name der Rolle Träger → Potform | `hasType`, invers `isTypeOf` (mit Allard Mees geklärt) | vor 2026-10-30 |
| Diagramme | „mermaid-like“, mit Python gezeichnet; Farben nach dem AMT-Schema | 2026-10-30 |
| Ist `amt:weight` in beide Richtungen gleich? | Ja bei Inversen; Anteile und Häufigkeiten gehören nicht in `amt:weight` | 2026-10-30 |
| Wie wird das Gewicht berechnet? | `1 / (n_? + n_Möglichkeiten)`, zwei Nachkommastellen; AND behält volles Gewicht, OR teilt, `?` zählt als eine Möglichkeit | 2026-10-30 |
| Zuordnung FW-Typ je Muster | `?` → `UncertainValue`; OR oder AND → `VagueValue`; `?` mit OR oder AND → `FuzzinessWobblinessValue` (Flo) | 2026-10-30 |
| Erwartete Muster je Relation | Träger–Potform: OR, `?`, `?`+OR; Actor–Zentrum: OR, AND, `?`+AND, `?`; Träger–Zentrum: `?` (Flo) | 2026-10-30 |
| Hextupel | Quadrupel plus Typ und Methode; Methode wird in `caa-datadragons/FW_Ontology` beschrieben und verlinkt | 2026-10-30 |
| Namen für Gewicht, Typ, Methode, Evidenz | `fw:hasDegreeOfConnection` (≡ `amt:weight`), `fw:hasType` (Individuen `fw:Uncertainty` / `fw:Vagueness` / `fw:FuzzinessWobbliness`), `fw:hasMethod` (`fw:EqualShareRule`), optional `fw:derivedFrom` (`fw:TextEvidence`). Hinfällig: die Vorschläge `amt:type`, `amt:method`, `nfdi_fw:ReciprocalPossibilityWeight` und `nfdi_fw:WeightMethod`; die FW-Ontologie hat es am 2026-10-30 anders festgelegt. Mini-AMT zieht in S3a nach | 2026-10-30 |
| Methode und Typ abgeleiteter Kanten | wie in AMT.engine 0.6.0: Rollenkette setzt die Logik als `fw:hasMethod` (`amt:ProductLogic` usw.) und als Typ den gemeinsamen Typ der Vorderglieder, bei Unterschied `fw:FuzzinessWobbliness`; Inverse und Subsumtion übernehmen den Typ und haben keine Methode; kein Typ gilt als `fw:Vagueness`; der Referenz-Reasoner bildet das nach und wird gegen die Engine geprüft | 2026-10-30 |
| Typ einer sicheren Aussage (Muster `certain`) | kein `fw:hasType` geschrieben; AMT liest das als `fw:Vagueness` (Standard der Engine seit 0.6.0) | 2026-10-30 |
| Gewicht im Hextupel | `fw:hasDegreeOfConnection` (die Engine liest es wie `amt:weight`); beide zusammen werden nicht geschrieben | 2026-10-30 |
| Evidenzknoten | ein `fw:TextEvidence`-Knoten je Quellzeichenkette (`mini:ev_<potform\|centre>_<slug>`, `?` als `_q`), von allen Aussagen der Zeichenkette über `fw:derivedFrom` geteilt | 2026-10-30 |
| Logik der Rollenketten | `ProductLogic` wie im Paper | Vorschlag |
| Modell M1 (Träger–Zentrum asserted) oder M2 (aus dem Actor abgeleitet) | M1 bleibt Hauptmodell, bis Allard geantwortet hat | Vorschlag |
| Typ-Klassen | hinfällig: der Typ einer Aussage ist ein Individuum von `fw:FW_Type`, keine Klasse (FW-Ontologie, 2026-10-30) | 2026-10-30 |
| Sprache | PRIMER und Memos deutsch, Repository englisch | 2026-10-30 |

### A5 Was in welchem Chat hochgeladen wird

Das Repository als Bündel (ohne Erzeugtes), dazu `PRIMER.md`:

```
robocopy . %TEMP%\mini-amt-bundle /E /XD .git .venv dist __pycache__ docs\diagrams
```

```
powershell -Command "Compress-Archive -Path $env:TEMP\mini-amt-bundle\* -DestinationPath mini-amt-bundle.zip -Force"
```

Nicht hochladen: `.git/`, `.venv/`, `dist/`, die CHNT-Exporte (nur bei Schritten, die sie brauchen, und dann einzeln).

---

## Teil B — Schrittübersicht

| ID | Schritt | Repo | hängt ab von | Status |
|---|---|---|---|---|
| S1 | Modell, Ontologie, Referenz-Reasoner, vier Grafiken (0.1.0) | CHNT2026-amt | | erledigt 2026-10-30 |
| S2 | Reasoning-Rollen mit Inversen, Docs für GitHub Pages, Gewichtsrichtung (0.2.0) | CHNT2026-amt | S1 | erledigt 2026-10-30 |
| S3 | Gewichtsregel, Hextupel, drei echte Ketten, Modell M2 (0.3.0) | CHNT2026-amt | S2 | erledigt 2026-10-30 |
| S4 | Entscheidung M1 / M2 und Logik nach der Prüfung durch Allard | CHNT2026-amt | S3 | offen |
| S3a | Mini-AMT an die FW-Ontologie anpassen (Namen, Typ-Individuen, Methode, Evidenz) | CHNT2026-amt | S3 | erledigt 2026-10-30 (0.4.0) |
| S5 | Methode und Typen in der FW-Ontologie | FW_Ontology | S3 | FW-Seite erledigt 2026-10-30; `fw:implementedBy` offen (Triple liegt in `ontology/fw-implemented-by.ttl`) |
| S10 | Hextupel in amt-engine und amt-runner einlesen und durchreichen | amt-engine, amt-runner | S3a | erledigt 2026-10-30 (Engine 0.6.0, Runner 0.5.0; in den Primern dort S19 bis S23) |
| S6 | Alle Potter und Träger als Hextupel (Export → `dist/`) | CHNT2026-amt | S4 | offen |
| S7 | Viewer, angepasst aus amt-engine und amt-runner | CHNT2026-amt | S6 | offen |
| S8 | Notebook (quarto-live) | CHNT2026-amt | S6 | offen |
| S9 | Engine-Abgleich und SHACL-Validierung | CHNT2026-amt | S3 | Abgleich erledigt 2026-10-30 (mit S3a); SHACL: M1 hat vier Verstöße (Teil D) |

S5 und der SHACL-Teil von S9 sind unabhängig von S4. S6 bis S8 warten auf die Entscheidung in S4.

---

## Teil C — Die Schritte

## S3 — Gewichtsregel, Hextupel, drei echte Ketten

**Ziel:** Gewicht, FW-Typ und Methode jeder Aussage werden aus der Quellzeichenkette berechnet; drei echte Ketten laufen durch zwei Modelle.

**Uploads:** Paper „How to handle vagueness and uncertainty“; die CHNT-Exporte nur für die Prüfung der Kantengewichte.

Inhalt: `py/weights.py`, `data/weight-cases.csv`, `data/chains-source.csv`, `py/step_chains.py`, `ontology/variant-b-derived.ttl`,
`ontology/fw-method-draft.ttl`, Grafik 05, Seite *Chains*, Abschnitte auf der Seite *Weights*, Review-Fragen 8 bis 14.

**Abnahme:** `python main.py` läuft durch; `python py/weights.py` meldet „15 cases agree“; zwei Läufe hintereinander ändern keine Datei in `docs/` und `dist/`;
die exportierten Zentrumsgewichte der vier Träger stimmen mit der Regel überein (sonst bricht `step_chains` ab).

### Erledigt 2026-10-30

- Regel gegen alle Zentrumskanten geprüft: 95.819 von 95.819 stimmen. Die Lücken (9.033 von 45.685 Strings) sind Abdeckung, kein Gewichtsfehler.
- Ketten: A Vitalis viii (AND, `32?`), B Onnio- (OR, `18/31?`), C Ve- i (OR mit drei Formen, AND mit `?`).
- Unter Product zählt M1 die Unsicherheit am Potter doppelt (Ve- i `carrierToActor` 0.25 gegen 0.5 unter Gödel); M2 nicht.
- Der Roundtrip vom Hextupel zur Zeichenkette ist verlustfrei bis auf Reihenfolge und Schreibweise der Entitäten.
- Nicht geprüft: Engine-Abgleich (Engine nicht installiert) und SHACL-Validierung.

## S4 — Entscheidung M1 / M2 und Logik

**Ziel:** Ein Modell, eine Logik, dokumentiert in A4.

**Abnahme:** A4 enthält Beschluss und Datum; die Ontologie entspricht dem Beschluss; Review-Seite aktualisiert.

## S3a — Mini-AMT an die FW-Ontologie anpassen

**Ziel:** Hextupel, Quellen und Dokumentation benutzen die Begriffe der FW-Ontologie statt meiner Vorschläge.

**Uploads:** `PRIMER.md`, das Repository als Bündel, die aktuelle FW-Ontologie (`ontology/nfdi_fw_ontology.owl`).

Inhalt:

- `py/weights.py`: `FW_TYPE` liefert die Individuen `Uncertainty`, `Vagueness`, `FuzzinessWobbliness` (Zuordnung der Muster bleibt); die Methode heißt `EqualShareRule`.
- `py/step_chains.py`: `dist/chains.ttl` schreibt `fw:hasDegreeOfConnection`, `fw:hasType`, `fw:hasMethod` und je Quellzeichenkette einen `fw:TextEvidence`-Knoten (`fw:sourceString`), den sich die Aussagen einer Zeichenkette über `fw:derivedFrom` teilen. Das beantwortet Review-Frage 14 (Reihenfolge und Schreibweise bleiben erhalten).
- Der Roundtrip-Test liest zusätzlich die Zeichenkette aus dem Evidenzknoten; die Rekonstruktion aus Gewicht, Typ und Kantenzahl bleibt als Gegenprobe.
- `ontology/fw-method-draft.ttl` entfällt; `fw:implementedBy` bekommt die IRI von `py/weights.py` (Datei im Repository oder Release).
- Seiten *Weights*, *Chains*, *Review* und die Grafik 05 nennen die neuen Begriffe; `README.md` und `CHANGELOG.md` auch.

**Abnahme:** `python main.py` läuft durch; `dist/chains.ttl` enthält kein `amt:type` und kein `amt:method` mehr; der Selbsttest prüft, dass jede Aussage einer Zeichenkette denselben Evidenzknoten hat und dass Gewicht, Typ und Methode zu den Beispielen der FW-Ontologie (`Lezoux or Vichy ?` = 0,33, `South Gaul?` = 0,5) passen; zwei Läufe ändern keine Datei.

### Erledigt 2026-10-30 (S3a, Version 0.4.0)

- `py/weights.py`: Typ-Individuen `Uncertainty`, `Vagueness`, `FuzzinessWobbliness`; Methode `EqualShareRule`; `IMPLEMENTED_BY`; die Nutzlast jeder Kante nennt die Quellzeichenkette. `data/weight-cases.csv` hat 17 Fälle (neu: die beiden Beispiele der FW-Ontologie).
- `py/step_chains.py`: `dist/chains.ttl` mit `fw:`-Präfix, `fw:hasDegreeOfConnection`, `fw:hasType`, `fw:hasMethod`, `fw:derivedFrom` und je Zeichenkette einem `fw:TextEvidence`-Knoten. Neu: `check_roundtrip` (die Datei wird zurückgelesen: jede Aussage führt zu ihrer Zeichenkette; Gewicht, Typ, Methode stimmen mit der Regel; Gegenprobe aus Gewicht, Typ und Kantenzahl), `dist/chains-with-model.ttl` (Ontologie M1 plus Daten, für Engine und Runner), `engine_check` (drei Läufe mit der Engine, Kante für Kante inklusive Typ und Methode; ab Engine 0.6.0, sonst übersprungen mit Hinweis; dazu die SHACL-Prüfung als Information).
- `py/reference_reasoner.py`: Typ und Methode abgeleiteter Kanten nach der Regel der Engine (Beschlusslage oben), unabhängig geschrieben.
- `ontology/fw-method-draft.ttl` entfällt; `ontology/fw-implemented-by.ttl` hält das eine Triple `fw:EqualShareRule fw:implementedBy <…/py/weights.py>` für die FW-Ontologie.
- Seiten *Weights* und *Chains*, Grafik 05, `README.md`, `CHANGELOG.md`, `requirements.txt` (Engine-Zeile jetzt `alpaca-fair-framework`, ab `v0.6.0`).
- Geprüft (Linux, Python 3.13.18, Engine 0.6.0 aus dem Klon): `python main.py` zweimal, Status stabil; 340 Kanten gleich; der Rückweg liest 20 Aussagen. Mit einer installierten Engine 0.5.0 meldet der Schritt, dass er mindestens 0.6.0 braucht, und überspringt den Abgleich (0.5.0 liest die `fw:`-Begriffe nicht und würde sonst alle Kanten als fehlend melden).
- Nicht geprüft: Windows; ob die Grafiken 01 bis 04 dort unverändert bleiben (matplotlib erzeugt auf anderen Versionen andere Bytes).

## S5 — FW-Ontologie

**Stand 2026-10-30:** Die FW-Seite ist erledigt (Commit `15ae05f`): `fw:hasType`, `fw:hasMethod`, `fw:formula`, `fw:implementedBy`, Evidenzklassen, `fw:EqualShareRule`. Offen ist nur `fw:implementedBy` für die Gewichtsregel; die IRI liefert S3a.

## S6 bis S9

Werden vor dem Start ausgearbeitet (Ziel, Uploads, Abnahme), sobald S4 entschieden ist.

---

## Teil D — Offene Punkte

- **SHACL M1**: `mini:reaches` und `mini:reachedBy` brauchen je ein `rdfs:domain` und ein `rdfs:range`, sonst entspricht M1 den Shapes der Engine nicht und der Runner bricht ab. Möglichkeiten: ein gemeinsames Oberconcept als Domain und Range (zum Beispiel `mini:Entity`); die Oberrolle und ihre drei Subsumtionen weglassen; oder die Shapes der Engine für Oberrollen lockern (Änderung in `amt-engine`). Das ist eine Modellentscheidung; mit S4 klären.
- `fw:implementedBy`: das Triple liegt bereit; an die FW-Ontologie weitergeben, mit einer Release- oder Zenodo-IRI statt des Branch-Links, sobald es eine gibt.
- Typ abgeleiteter Kanten ist geklärt (A4), aber noch nicht mit Allard besprochen (Frage 9 der Review-Seite): eine abgeleitete Kante, deren Vorderglieder Unsicherheit und Vagheit mischen, bekommt `fw:FuzzinessWobbliness`.
- Regionen und Gruppen ohne Zentrumsknoten (9.033 Strings): eigene Klasse oder weglassen?
- LICENSE, `CITATION.cff` und eine `RELEASE`-Konstante fehlen noch; mit dem ersten Zenodo-Release nachziehen.
- Namespace `mini:` ist ein Platzhalter; persistente IRI per w3id klären.
- Eine IRI-Landkarte (A6) entsteht, sobald RDF veröffentlicht wird.
