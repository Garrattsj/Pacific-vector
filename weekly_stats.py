#!/usr/bin/env python3
"""
PACIFIC VECTOR — Weekly Subscriber Stats
Pulls the current Resend audience, summarises growth and composition over the
last 7 days, and emails the summary to the owner. Runs weekly via GitHub Actions.
"""

import os
import datetime
import requests
from collections import Counter

JST = datetime.timezone(datetime.timedelta(hours=9))


def now_jst():
    return datetime.datetime.now(JST)


# ── CONFIGURATION ────────────────────────────────────────────────────────────
RESEND_API_KEY    = os.environ.get("RESEND_API_KEY", "")
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID", "")
DELIVER_TO_EMAIL  = ["stuartgarratt@hotmail.com"]
SEND_FROM_EMAIL   = "brief@pacific-vector.com"

if not RESEND_API_KEY:
    raise SystemExit("ERROR: RESEND_API_KEY environment variable is not set.")
if not RESEND_AUDIENCE_ID:
    raise SystemExit("ERROR: RESEND_AUDIENCE_ID environment variable is not set.")


# ── STEP 1: FETCH ALL CONTACTS ───────────────────────────────────────────────
def fetch_contacts():
    contacts = []
    page_token = None
    while True:
        url = f"https://api.resend.com/audiences/{RESEND_AUDIENCE_ID}/contacts"
        params = {"after": page_token} if page_token else {}
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        contacts.extend(data.get("data", []))
        page_token = data.get("next_page_token")
        if not page_token:
            break
    return contacts


# ── STEP 2: COMPUTE STATS ────────────────────────────────────────────────────
def compute_stats(contacts):
    now = now_jst()
    week_ago = now - datetime.timedelta(days=7)

    total = len(contacts)
    active = sum(1 for c in contacts if not c.get("unsubscribed"))
    unsubscribed = total - active

    new_this_week = 0
    for c in contacts:
        created = c.get("created_at")
        if not created:
            continue
        try:
            created_dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
        except ValueError:
            continue
        if created_dt >= week_ago:
            new_this_week += 1

    industries = Counter()
    sources = Counter()
    for c in contacts:
        props = c.get("properties") or {}
        if props.get("industry"):
            industries[props["industry"]] += 1
        if props.get("source"):
            sources[props["source"]] += 1

    return {
        "total": total,
        "active": active,
        "unsubscribed": unsubscribed,
        "new_this_week": new_this_week,
        "top_industries": industries.most_common(5),
        "top_sources": sources.most_common(5),
    }


# ── STEP 3: BUILD AND SEND EMAIL ─────────────────────────────────────────────
def render_list(items, empty_label):
    if not items:
        return f'<p style="color:#888; font-size:0.8rem;">{empty_label}</p>'
    rows = "".join(
        f'<tr><td style="padding:0.3rem 0; font-size:0.82rem;">{name}</td>'
        f'<td style="padding:0.3rem 0; font-size:0.82rem; text-align:right; color:#1a3a5c; font-weight:500;">{count}</td></tr>'
        for name, count in items
    )
    return f'<table style="width:100%; border-collapse:collapse;">{rows}</table>'


def send_stats_email(stats, date_str):
    html = f"""
    <div style="font-family: 'IBM Plex Mono', monospace; max-width: 600px; margin: 0 auto; padding: 2rem; color: #0d0d0d; background: #f8f8f6;">
      <div style="font-size: 1rem; font-weight: 500; letter-spacing: 0.2em; margin-bottom: 0.5rem; color: #1a3a5c;">
        PACIFIC<span style="color: #2a5a8c;">VECTOR</span>
      </div>
      <p style="font-size: 0.7rem; color: #888; letter-spacing: 0.08em; margin-bottom: 2rem;">
        WEEKLY SUBSCRIBER STATS — {date_str}
      </p>

      <div style="display: flex; gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap;">
        <div>
          <div style="font-size: 1.6rem; font-weight: 500; color: #1a3a5c;">{stats['active']}</div>
          <div style="font-size: 0.68rem; color: #888; letter-spacing: 0.05em;">ACTIVE SUBSCRIBERS</div>
        </div>
        <div>
          <div style="font-size: 1.6rem; font-weight: 500; color: #1a3a5c;">+{stats['new_this_week']}</div>
          <div style="font-size: 0.68rem; color: #888; letter-spacing: 0.05em;">NEW THIS WEEK</div>
        </div>
        <div>
          <div style="font-size: 1.6rem; font-weight: 500; color: #888;">{stats['unsubscribed']}</div>
          <div style="font-size: 0.68rem; color: #888; letter-spacing: 0.05em;">UNSUBSCRIBED</div>
        </div>
      </div>

      <div style="border-left: 2px solid #1a3a5c; padding-left: 1rem; margin-bottom: 1.5rem;">
        <p style="font-size: 0.7rem; color: #888; letter-spacing: 0.08em; margin-bottom: 0.5rem;">TOP INDUSTRIES</p>
        {render_list(stats['top_industries'], 'No industry data yet.')}
      </div>

      <div style="border-left: 2px solid #1a3a5c; padding-left: 1rem; margin-bottom: 2rem;">
        <p style="font-size: 0.7rem; color: #888; letter-spacing: 0.08em; margin-bottom: 0.5rem;">TOP SOURCES</p>
        {render_list(stats['top_sources'], 'No source data yet.')}
      </div>

      <div style="padding-top: 1.5rem; border-top: 1px solid #e5e5e5; font-size: 0.65rem; color: #888; letter-spacing: 0.08em;">
        PACIFIC VECTOR — Japan Geopolitical Intelligence
      </div>
    </div>
    """

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json={
            "from":    SEND_FROM_EMAIL,
            "to":      DELIVER_TO_EMAIL,
            "subject": f"Pacific Vector — Weekly Stats ({date_str})",
            "html":    html,
        },
        timeout=15,
    )
    if resp.status_code in (200, 201):
        print("  ✓ Weekly stats email sent")
    else:
        print(f"  ⚠️  Failed to send stats email: {resp.status_code} — {resp.text}")


def main():
    print("📊 Fetching subscriber audience...")
    contacts = fetch_contacts()
    print(f"  ✓ Fetched {len(contacts)} contacts")

    stats = compute_stats(contacts)
    print(f"  Active: {stats['active']} | New this week: {stats['new_this_week']} | Unsubscribed: {stats['unsubscribed']}")

    date_str = now_jst().strftime("%Y-%m-%d")
    send_stats_email(stats, date_str)


if __name__ == "__main__":
    main()
