<div align="center">

# 🧪 AI Makers Lab — Claude Code Marketplace

**Offizieller Plugin-Marketplace von [AI Makers Lab](https://makerslab.ai)**

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Marketplace-D97757?logo=anthropic&logoColor=white)](https://code.claude.com/docs/en/plugin-marketplaces)
[![Plugins](https://img.shields.io/badge/Plugins-3-6E56CF)](#-plugins)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#-lizenz)

Kuratierte Claude Code Plugins — gebaut für echten Workflow, nicht für Demos.

</div>

---

## 🚀 Quickstart

In Claude Code einmalig den Marketplace hinzufügen:

```bash
/plugin marketplace add makerslab-ai/marketplace
```

Plugin installieren:

```bash
/plugin install destillar@makerslab-ai
```

Das war's. Auto-Updates laufen ab jetzt bei jedem Start von Claude Code.

---

## 📦 Plugins

| Plugin | Version | Beschreibung |
|--------|:-------:|--------------|
| [**`destillar`**](./plugins/destillar) | `0.5.0` | Zugriff auf Philipp Maderthaners Wissensgraph über Destillar — für Wissensabfragen und Content-Erstellung |
| [**`groundcontrol-for-claude-code`**](./plugins/groundcontrol-for-claude-code) | `0.1.9` | Claude-Code-Session als autonomer Coding-Agent auf GROUNDCONTROL-Tasks — pickt Tasks, implementiert, öffnet PRs |
| [**`cambuildr`**](./plugins/cambuildr) | `0.4.0` | Cambuildr-Tenant aus Claude Code steuern — Landing Pages, Kampagnen-Mails, Automated Emails, Workflows, Zielgruppen, Supporter, Media |

> Mehr Plugins folgen. PRs willkommen.

### `destillar`

Wissensabfragen und Content-Erstellung auf Basis von Philipp Maderthaners Wissensgraph.

- **Commands:** `/destillar-query`, `/destillar-ideas`, `/destillar-content`
- **MCP:** Remote HTTP (`api.destillar.ai/mcp`), gebündelt — Auth per OAuth 2.1 Magic-Link beim ersten Connect
- **Setup:** keins. Installieren, Command aufrufen, im Browser einloggen.

→ [Details](./plugins/destillar/README.md)

### `groundcontrol-for-claude-code`

Verwandelt die Session in einen Coding-Agent gegen einen [GROUNDCONTROL](https://groundcontrol.makerslab.ai)-Workspace: nimmt zugewiesene Tasks, implementiert sie, pusht Branches, öffnet PRs und kommentiert den Task.

- **Commands:** `/gc-init` (einmaliges Setup), `/gc-loop` (15-Minuten-Loop), `/gc-check` (ein Durchlauf)
- **MCP:** lokaler Node-Server, im Plugin gebündelt
- **Setup:** `/gc-init` — fragt den API-Key (`gc_live_…`) ab und schreibt `.env`

→ [Details](./plugins/groundcontrol-for-claude-code/README.md)

### `cambuildr`

Landing Pages, Kampagnen-Mails, Automated Emails, Workflows, Zielgruppen, Tags, Media Library und Supporter im [Cambuildr](https://cambuildr.com/)-Tenant lesen und schreiben — inklusive KI-Befüllung der Inhalte.

- **Commands:** `/cambuildr:connect`, `/cambuildr:init`, `/cambuildr:create-landing-page`, `/cambuildr:create-mail`, `/cambuildr:create-workflow`
- **MCP:** Remote HTTP, **nicht gebündelt** — jeder Tenant hat eine eigene URL
- **Setup:** Bevorzugt über den fertigen `/plugin marketplace add …`-Befehl im eigenen Tenant unter `/admin/settings/mcp` — dort ist die MCP-URL bereits eingebaut (braucht Claude Code ≥ 2.1.224). Fallback: `/cambuildr:connect` legt den Connector für deinen Tenant an. Tenant braucht das Feature-Flag `ai_mcp_server`.

→ [Details](./plugins/cambuildr/README.md)

---

## 🔄 Updates

### Für User

```bash
/plugin marketplace update makerslab-ai      # Katalog neu ziehen
/plugin update destillar@makerslab-ai        # Plugin auf neueste Version
```

Auto-Updates laufen bei jedem Start von Claude Code automatisch, solange das Repo public bleibt.

### Für Maintainer

1. Änderungen am Plugin → committen → PR öffnen → nach `main` mergen
2. Bei relevanten Änderungen die `version` erhöhen — in **beiden** Dateien:
   `plugins/<name>/.claude-plugin/plugin.json` und `.claude-plugin/marketplace.json`
   — Claude Code erkennt Updates **nur** über eine neue Versionsnummer

Das gilt für `destillar` und `groundcontrol-for-claude-code`. **`cambuildr` wird nicht hier gepflegt** — siehe unten.

### Versions-Parity

| Workflow | Trigger | Was er tut |
|---|---|---|
| `.github/workflows/plugin-version-check.yml` | Pull Request | Schlägt fehl, wenn die `version` eines Plugins in `.claude-plugin/marketplace.json` nicht der in `plugins/<name>/.claude-plugin/plugin.json` entspricht. |

Ein Mismatch ist zur Laufzeit unsichtbar: Claude Code liest den Katalogeintrag und das installierte Manifest getrennt, und ein Release erreicht die User schlicht nicht. Der Check macht daraus einen roten PR statt eines stillen Nicht-Updates — `destillar` hatte gar keine `version`, genau dieser Fall.

### `cambuildr` wird generiert

Seine Quelle ist `resources/mcp-plugin/` im Applikations-Repo, damit es im selben Pull Request wie der MCP-Server geändert wird, den es beschreibt, und nicht von ihm abweichen kann. Ein Job dort pusht diese Kopie hierher; Änderungen direkt in `plugins/cambuildr/` werden beim nächsten Release überschrieben.

Tenants bekommen ihre eigene, vorkonfigurierte Kopie direkt aus der Applikation — dieser Katalog ist der öffentliche Discovery-Kanal, keine Distributions-Abhängigkeit.

> 💡 **Release-Channels:** Für getrennte `stable`/`beta`-Kanäle einen zweiten Marketplace-Eintrag mit anderem `ref` einrichten ([Doku](https://code.claude.com/docs/en/plugin-marketplaces#set-up-release-channels)).

---

## 🗂 Repo-Struktur

```
.
├── .claude-plugin/
│   └── marketplace.json                    # Plugin-Katalog
├── .github/
│   ├── scripts/check_plugin_versions.py    # Prüfskript des Workflows
│   └── workflows/
│       └── plugin-version-check.yml        # PR-Gate: Katalog- vs. Plugin-Version
└── plugins/
    ├── destillar/                          # → plugins/destillar/README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .mcp.json                       # gebündelter Remote-MCP
    │   ├── commands/
    │   └── skills/
    ├── groundcontrol-for-claude-code/      # → plugins/groundcontrol-for-claude-code/README.md
    │   ├── .claude-plugin/plugin.json
    │   ├── .mcp.json                       # lokaler MCP-Server
    │   ├── commands/
    │   ├── server/dist/                    # gebauter Artefakt (Source: groundcontrol-Repo)
    │   └── skills/
    └── cambuildr/                          # → plugins/cambuildr/README.md
        ├── .claude-plugin/plugin.json
        ├── commands/                       # kein .mcp.json — Connector per /cambuildr:connect
        └── skills/
```

---

## 🤝 Mitwirken

Issues und PRs sind willkommen. Für neue Plugins:

1. Plugin unter `plugins/<name>/` anlegen — mit `.claude-plugin/plugin.json` (`name`, `description`, `version`, `author`)
2. Eintrag in `.claude-plugin/marketplace.json` ergänzen — mit **derselben** Version wie in der `plugin.json`, sonst schlägt der Parity-Check im PR fehl
3. `commands/` und optional `skills/` ergänzen, MCP-Server per `.mcp.json` bündeln — wenn die URL pro Tenant/User variiert, stattdessen einen `connect`-Command bereitstellen
4. README unter `plugins/<name>/README.md` mit Beschreibung, Commands, Installation und Setup
5. Plugin in der Tabelle oben eintragen und den Plugin-Badge-Count aktualisieren

---

## 📄 Lizenz

MIT © [AI Makers Lab](https://makerslab.ai)
