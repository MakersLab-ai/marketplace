---
name: destillar
description: >
  This skill should be used when the user asks about "Philipp Maderthaner",
  "Philipps Wissen", "Destillar", "Wissensgraph", "Destillar abfragen",
  "Content erstellen aus Destillar", "Content-Ideen", "Ideen", "IdeaCard",
  "Idee generieren", or wants to create articles, blog posts, newsletters,
  or any content based on Philipp Maderthaner's expertise. Also triggers
  for topics in Philipp's domain: "Führung", "Unternehmertum", "Delegation",
  "Skalierung", "Teamführung", "Pricing", "Kommunikation", "Mindset",
  "Persönlichkeitsentwicklung" — when the user wants content grounded in
  his specific knowledge rather than general information.
version: 0.4.0
---

# Destillar — Philipp Maderthaners Wissensgraph

Philipp Maderthaners gesamtes Wissen — aus Podcasts, Seminaren, Büchern und Dokumenten — ist in einem Wissensgraph strukturiert und über Destillar abfragbar. Verwende die MCP-Tools des `destillar`-Servers, um auf dieses Wissen zuzugreifen.

## Verfügbare MCP-Tools

**Wissensgraph:**

| Tool | Beschreibung |
|------|-------------|
| `query_knowledge_base` | Semantische Suche im Wissensgraph |
| `list_sources` | Alle Quellen auflisten (Podcasts, Seminare, Dokumente) |
| `get_source` | Details einer bestimmten Quelle abrufen (braucht `source_id` aus `list_sources`) |
| `get_graph_stats` | Statistiken zum Wissensgraph |

**Content-Ideas (IdeaCards):**

| Tool | Beschreibung |
|------|-------------|
| `generate_content_ideas` | Content-würdige Subgraphs finden und als IdeaCards persistieren |
| `list_content_ideas` | Persistierte IdeaCards mit Filtern auflisten (Status, Format, Topic) |
| `get_content_idea` | Eine einzelne IdeaCard inkl. verknüpfter Entities abrufen |
| `update_content_idea_status` | Lifecycle-Status einer IdeaCard setzen |

### query_knowledge_base — Parameter

| Parameter | Typ | Required | Default | Beschreibung |
|-----------|-----|----------|---------|-------------|
| `question` | string | ja | — | Suchanfrage in natürlicher Sprache |
| `top_k` | integer | nein | 3 | Anzahl der Top-Ergebnisse (Sub-Graphs) |
| `include_chunks` | boolean | nein | false | Original-Textstellen mitliefern |

**Achtung: Das sind die einzigen verfügbaren Parameter.** Es gibt aktuell keine Parameter für Graph-Tiefe, Similarity-Threshold oder Synthese.

## Grundprinzip

Destillar liefert **strukturiertes Rohmaterial**, nicht fertige Antworten. Du erhältst:

- **Entities** (Wissensbausteine): Fragen, Einsichten, Illustrationen, Methoden
- **Relationen** zwischen Entities: ANSWERED_BY, ILLUSTRATES, IMPLEMENTED_BY, HAS_SUBSTEP, RELATES_TO
- **Source Chunks** (wenn `include_chunks: true`): Original-Textstellen mit Quellverweis

Deine Aufgabe: aus diesen Bausteinen hochwertige, quellengestützte Inhalte synthetisieren.

## Umgang mit großen Ergebnissen

Die Ergebnisse können sehr groß sein (50K–500K Zeichen), weil jeder Entry-Node über Relationen Dutzende weitere Nodes lädt. Das kann das Token-Limit sprengen. Daher:

### Ergebnisgröße minimieren

1. **Immer mit `top_k: 1` starten.** Erst wenn das Ergebnis überschaubar ist, schrittweise erhöhen.
2. **`include_chunks: false` als Default.** Chunks nur anfordern, wenn konkrete Zitate benötigt werden — und dann nur für eine gezielte Nachfolge-Query mit `top_k: 1`.
3. **Lieber viele kleine Queries als eine große.** Statt `top_k: 5` für ein breites Thema besser 5 einzelne Queries mit `top_k: 1` zu verschiedenen Aspekten stellen.

### Wenn Ergebnisse abgeschnitten werden

Falls ein Ergebnis das Token-Limit überschreitet und in eine temporäre Datei geschrieben wird:
- Die Datei nicht versuchen komplett einzulesen
- Stattdessen die Query mit `top_k: 1` und `include_chunks: false` wiederholen
- Für Zitate danach eine gezielte Nachfolge-Query mit `include_chunks: true` und `top_k: 1` stellen

## Query-Strategien

### Fokussierte Einzelabfrage (empfohlen)
Für die meisten Anwendungsfälle: präzise Frage, minimale Ergebnisgröße.

```
question: "Wie delegiert man als Führungskraft ohne Kontrollverlust?"
top_k: 1
include_chunks: false
```

### Breite Recherche (iterativ)
Für Überblick über ein Thema: mehrere kleine Queries statt einer großen.

```
# Schritt 1: Überblick
question: "Delegation"
top_k: 1

# Schritt 2: Basierend auf den Ergebnissen fokussieren
question: "Delegation und Vertrauen aufbauen"
top_k: 1

# Schritt 3: Zitate holen für die besten Entities
question: "Delegation und Vertrauen aufbauen"
top_k: 1
include_chunks: true
```

### Mehrere Queries kombinieren
Für Content-Erstellung oft mehrere Queries hintereinander stellen:
1. Übersichts-Query zum Thema (`top_k: 1`) → Kernentities identifizieren
2. Fokussierte Queries zu Unter-Aspekten (`top_k: 1`) → Details holen
3. Gezielte Queries mit `include_chunks: true` → Zitate für die besten Treffer

## Content-Erstellung

### Grundregeln

1. **Immer mit Quellverweisen arbeiten.** Jede Aussage, die auf Philipps Wissen basiert, muss auf einen Source Chunk referenzieren. Nenne die Quelle (z.B. "Podcast Episode 42", "Seminar Q3 2024").

2. **Nicht halluzinieren.** Wenn Destillar keine Informationen zu einem Thema liefert, sage das offen. Erfinde keine Aussagen und schreibe sie Philipp zu.

3. **Entities als Bausteine nutzen.** Jede Entity hat einen Typ:
   - **Einsicht (insight)**: Kernaussage, Prinzip → gut als Hauptthese oder Abschnittskern
   - **Methode (method)**: Framework, Vorgehen → gut als How-to-Abschnitt
   - **Illustration**: Analogie, Metapher, Geschichte → gut als Aufhänger oder Erklärung
   - **Frage (question)**: Häufige Frage → gut als Strukturelement oder Einstieg

4. **Relationen nutzen.** Die Verbindungen zwischen Entities zeigen, wie Ideen zusammenhängen:
   - ANSWERED_BY: Eine Frage wird durch eine Einsicht/Methode beantwortet
   - ILLUSTRATES: Eine Illustration veranschaulicht ein Konzept
   - IMPLEMENTED_BY: Eine Methode setzt ein Konzept um
   - HAS_SUBSTEP: Teil-Schritte einer Methode

5. **Tonfall flexibel halten.** Je nach Format:
   - Blog-Artikel: Direkter, motivierender Stil à la Philipp
   - Newsletter: Persönlich, mit einem konkreten Takeaway
   - Deep-Dive PDF: Strukturiert, mit Frameworks und Quellenapparat
   - Social Media: Kurz, provokant, eine starke These

### Content-Workflow

1. **Thema klären**: Was genau soll der Inhalt abdecken?
2. **Destillar abfragen**: Mehrere kleine Queries (`top_k: 1`, `include_chunks: false`), thematisch gestaffelt
3. **Material sichten**: Welche Entities sind am relevantesten?
4. **Zitate holen**: Gezielte Nachfolge-Queries mit `include_chunks: true` für die besten Treffer
5. **Struktur planen**: Roter Faden basierend auf den gefundenen Entities
6. **Schreiben**: Entities als Bausteine verwenden, Quellen einbauen
7. **Prüfen**: Stimmen alle Aussagen mit den Destillar-Ergebnissen überein?

## Content-Ideas-Workflow

Neben der freien Query-Recherche kann Destillar **automatisch Content-Ideen** vorschlagen. Diese werden als **IdeaCards** persistiert und haben einen Lebenszyklus.

### IdeaCard-Anatomie

Eine IdeaCard ist ein strukturierter Content-Vorschlag mit:

- **`title`**, **`hook`**, **`description`** — der redaktionelle Pitch
- **`alt_hooks`** — alternative Aufhänger
- **`outline`** — Gliederungspunkte
- **`format`** — `article` | `post` | `carousel`
- **`storyline`** — `how_to` | `contrarian` | `case_study` | `framework_explainer` | `story_hook` | `listicle`
- **`seed_reason`** — warum diese Idee aus dem Graph gepickt wurde (siehe unten)
- **`language`** — meist `"de"`
- **`score`** — Relevanz-/Qualitätsschätzung
- **`entities`** — verknüpfte Wissensgraph-Entities, jeweils mit einer **Rolle** (siehe unten)
- **`status`** — Lifecycle-State

### Lifecycle-States

| Status | Bedeutung | Wird gesetzt wenn… |
|---|---|---|
| `pending` | Neu generiert, unsortiert | Initial nach `generate_content_ideas` |
| `accepted` | Vom User für später vorgemerkt | User entscheidet „gute Idee, aber nicht jetzt" |
| `dismissed` | Verworfen | User will nicht |
| `drafted` | Es existiert ein Content-Entwurf dazu | Nach erfolgreichem Draft im `/destillar-content`-Workflow |

Statuswechsel erfolgt immer über `update_content_idea_status`.

### Seed Reasons (warum wurde die Idee gepickt?)

| Seed | Bedeutung |
|---|---|
| `framework_chain` | Mehrere Methoden/Frameworks verbinden sich zu einem Prozess |
| `cross_source_insight` | Dieselbe Einsicht taucht in mehreren Quellen auf → hohe Konfidenz |
| `story_dense` | Entity-Cluster mit vielen Illustrationen/Analogien → gut erzählbar |
| `unused_core` | Zentrale Einsicht, die in keiner bisherigen Idee vorkommt |
| `topic_targeted` | Gezielt auf vom User spezifiziertes `topic` fokussiert |

Der Seed ist ein **Qualitätssignal**. `cross_source_insight` und `framework_chain` sind typischerweise die stärksten.

### Entity-Rollen in einer IdeaCard

Jede verknüpfte Entity hat eine **Rolle**, die sagt, wie sie im Content verwendet werden soll:

| Rolle | Verwendung beim Schreiben |
|---|---|
| `hook` | Aufhänger am Anfang — provokante Frage, überraschende Statistik, Analogie |
| `core_insight` | Hauptthese / zentrale Aussage |
| `substep` | Ein Teilschritt einer Methode — gut in How-to-Abschnitten |
| `illustration` | Beispiel, Metapher, Geschichte — veranschaulicht das Konzept |
| `payoff` | Abschluss / Takeaway / Call to Action |

Beim Drafting die Rollen respektieren: ein `hook`-Entity gehört an den Anfang, `payoff` ans Ende.

### Typischer Workflow

1. **Generieren:** `generate_content_ideas(topic?, format?, count=5)` — Destillar findet Subgraphs und formt sie.
2. **Kuratieren:** IdeaCards mit `list_content_ideas(status="pending")` durchsehen. Schlechte mit `update_content_idea_status(status="dismissed")` aussortieren, starke mit `accepted` markieren.
3. **Drafting starten:** Eine IdeaCard mit `get_content_idea` vollständig laden, Draft schreiben (via `/destillar-content`).
4. **Abschluss:** Nach erfolgreichem Draft Status auf `drafted` setzen.

### Wann welches Tool?

- **Frage → Antwort:** `query_knowledge_base` (direkte Recherche)
- **„Worüber soll ich schreiben?" → mehrere Vorschläge:** `generate_content_ideas`
- **Vorgemerkte Ideen ansehen:** `list_content_ideas` mit passendem Status-Filter
- **Idee in Content umsetzen:** `get_content_idea` → Draft → Status `drafted`

## Verfügbare Themen (Taxonomy)

Für eine Übersicht der Themen, die in Destillar abgedeckt sind, siehe `references/taxonomy.md`.

## API-Response verstehen

Die Query-API liefert `subgraphs` — jeder Sub-Graph ist um eine Entity zentriert, die zur Query passt. Innerhalb eines Sub-Graphs findest du:

- **nodes**: Alle Entities mit Name, Typ, Beschreibung, Source-Quote, und Score
- **edges**: Relationen zwischen den Entities
- **chunks** (wenn `include_chunks: true`): Die Original-Textstellen

Der `score` zeigt die semantische Ähnlichkeit zur Query (0-1). `is_entry: true` markiert die Haupt-Entity des Sub-Graphs.
