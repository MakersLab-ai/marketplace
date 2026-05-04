---
description: Philipps Wissensgraph über Destillar abfragen
argument-hint: [frage]
---

Der Nutzer möchte Philipp Maderthaners Wissensgraph über Destillar abfragen.

Wenn ein Argument übergeben wurde (`$ARGUMENTS`), verwende es direkt als Query. Wenn nicht, frage den Nutzer nach seinem Thema oder seiner Frage.

**Vorgehen:**

1. Rufe `query_knowledge_base` auf mit der Frage des Nutzers. Starte **immer** mit diesen Defaults:
   - `top_k`: 1
   - `include_chunks`: false

   Das sind die einzigen verfügbaren Parameter neben `question`. Verwende keine anderen Parameter.

2. Präsentiere die Ergebnisse übersichtlich auf Deutsch:
   - Fasse die wichtigsten Einsichten zusammen (basierend auf den Entities)
   - Nenne konkrete Methoden oder Frameworks, falls vorhanden
   - Verweise auf die Quellen (Podcast-Episode, Seminar, Dokument)

3. Falls der Nutzer Originalzitate braucht, stelle eine Nachfolge-Query mit `include_chunks: true` und `top_k: 1`.

4. Falls die Ergebnisse zu groß sind und abgeschnitten werden: Query mit `top_k: 1` und `include_chunks: false` wiederholen. Niemals `top_k` erhöhen, um das Problem zu lösen.

5. Wenn die Ergebnisse dünn sind (wenige Entities, niedrige Scores), biete an:
   - Die Query anders zu formulieren
   - Verwandte Themen zu erkunden (neue Query mit anderem Blickwinkel)

**Wichtig:** Alle Aussagen müssen durch Destillar-Ergebnisse belegt sein. Keine Informationen erfinden oder Philipp Aussagen zuschreiben, die nicht in den Ergebnissen stehen.
