# Pacific Focus — Slack workspace blueprint

Foundations-first setup for the Pacific Focus project: get Owen's book finished, published,
and in front of the right readers — and build the platform that carries it.

This repo holds everything needed to stand up the Slack workspace: 7 numbered channels, each
with a pinned **Canvas** intro and an owner-tagged **task checklist**.

## What's here

```
channels/            Human-readable Canvas text + checklist for each channel (00–06)
slack_setup/         Automation: channels.json (source of truth) + setup_slack.py
```

## Channels

| # | Channel | Owner(s) | Purpose |
|---|---------|----------|---------|
| 00 | `start-here` | Team | Vision, roles, and the identities everyone steps into |
| 01 | `manuscript` | Owen | Edit → break down → rewrite to a publisher-ready draft |
| 02 | `publishing` | Owen + Adoniah | Agent route, paid-hybrid offer, and self-pub fallback in parallel |
| 03 | `website-funnel` | Adoniah | Author website + GoHighLevel lead-capture engine |
| 04 | `content-and-linkedin` | Adoniah + Owen | Content engine + Owen's LinkedIn |
| 05 | `launch` | Bree | Launch plan (light until the publishing path is chosen) |
| 06 | `team-and-ops` | Adoniah | Tools, access, onboarding, and keeping Kez warm |

**People & tags:** `[Owen]` author · `[Adoniah]` builder/marketer (website, GoHighLevel,
content) · `[Bree]` launch/PR · `[Kez]` not yet onboard (warm) · `[Team]` shared decision.

## Create the channels in Slack

See [`slack_setup/README.md`](slack_setup/README.md). Short version:

```bash
cd slack_setup
python3 setup_slack.py --dry-run        # preview
export SLACK_BOT_TOKEN=xoxb-...          # bot token, scopes in the setup README
python3 setup_slack.py                   # create channels + canvases
```

Prefer to do it by hand? Each file in [`channels/`](channels) is ready to paste: drop the
**📌 Canvas** block into the channel's Canvas, and the **Tasks** block as a checklist or
Slack List.

> **Order of attack (foundations first):** `#00` set identities → `#03` + `#04` (Adoniah builds
> the website/funnel and content engine) alongside `#01` (Owen's rewrite) → `#02` publishing kept
> warm on both tracks → `#05`/`#06` stay light until there's momentum to show.
