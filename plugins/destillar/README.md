# Destillar Plugin

Zugriff auf Philipp Maderthaners Wissensgraph über **Destillar** — für Wissensabfragen und Content-Erstellung in Claude Code.

## Was das Plugin kann

- **Wissen abfragen**: Philipps gesamtes Wissen aus Podcasts, Seminaren und Dokumenten durchsuchen
- **Content erstellen**: Blog-Artikel, Newsletter, Social Media Posts und mehr — gestützt auf echte Quellen aus dem Wissensgraph
- **Content-Ideen generieren**: Destillar schlägt automatisch content-würdige IdeaCards (Titel, Hook, Outline, Format, Storyline) vor, die kuratiert und direkt in Drafts überführt werden können
- **Quellen erkunden**: Alle eingespeisten Quellen durchsuchen und im Detail betrachten

## Komponenten

### MCP Server: `destillar` (Remote)
Verbindet Claude mit Destillar über einen gehosteten MCP-Endpunkt. Kein lokaler Server nötig.

**Authentifizierung:** OAuth 2.1 mit Magic-Link. Beim ersten Connect öffnet Claude Code den Browser, du loggst dich mit deiner Email ein, fertig — kein API-Key, kein Setup. Jeder User authentifiziert sich mit dem eigenen Account, was sauberen Audit-Trail und User-spezifische Rate-Limits ermöglicht.

### Skill: `destillar`
Lehrt Claude, wie man effektive Queries formuliert und aus den Ergebnissen hochwertige Inhalte erstellt.

### Commands
- `/destillar-query [frage]` — Schnelle Wissensabfrage mit strukturierter Antwort
- `/destillar-ideas [generate|browse]` — Content-Ideen (IdeaCards) generieren oder kuratieren
- `/destillar-content [idea_id]` — Interaktiver Content-Erstellungs-Workflow, optional direkt aus einer IdeaCard

## Installation

```
/plugin marketplace add makerslab-ai/marketplace
/plugin install destillar@makerslab-ai
```
