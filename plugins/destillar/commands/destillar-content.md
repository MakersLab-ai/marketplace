---
description: Content aus Philipps Wissensgraph (Destillar) erstellen
argument-hint: [idea_id]
---

Der Nutzer möchte einen Inhalt auf Basis von Philipp Maderthaners Wissensgraph (Destillar) erstellen. Führe den Nutzer interaktiv durch den Prozess.

**Einstieg aus einer IdeaCard:** Wenn `$ARGUMENTS` eine `idea_id` enthält (oder der User aus `/destillar-ideas` weitergeleitet wurde), rufe zuerst `get_content_idea` mit der `idea_id` auf. Übernimm die Felder `title`, `description`, `format`, `storyline`, `language`, `outline` und `entities` als vorausgefülltes Briefing und überspringe **Schritt 1**. Gehe direkt zu Schritt 2 (Recherche). Setze nach erfolgreichem Draft (Ende von Schritt 3) den Status der IdeaCard via `update_content_idea_status` auf `drafted`.

**Schritt 1: Briefing** *(nur wenn kein `idea_id` übergeben wurde)*

Frage den Nutzer nacheinander:

1. **Thema**: Worüber soll der Inhalt sein? (z.B. "Delegation", "Skalierung von Teams", "Pricing-Strategien")
2. **Format**: Was für ein Format? (Blog-Artikel, Newsletter, Social Media Post, Deep-Dive PDF, LinkedIn-Post, etc.)
3. **Zielgruppe**: Für wen ist der Inhalt? (Unternehmer, Führungskräfte, Gründer, allgemeines Publikum)
4. **Tonfall**: Eher direkt und motivierend (à la Philipp), sachlich-redaktionell, oder anders?
5. **Länge**: Kurz (300-500 Wörter), mittel (800-1200), oder lang (1500+)?

**Schritt 2: Recherche**

Führe mehrere kleine Queries mit `query_knowledge_base` durch. Verfügbare Parameter sind **nur**: `question` (string), `top_k` (integer, default 3), `include_chunks` (boolean, default false).

Strategie — immer klein anfangen:
1. Übersichts-Query zum Hauptthema (`top_k: 1`, `include_chunks: false`)
2. Fokussierte Queries zu Unter-Aspekten, die in den ersten Ergebnissen auftauchen (`top_k: 1`, `include_chunks: false`)
3. Gezielte Queries mit `include_chunks: true` und `top_k: 1` für die vielversprechendsten Treffer — um Originalzitate zu holen

**Einstieg aus einer IdeaCard:** Die verknüpften Entities sind bereits bekannt. Die Recherche verkürzt sich dann auf gezielte Nachfolge-Queries (`include_chunks: true`, `top_k: 1`) pro Entity, um Original-Zitate zu holen. Breite Übersichts-Queries sind nicht mehr nötig.

**Niemals `top_k` höher als 2 setzen**, da die Ergebnisse sonst zu groß werden und das Token-Limit sprengen. Lieber mehr einzelne Queries stellen.

Präsentiere dem Nutzer eine kurze Zusammenfassung des gefundenen Materials:
- Die wichtigsten Einsichten und Methoden
- Vorschlag für die inhaltliche Struktur

Frage, ob die Richtung passt oder ob weitere Recherche nötig ist.

**Schritt 3: Schreiben**

Erstelle den Inhalt basierend auf dem Destillar-Material:

- Verwende Entities als inhaltliche Bausteine (Einsichten als Thesen, Methoden als How-to, Illustrationen als Beispiele)
- Baue Quellverweise ein (z.B. "Wie Philipp in Podcast Episode 42 erklärt...")
- Halte dich an den gewünschten Tonfall und die Länge
- Strukturiere nach dem Format (Blog: Einleitung → Hauptteil → Takeaway; Newsletter: Hook → Insight → CTA; etc.)

Schreibe den fertigen Inhalt als Datei (Markdown für Blog/Newsletter, oder das passende Format).

**Schritt 4: Review**

Prüfe den erstellten Inhalt:
- Sind alle Aussagen durch Destillar-Ergebnisse belegt?
- Stimmt der Tonfall?
- Passt die Länge?

Präsentiere den Inhalt und frage nach Feedback. Iteriere bei Bedarf.

**IdeaCard-Lifecycle:** Wenn der Draft aus einer IdeaCard entstanden ist, setze nach Abschluss den Status der Card via `update_content_idea_status` auf `drafted`. Das markiert die Idee als "verwendet" und verhindert, dass sie erneut in der `pending`-Liste auftaucht.

**Wichtig:** Erfinde keine Aussagen. Wenn Destillar zu einem Aspekt nichts hergibt, markiere das transparent oder lasse den Aspekt weg.
