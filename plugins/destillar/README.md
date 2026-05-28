# Destillar Plugin

Zugriff auf Philipp Maderthaners Wissensgraph über **Destillar** — für Wissensabfragen und Content-Erstellung in Claude Code.

## Was das Plugin kann

- **Wissen abfragen**: Philipps gesamtes Wissen aus Podcasts, Seminaren und Dokumenten durchsuchen
- **Content erstellen**: Blog-Artikel, Newsletter, Social Media Posts und mehr — gestützt auf echte Quellen aus dem Wissensgraph
- **Content-Ideen generieren**: Destillar schlägt automatisch content-würdige IdeaCards (Titel, Hook, Outline, Format, Storyline) vor, die kuratiert und direkt in Drafts überführt werden können
- **Quellen erkunden**: Alle eingespeisten Quellen durchsuchen und im Detail betrachten

## Bevor du anfängst

> ⚠️ **Zugang ist allowlist-kontrolliert.** Destillar lässt nicht jede gültige Email-Adresse rein. Deine Email muss auf der **User-Allowlist** des Backends stehen, sonst weist dich der Server beim Login ab — auch mit funktionierendem Magic-Link.

Wenn du noch keinen Zugang hast, melde dich bei **christoph@cambuildr.com** (oder einem Admin-User), damit deine Email freigeschaltet wird. Erst danach funktioniert der Connect-Flow unten.

## Komponenten

### MCP Server: `destillar` (Remote)
Verbindet Claude mit Destillar über einen gehosteten MCP-Endpunkt. Kein lokaler Server nötig.

**Authentifizierung:** OAuth 2.1 mit Magic-Link. Beim ersten Connect öffnet Claude Code den Browser, du loggst dich mit deiner Email ein, fertig — kein API-Key, kein Setup. Jeder User authentifiziert sich mit dem eigenen Account, was sauberen Audit-Trail und User-spezifische Rate-Limits ermöglicht. Voraussetzung: deine Email steht auf der Allowlist (siehe [Bevor du anfängst](#bevor-du-anfängst)).

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

## Wenn etwas nicht funktioniert

| Was du siehst | Bedeutung | Nächster Schritt |
|---|---|---|
| `403 email_not_allowlisted` direkt nach dem Magic-Link-Klick | Deine Email ist (noch) nicht auf der Allowlist. Der Check greift schon beim OAuth-Callback, damit du den Fehler sofort siehst statt erst beim ersten Tool-Aufruf. | Email-Freischaltung bei **christoph@cambuildr.com** (oder Admin) anfragen. Adds greifen nach max. 60 Sekunden. |
| `403 email_not_allowlisted` bei einem Tool-Aufruf (Query, Content, Ideas) | Gleiche Ursache — der Allowlist-Check läuft zusätzlich auf jeder authentifizierten Route (defense in depth). Tritt typischerweise auf, wenn dein Zugang nachträglich entfernt wurde. | Admin kontaktieren und klären, ob dein Zugang noch aktiv sein soll. |
| `403 JWT missing email claim` | Das ausgestellte Token trägt keinen Email-Claim — selten, meist ein Provider-Konfigurationsproblem. | Admin melden (Backend-seitige Supabase-Provider-Konfig prüfen). |
| `503 Allowlist not configured` / `503 Allowlist temporarily unavailable` | Server-seitiges Problem (Service-Role-Key fehlt bzw. Supabase-Outage), liegt nicht an dir. | Kurz warten und erneut versuchen; bei Persistenz Admin melden. |

> Magic-Link kommt an, aber Login schlägt trotzdem fehl? Fast immer ist es die Allowlist. Frag im Zweifel bei **christoph@cambuildr.com** nach, ob deine Email freigeschaltet ist.
