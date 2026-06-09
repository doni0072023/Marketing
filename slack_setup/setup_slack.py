#!/usr/bin/env python3
"""
Pacific Focus — Slack workspace bootstrapper.

Reads slack_setup/channels.json and, for each channel:
  1. Creates the channel (or reuses it if it already exists).
  2. Sets the channel purpose.
  3. Creates/overwrites a channel Canvas containing the "📌 Canvas" intro
     plus the task checklist (rendered as interactive checkboxes).

Owner tags like [Owen] are kept as plain text by default. If
slack_setup/owners.json exists mapping a tag to a Slack user ID, e.g.
    {"Owen": "U012ABCDEF", "Adoniah": "U034GHIJKL"}
the matching tags are rewritten to <@U...> mentions inside the canvases.

Usage:
    export SLACK_BOT_TOKEN=xoxb-...          # bot token with the scopes below
    python3 slack_setup/setup_slack.py            # do it
    python3 slack_setup/setup_slack.py --dry-run  # show what would happen

Required bot token scopes:
    channels:read, channels:manage   (public channels)
    groups:read, groups:write        (only if any channel is private)
    canvases:write                   (create/edit canvases)

This script uses only the Python standard library — no pip install needed.
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

API = "https://slack.com/api/"
HERE = os.path.dirname(os.path.abspath(__file__))


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def call(method, token, dry_run=False, **params):
    """POST to a Slack Web API method, retrying on rate limits."""
    if dry_run:
        print(f"   [dry-run] {method}({', '.join(f'{k}=...' for k in params)})")
        return {"ok": True, "dry_run": True}

    data = urllib.parse.urlencode(
        {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in params.items()}
    ).encode()
    req = urllib.request.Request(
        API + method,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = int(e.headers.get("Retry-After", 2 ** attempt))
                print(f"   rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise
        if not body.get("ok") and body.get("error") == "ratelimited":
            time.sleep(2 ** attempt)
            continue
        return body
    return {"ok": False, "error": "ratelimited_giveup"}


def find_channel(token, name, is_private, dry_run):
    """Return existing channel id by name, or None."""
    if dry_run:
        return None
    types = "private_channel" if is_private else "public_channel"
    cursor = ""
    while True:
        res = call("conversations.list", token, types=types, limit=1000, cursor=cursor,
                   exclude_archived=True)
        if not res.get("ok"):
            print(f"   ! conversations.list failed: {res.get('error')}")
            return None
        for ch in res.get("channels", []):
            if ch.get("name") == name:
                return ch.get("id")
        cursor = res.get("response_metadata", {}).get("next_cursor", "")
        if not cursor:
            return None


def apply_owner_map(text, owners):
    for tag, uid in owners.items():
        if uid:
            text = text.replace(f"[{tag}]", f"<@{uid}>")
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print actions without calling Slack")
    ap.add_argument("--config", default=os.path.join(HERE, "channels.json"))
    args = ap.parse_args()

    token = os.environ.get("SLACK_BOT_TOKEN", "")
    if not token and not args.dry_run:
        sys.exit("ERROR: set SLACK_BOT_TOKEN (or use --dry-run).")

    config = load_json(args.config)
    owners = load_json(os.path.join(HERE, "owners.json"), default={}) or {}
    if owners:
        print(f"Owner map loaded: {', '.join(owners)}")

    for ch in config["channels"]:
        name = ch["name"]
        is_private = ch.get("is_private", False)
        print(f"\n=== #{name} ===")

        # 1. Create or reuse the channel
        existing = find_channel(token, name, is_private, args.dry_run)
        if existing:
            cid = existing
            print(f"   channel exists -> {cid}")
        else:
            res = call("conversations.create", token, name=name, is_private=is_private,
                       dry_run=args.dry_run)
            if not res.get("ok") and not args.dry_run:
                print(f"   ! create failed: {res.get('error')} (skipping)")
                continue
            cid = res.get("channel", {}).get("id", "(dry-run-id)")
            print(f"   created -> {cid}")

        # 2. Set the purpose
        if ch.get("purpose"):
            call("conversations.setPurpose", token, channel=cid, purpose=ch["purpose"],
                 dry_run=args.dry_run)

        # 3. Build canvas markdown (intro + checklist) and create the channel canvas
        markdown = "## 📌 Canvas\n\n" + ch["canvas"] + "\n\n" + ch["tasks"] + "\n"
        markdown = apply_owner_map(markdown, owners)
        res = call("conversations.canvases.create", token, channel_id=cid,
                   document_content={"type": "markdown", "markdown": markdown},
                   dry_run=args.dry_run)
        if res.get("ok"):
            print(f"   canvas set ({len(markdown)} chars)")
        elif not args.dry_run:
            print(f"   ! canvas failed: {res.get('error')}")

    print("\nDone.")


if __name__ == "__main__":
    main()
