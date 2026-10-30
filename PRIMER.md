# PRIMER — Mini-AMT (CHNT2026-amt)

Arbeitsplan für das Repository `leiza-scit/CHNT2026-amt`. Wird in jedem Chat hochgeladen, am Ende des Chats
zurückgeschrieben. Dieses Dokument ist deutsch; alles andere im Repository ist britisches Englisch.

---

## Teil A — Immer gültig

### A1 Ausgangslage

| Was | Wo | Rolle |
|---|---|---|
| Mini-AMT-Ontologie, Reasoning, Docs, Ketten | dieses Repository | Ziel |
| `n4o-rse/amt-engine`, `n4o-rse/amt-runner` | GitHub | Engine und Runner; Quelle für den späteren Viewer |
| `leiza-scit/CAA2026-amt` | GitHub | Vorbild für Viewer und Docs |
| `caa-datadragons/FW_Ontology` | GitHub | `nfdi_fw:`-Klassen; soll die Methode (`amt:method`) aufnehmen |
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
- Die AMT-Engine wurde in diesen Chats **nie ausgeführt**; die SHACL-Validierung gegen `amt-shapes.ttl` ist **nicht gelaufen**.

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
| Hextupel | `amt:type` und `amt:method` zusätzlich zum Quadrupel; Methode wird in `caa-datadragons/FW_Ontology` beschrieben und verlinkt | 2026-10-30 |
| Namen `amt:type`, `amt:method`, `nfdi_fw:ReciprocalPossibilityWeight`, `nfdi_fw:WeightMethod` | Vorschlag | Vorschlag |
| Logik der Rollenketten | `ProductLogic` wie im Paper | Vorschlag |
| Modell M1 (Träger–Zentrum asserted) oder M2 (aus dem Actor abgeleitet) | M1 bleibt Hauptmodell, bis Allard geantwortet hat | Vorschlag |
| Typ-Klassen | die Basisklassen (`VagueValue` usw.), nicht die `…ResourceValue`-Unterklassen | Vorschlag |
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
| S5 | Methode und `amt:type` / `amt:method` in die FW-Ontologie | FW_Ontology | S3 | offen |
| S6 | Alle Potter und Träger als Hextupel (Export → `dist/`) | CHNT2026-amt | S4 | offen |
| S7 | Viewer, angepasst aus amt-engine und amt-runner | CHNT2026-amt | S6 | offen |
| S8 | Notebook (quarto-live) | CHNT2026-amt | S6 | offen |
| S9 | Engine-Abgleich und SHACL-Validierung | CHNT2026-amt | S3 | offen |

S5 und S9 sind unabhängig von S4 und können in beliebiger Reihenfolge laufen. S6 bis S8 warten auf die Entscheidung in S4.

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

## S5 — FW-Ontologie

**Ziel:** Die Methode ist im FW-Repository beschrieben und per w3id auflösbar; `amt:type` und `amt:method` stehen mit Definition dort oder im AMT-Vokabular.

**Uploads:** das FW-Repository als Bündel.

**Abnahme:** Die Klasse und die Methode erscheinen in der pyLODE-Dokumentation; die IRI im Hextupel löst auf.

## S6 bis S9

Werden vor dem Start ausgearbeitet (Ziel, Uploads, Abnahme), sobald S4 entschieden ist.

---

## Teil D — Offene Punkte

- Sind die `…ResourceValue`-Klassen der FW-Ontologie die richtigen Typen für Objekte, die Ressourcen sind? Heute: Basisklassen (A4).
- Soll die Originalzeichenkette als siebtes Element oder als Eigenschaft der Aussage mitlaufen, falls die Reihenfolge der Entitäten zählt?
- Regionen und Gruppen ohne Zentrumsknoten (9.033 Strings): eigene Klasse oder weglassen?
- LICENSE, `CITATION.cff` und eine `RELEASE`-Konstante fehlen noch; mit dem ersten Zenodo-Release nachziehen.
- Namespace `mini:` ist ein Platzhalter; persistente IRI per w3id klären.
- Eine IRI-Landkarte (A6) entsteht, sobald RDF veröffentlicht wird.
