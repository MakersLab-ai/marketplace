---
description: Content-Ideen aus Destillar generieren und kuratieren
argument-hint: [generate|browse]
---

Der Nutzer möchte mit Destillars **IdeaCards** arbeiten — automatisch generierte Content-Ideen aus dem Wissensgraph. Führe den Nutzer interaktiv durch den Workflow.

**Argument-Handling:** Wenn `$ARGUMENTS` `generate` oder `browse` enthält, überspringe Schritt 1 und nutze direkt den entsprechenden Zweig. Sonst frage.

---

## Schritt 1 — Modus wählen

Frage den Nutzer:

> Möchtest du **neue Ideen generieren** oder **existierende Ideen durchstöbern**?

- `generate` → Schritt 2a
- `browse` → Schritt 2b

---

## Schritt 2a — Ideen generieren

Frage nacheinander:

1. **Thema** (optional): Auf welches Thema sollen sich die Ideen fokussieren? (Leerlassen = freie Entdeckung über den gesamten Graph)
2. **Format** (optional): `article`, `post`, `carousel` — oder leer lassen, damit Destillar selbst entscheidet
3. **Anzahl**: Wie viele Ideen? (1–20, Default 5)

Rufe `generate_content_ideas` auf mit den gewählten Parametern (`topic`, `format`, `count`; `seed_reasons` nicht setzen, es sei denn der Nutzer nennt explizit eine Heuristik).

Präsentiere das Ergebnis kompakt:

```
Generiert: {generated.length} Ideen ({skipped_duplicates} Duplikate übersprungen, {duration_ms}ms)

1. **{title}** — {format} / {storyline}
   Hook: {hook}
   Seed: {seed_reason} | Score: {score}

2. ...
```

Keine vollständigen Entities oder Outlines in dieser Übersicht — nur Titel, Hook, Format, Storyline, Seed-Reason, Score.

Weiter zu **Schritt 3**.

---

## Schritt 2b — Ideen durchstöbern

Frage nacheinander:

1. **Status-Filter**: `pending` (Default), `accepted`, `dismissed`, `drafted`
2. **Format-Filter** (optional): `article`, `post`, `carousel`
3. **Topic-Filter** (optional): Freitext

Rufe `list_content_ideas` mit den Filtern auf (`limit: 20`, `sort: score_desc`).

Präsentiere identisch zu Schritt 2a (nummerierte Titel + Hook + Format/Storyline + Seed + Score). Wenn `total > limit`: Hinweis auf weitere Seiten, biete an, mit `offset` nachzuladen.

Weiter zu **Schritt 3**.

---

## Schritt 3 — Idee auswählen

Frage den Nutzer nach der Nummer der interessanten Idee. Rufe `get_content_idea` mit der entsprechenden `id` auf.

Zeige dann die **volle IdeaCard** an:

```
{title}

Hook: {hook}
Alt-Hooks: {alt_hooks.join(" | ")}

{description}

Format: {format} | Storyline: {storyline} | Sprache: {language}
Seed: {seed_reason} ({seed_detail})

Outline:
- {outline[0]}
- {outline[1]}
...

Verknüpfte Entities:
- [{role}] {name} ({entity_type}) — aus Quelle {source_id}
  "{source_quote}"
...
```

---

## Schritt 4 — Aktion wählen

Frage:

> Was möchtest du tun?
> 1. **Draft schreiben** — direkt einen Content-Entwurf erstellen
> 2. **Accepten** — Idee für später vormerken
> 3. **Verwerfen** — Idee aussortieren
> 4. **Nichts tun** — nur angeschaut

**Option 1 (Draft):**
- Rufe `update_content_idea_status` mit `status: drafted` auf
- Leite in den `/destillar-content`-Workflow über, indem du die Parameter aus der IdeaCard als vorausgefülltes Briefing übernimmst:
  - Thema = `title` bzw. `description`
  - Format = `format`
  - Tonfall = aus `storyline` ableiten (z.B. `how_to` → praktisch-anleitend, `contrarian` → pointiert, `story_hook` → erzählerisch)
  - Länge = Format-typisch (post: 200–400 Wörter; article: 800–1500; carousel: 6–10 Slides)
  - Sprache = `language`
- Folge dann dem Schreib-Workflow aus `/destillar-content` ab **Schritt 3 (Schreiben)** — die Recherche-Phase kann verkürzt werden, weil die verknüpften Entities bereits in der IdeaCard stehen. Gezielte Nachfolge-Queries mit `include_chunks: true` und `top_k: 1` auf diese Entities, um Zitate zu holen.

**Option 2 (Accept):**
- Rufe `update_content_idea_status` mit `status: accepted` auf
- Bestätige: „Idee als akzeptiert vorgemerkt — findbar über `/destillar-ideas browse` mit Status-Filter `accepted`."

**Option 3 (Dismiss):**
- Rufe `update_content_idea_status` mit `status: dismissed` auf
- Bestätige: „Idee verworfen."

**Option 4:**
- Keine Aktion.

---

## Wichtig

- Nie `seed_reasons` auf eigene Faust setzen — nur wenn der Nutzer explizit z.B. „nur Frameworks" oder „nur Cross-Source-Insights" verlangt (dann entsprechend `framework_chain` bzw. `cross_source_insight`).
- Bei großen Listen in Schritt 2b: niemals alle Details auf einmal anzeigen, sondern die kompakte Liste. Details erst nach Auswahl in Schritt 3.
- Fehler beim Tool-Call (z.B. ungültige `idea_id`): sauber zurückmelden, dem Nutzer anbieten, die Liste neu zu laden.
