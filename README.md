<div align="center">

# 🧪 AI Makers Lab — Claude Code Marketplace

**Offizieller Plugin-Marketplace von [AI Makers Lab](https://makerslab.ai)**

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Marketplace-D97757?logo=anthropic&logoColor=white)](https://code.claude.com/docs/en/plugin-marketplaces)
[![Plugins](https://img.shields.io/badge/Plugins-2-6E56CF)](#-plugins)
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
| [**`groundcontrol-for-claude-code`**](./plugins/groundcontrol-for-claude-code) | `0.1.0` | Coding-Agent für GROUNDCONTROL — picks up assigned tasks, opens PRs, closes the loop. |

> Mehr Plugins folgen. PRs willkommen.

---

## 🔄 Updates

### Für User

```bash
/plugin marketplace update makerslab-ai      # Katalog neu ziehen
/plugin update destillar@makerslab-ai        # Plugin auf neueste Version
```

Auto-Updates laufen bei jedem Start von Claude Code automatisch, solange das Repo public bleibt.

### Für Maintainer

1. Änderungen am Plugin → committen → nach `main` pushen
2. Bei relevanten Änderungen die `version` in `.claude-plugin/marketplace.json` erhöhen
   — Claude Code erkennt Updates **nur** über eine neue Versionsnummer
3. Optional: Git-Tag setzen (z.B. `v0.5.0`), damit User sich per `ref` pinnen können

> 💡 **Release-Channels:** Für getrennte `stable`/`beta`-Kanäle einen zweiten Marketplace-Eintrag mit anderem `ref` einrichten ([Doku](https://code.claude.com/docs/en/plugin-marketplaces#set-up-release-channels)).

---

## 🗂 Repo-Struktur

```
.
├── .claude-plugin/
│   └── marketplace.json       # Plugin-Katalog
└── plugins/
    └── destillar/             # → plugins/destillar/README.md
```

---

## 🤝 Mitwirken

Issues und PRs sind willkommen. Für neue Plugins:

1. Plugin unter `plugins/<name>/` anlegen
2. Eintrag in `.claude-plugin/marketplace.json` ergänzen
3. README mit Beschreibung, Commands und Installation hinzufügen

---

## 📄 Lizenz

MIT © [AI Makers Lab](https://makerslab.ai)
