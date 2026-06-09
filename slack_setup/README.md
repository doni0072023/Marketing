# Slack setup — Pacific Focus

This folder turns the Pacific Focus blueprint into the actual Slack workspace:
7 channels, each with a pinned **Canvas** intro and an owner-tagged **task checklist**.

## Files

| File | What it is |
|------|------------|
| `channels.json` | Source of truth — every channel's name, purpose, Canvas text, and checklist. |
| `setup_slack.py` | Creates the channels + canvases via the Slack Web API. Stdlib only, no installs. |
| `owners.example.json` | Template for mapping `[Tag]` → Slack user ID so tags become `@mentions`. |

Human-readable copies of each channel's Canvas + checklist live in
[`../channels/`](../channels) — useful for paste-by-hand or review.

## Run it

1. **Create a Slack app** at <https://api.slack.com/apps> → *From scratch*, in the Pacific Focus workspace.
2. Add these **bot token scopes** (OAuth & Permissions):
   - `channels:read`, `channels:manage` — public channels
   - `groups:read`, `groups:write` — only if you make any channel private
   - `canvases:write` — create/edit the channel canvases
3. **Install** the app to the workspace and copy the **Bot User OAuth Token** (`xoxb-…`).
4. *(Optional)* map owners to real people:
   ```bash
   cp owners.example.json owners.json   # then fill in Slack user IDs
   ```
   Get an ID from a member's profile → **More** → **Copy member ID**. Tags without an
   ID stay as literal text (e.g. `[Owen]`).
5. Preview, then run for real:
   ```bash
   python3 setup_slack.py --dry-run     # shows the plan, calls nothing
   export SLACK_BOT_TOKEN=xoxb-...
   python3 setup_slack.py
   ```

The script is **idempotent on channels**: re-running reuses an existing channel by name
instead of erroring. It will add a fresh canvas each run, so run it once per channel set
(or delete a channel's canvas before re-running if you want a clean replace).

## Notes

- **Owners**: each task keeps its `[Name]` tag inline. For a sortable *Task · Owner · Status*
  view, build a **Slack List** per channel and set the Owner column from the tags — the
  checklist text in `channels.json` maps 1:1 to list rows.
- **Canvas content** combines the `📌 Canvas` intro and the checklist so a single channel
  canvas shows purpose + tasks. Checkbox lines (`- [ ]`) render as interactive to-dos.
- The bot must be **invited to private channels** it didn't create before it can canvas them.
