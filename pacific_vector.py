#!/usr/bin/env python3
"""
PACIFIC VECTOR v2.0 — Daily Japan Geopolitical Brief Generator
RSS-powered. No NewsAPI dependency.
"""

import os
import json
import datetime
import requests
import xml.etree.ElementTree as ET
from pathlib import Path

# Pacific Vector publishes on a Japan timezone schedule — always compute
# "today" in JST so the masthead date matches the publish day, regardless
# of the UTC time the GitHub Actions runner executes in.
JST = datetime.timezone(datetime.timedelta(hours=9))


def now_jst():
    return datetime.datetime.now(JST)

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
RESEND_API_KEY    = os.environ.get("RESEND_API_KEY", "")

if not ANTHROPIC_API_KEY:
    raise SystemExit(
        "ERROR: ANTHROPIC_API_KEY environment variable is not set. "
        "Set it before running this script (do not hardcode keys in this file)."
    )
if not RESEND_API_KEY:
    raise SystemExit(
        "ERROR: RESEND_API_KEY environment variable is not set. "
        "Set it before running this script (do not hardcode keys in this file)."
    )
OUTPUT_DIR        = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)

# ── CHANGE COLOURS HERE (email) ───────────────────────────────────────────────
DELIVER_TO_EMAIL  = ["stuartgarratt@hotmail.com"]
SEND_FROM_EMAIL   = "brief@pacific-vector.com"
ALERT_EMAIL       = "stuartgarratt@hotmail.com"  # Where to send failure alerts

# Resend audience to broadcast the daily brief to. Set RESEND_AUDIENCE_ID in
# GitHub Secrets — if unset, broadcast step is skipped (personal email still sends).
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID", "")

# ── RSS FEED SOURCES ───────────────────────────────────────────────────────────
# To add a source: add a new dict to this list
# To remove a source: delete or comment out the line
RSS_FEEDS = [
    {"name": "Japan Times",     "url": "https://www.japantimes.co.jp/feed/"},
    {"name": "Kyodo News",      "url": "https://english.kyodonews.net/rss/all.xml"},
    {"name": "The Diplomat",    "url": "https://thediplomat.com/feed/"},
    {"name": "East Asia Forum", "url": "https://www.eastasiaforum.org/feed/"},
    {"name": "Japan News (Yomiuri)", "url": "https://japannews.yomiuri.co.jp/feed/"},
    {"name": "CSIS",            "url": "https://www.csis.org/rss.xml"},
    {"name": "Stimson Center",  "url": "https://www.stimson.org/feed/"},
]
# NOTES ON THIS UPDATE (Phase 2 RSS fix):
#  - NHK World's English RSS feed has been discontinued/dead for some time
#    (404). Replaced with Kyodo News Plus, a major English-language Japanese
#    wire service with a reliable feed.
#  - Reuters discontinued its public RSS feeds entirely (the old
#    feeds.reuters.com URL is dead with no direct replacement). Replaced with
#    The Japan News by The Yomiuri Shimbun, another major English Japan source.
#  - East Asia Forum and Stimson Center were returning 403 errors, which is
#    typically caused by sites blocking generic/bot User-Agent strings rather
#    than the feed itself being down. The User-Agent below has been changed to
#    a standard browser string to address this.
#  - All entries use the existing try/except per-feed handling, so if any one
#    of these still fails it will simply be skipped and logged, not crash the
#    run. Run the script once and check the "Fetching news from RSS feeds..."
#    output to confirm each source returns articles.

# Keywords to filter relevant articles (must contain at least one)
RELEVANCE_KEYWORDS = [
    "japan", "japanese", "tokyo", "kishida", "koizumi", "ishiba",
    "china", "beijing", "senkaku", "quad", "indo-pacific",
    "ldp", "jsdf", "us-japan", "japan-us", "asia-pacific",
    "taiwan", "korea", "north korea", "asean", "g7",
]


# ── STEP 1: FETCH NEWS VIA RSS ────────────────────────────────────────────────
def fetch_articles():
    """Pull articles from RSS feeds and filter for Japan relevance."""
    print("📡 Fetching news from RSS feeds...")
    articles = []
    seen_titles = set()
    cutoff = datetime.datetime.now() - datetime.timedelta(days=2)

    for feed in RSS_FEEDS:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            }
            resp = requests.get(feed["url"], headers=headers, timeout=15)
            resp.raise_for_status()

            # Parse RSS XML
            root = ET.fromstring(resp.content)

            # Handle both RSS and Atom formats
            items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

            feed_count = 0
            for item in items:
                # Extract fields (handles both RSS and Atom)
                title   = _get_text(item, ["title"])
                url     = _get_text(item, ["link", "guid"])
                desc    = _get_text(item, ["description", "summary", "{http://www.w3.org/2005/Atom}summary"])
                pubdate = _get_text(item, ["pubDate", "published", "updated"])

                if not title or title in seen_titles:
                    continue

                # Check relevance
                combined = (title + " " + (desc or "")).lower()
                if not any(kw in combined for kw in RELEVANCE_KEYWORDS):
                    continue

                seen_titles.add(title)
                articles.append({
                    "title":       title,
                    "source":      feed["name"],
                    "url":         url or "",
                    "description": desc or "",
                    "content":     desc or "",
                    "publishedAt": pubdate or "",
                })
                feed_count += 1

            print(f"  ✓ {feed['name']}: {feed_count} relevant articles")

        except Exception as e:
            print(f"  ⚠️  {feed['name']} failed: {e}")

    print(f"\n  📰 Total: {len(articles)} articles collected")
    return articles


def _get_text(element, tags):
    """Helper to extract text from XML element trying multiple tag names."""
    for tag in tags:
        el = element.find(tag)
        if el is not None:
            # For <link> tags that use href attribute (Atom)
            if el.text:
                return el.text.strip()
            href = el.get("href")
            if href:
                return href
    return None


# ── STEP 2: GENERATE BRIEF VIA CLAUDE ────────────────────────────────────────
def generate_brief(articles):
    """Send articles to Claude and generate the Pacific Vector brief."""
    print("🧠 Sending to Claude for analysis...")

    today = now_jst().strftime("%A, %d %B %Y")

    # Format articles for the prompt
    articles_text = ""
    for i, a in enumerate(articles[:20], 1):
        articles_text += f"""
[ARTICLE {i}]
Title: {a['title']}
Source: {a['source']}
URL: {a['url']}
Published: {a['publishedAt']}
Summary: {a['description']}
---"""

    prompt = f"""You are the editor of PACIFIC VECTOR, a precision daily intelligence brief on Japan geopolitics for a senior diplomat.

Today is {today}.

Below are {len(articles[:40])} articles collected from approved sources. Your job is to produce today's brief.

STRICT RULES:
- Only use information present in the articles provided. Never invent facts.
- Every story must cite its source and URL.
- Be blunt. Cut to the strategic implication. No filler phrases like "experts say" or "analysts believe."
- Tone: sharp, direct, professional. Like a trusted colleague who knows Japan deeply.

OUTPUT FORMAT — return valid JSON exactly matching this structure:

{{
  "date": "{today}",
  "opening_line": "One sharp sentence capturing the strategic mood of today's news.",
  "sections": [
    {{
      "title": "JAPAN–CHINA",
      "stories": [
        {{
          "headline": "Sharp headline in caps",
          "what_happened": "2 sentences max. Just the facts.",
          "so_what": "The strategic implication. Blunt. 2-3 sentences.",
          "source": "Source Name",
          "url": "https://..."
        }}
      ]
    }},
    {{
      "title": "JAPAN–US & SECURITY",
      "stories": [...]
    }},
    {{
      "title": "INDO-PACIFIC / QUAD",
      "stories": [...]
    }},
    {{
      "title": "DOMESTIC POLITICS",
      "stories": [...]
    }}
  ],
  "profile": {{
    "name": "Full name of the most significant Japanese political figure in today's news",
    "title": "Their current role",
    "who_they_are": "2-3 sentences on who they are and why they matter today.",
    "background": "Career and political lineage in 1-2 sentences.",
    "known_positions": "Their stance on China, US alliance, defence. Blunt.",
    "watch": "One thing to watch with this person right now."
  }}
}}

Include 2-4 stories per section where articles support it. If a section has no relevant articles, include 1 story noting limited coverage.

ARTICLES:
{articles_text}

Return only the JSON. No preamble, no markdown fences."""

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 4000,
        "messages": [{"role": "user", "content": prompt}],
    }

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=body,
        timeout=120,
    )
    result = resp.json()

    if "error" in result:
        raise Exception(f"Claude API error: {result['error']}")

    raw = result["content"][0]["text"].strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    brief = json.loads(raw)
    print("  ✓ Brief generated")
    return brief


# ── STEP 3: RENDER HTML ───────────────────────────────────────────────────────
def render_html(brief):
    """Render the brief as a minimal monospace HTML page."""
    print("🎨 Rendering HTML...")

    sections_html = ""
    for section in brief.get("sections", []):
        stories_html = ""
        for story in section.get("stories", []):
            stories_html += f"""
            <article class="story">
                <h3 class="story-headline">{story['headline']}</h3>
                <p class="story-what">{story['what_happened']}</p>
                <div class="so-what">
                    <span class="so-what-label">// so what</span>
                    <p>{story['so_what']}</p>
                </div>
                <a class="source-link" href="{story['url']}" target="_blank">↗ {story['source']}</a>
            </article>"""

        sections_html += f"""
        <section class="pillar">
            <div class="pillar-header">
                <span class="pillar-label">— {section['title']}</span>
            </div>
            {stories_html}
        </section>"""

    profile = brief.get("profile", {})
    profile_html = f"""
        <section class="pillar profile-section">
            <div class="pillar-header">
                <span class="pillar-label">— TODAY'S FIGURE</span>
            </div>
            <div class="profile-card">
                <div class="profile-name-block">
                    <span class="profile-name">{profile.get('name', '')}</span>
                    <span class="profile-title">{profile.get('title', '')}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">who</span>
                    <p>{profile.get('who_they_are', '')}</p>
                </div>
                <div class="profile-row">
                    <span class="profile-label">background</span>
                    <p>{profile.get('background', '')}</p>
                </div>
                <div class="profile-row">
                    <span class="profile-label">positions</span>
                    <p>{profile.get('known_positions', '')}</p>
                </div>
                <div class="profile-row watch-row">
                    <span class="profile-label">watch</span>
                    <p>{profile.get('watch', '')}</p>
                </div>
            </div>
        </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pacific Vector — {brief['date']}</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --white:   #ffffff;
    --navy:    #1a3a5c;
    --navy-lt: #e8f0f8;
    --ink:     #0d0d0d;
    --mid:     #888888;
    --rule:    #e5e5e5;
    --mono:    'IBM Plex Mono', monospace;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: var(--white); color: var(--ink); font-family: var(--mono); font-weight: 300; font-size: 13px; line-height: 1.75; }}
  a {{ color: inherit; text-decoration: none; }}
  .wrap {{ max-width: 720px; margin: 0 auto; padding: 0 2rem; }}
  header {{ padding: 3rem 0 2rem; border-bottom: 1px solid var(--ink); margin-bottom: 2.5rem; }}
  .logo {{ font-size: 1.1rem; font-weight: 500; letter-spacing: 0.25em; text-transform: uppercase; }}
  .logo-accent {{ color: var(--navy); }}
  .meta {{ display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.72rem; color: var(--mid); letter-spacing: 0.08em; }}
  .lede {{ margin-bottom: 3rem; padding-left: 1rem; border-left: 2px solid var(--navy); font-size: 0.85rem; line-height: 1.8; }}
  .pillar {{ margin-bottom: 3rem; }}
  .pillar-header {{ margin-bottom: 1.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--rule); }}
  .pillar-label {{ font-size: 0.68rem; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; color: var(--navy); }}
  .story {{ margin-bottom: 2rem; padding-bottom: 2rem; border-bottom: 1px solid var(--rule); }}
  .story:last-child {{ border-bottom: none; padding-bottom: 0; }}
  .story-headline {{ font-size: 0.88rem; font-weight: 500; line-height: 1.5; margin-bottom: 0.6rem; }}
  .story-what {{ font-size: 0.8rem; color: #444; margin-bottom: 0.8rem; line-height: 1.75; }}
  .so-what {{ background: var(--navy-lt); border-left: 2px solid var(--navy); padding: 0.8rem 1rem; margin-bottom: 0.8rem; }}
  .so-what-label {{ font-size: 0.62rem; font-weight: 500; color: var(--navy); letter-spacing: 0.12em; display: block; margin-bottom: 0.3rem; }}
  .so-what p {{ font-size: 0.8rem; line-height: 1.75; }}
  .source-link {{ font-size: 0.68rem; color: var(--mid); letter-spacing: 0.05em; }}
  .source-link:hover {{ color: var(--navy); }}
  .profile-card {{ border: 1px solid var(--rule); margin-top: 0.5rem; }}
  .profile-name-block {{ display: flex; justify-content: space-between; align-items: baseline; padding: 0.8rem 1rem; background: var(--navy); color: var(--white); flex-wrap: wrap; gap: 0.3rem; }}
  .profile-name {{ font-size: 0.88rem; font-weight: 500; }}
  .profile-title {{ font-size: 0.68rem; color: #a0b8d0; }}
  .profile-row {{ display: grid; grid-template-columns: 90px 1fr; gap: 1rem; padding: 0.8rem 1rem; border-bottom: 1px solid var(--rule); align-items: start; }}
  .profile-row:last-child {{ border-bottom: none; }}
  .profile-label {{ font-size: 0.62rem; font-weight: 500; color: var(--mid); letter-spacing: 0.12em; text-transform: uppercase; padding-top: 0.15rem; }}
  .profile-row p {{ font-size: 0.8rem; line-height: 1.75; }}
  .watch-row {{ background: #f5f8fc; }}
  .watch-row .profile-label {{ color: var(--navy); }}
  footer {{ margin-top: 3rem; padding: 1.5rem 0 3rem; border-top: 1px solid var(--rule); font-size: 0.65rem; color: var(--mid); letter-spacing: 0.08em; display: flex; flex-direction: column; gap: 0.4rem; }}
  .footer-top {{ display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; }}
  footer a {{ color: var(--navy); }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">PACIFIC<span class="logo-accent">VECTOR</span></div>
    <div class="meta">
      <span>{brief['date']}</span>
      <span>Japan Geopolitical Intelligence</span>
    </div>
  </header>
  <div class="lede">{brief.get('opening_line', '')}</div>
  <main>
    {sections_html}
    {profile_html}
  </main>
  <footer>
    <div class="footer-top">
      <span>PACIFIC VECTOR — Japan Geopolitical Intelligence</span>
      <span>All analysis grounded in sourced reporting</span>
    </div>
    <div>
      <a href="https://pacific-vector.com">pacific-vector.com</a>
      &nbsp;·&nbsp;
      <a href="{{{{{{RESEND_UNSUBSCRIBE_URL}}}}}}">Unsubscribe</a>
    </div>
  </footer>
</div>
</body>
</html>"""

    return html


# ── STEP 4: SAVE OUTPUT ───────────────────────────────────────────────────────
def save_output(brief, html):
    today_str = now_jst().strftime("%Y-%m-%d")
    html_path = OUTPUT_DIR / f"pacific_vector_{today_str}.html"
    json_path = OUTPUT_DIR / f"pacific_vector_{today_str}.json"
    html_path.write_text(html, encoding="utf-8")
    json_path.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ HTML saved → {html_path}")
    print(f"  ✓ JSON saved → {json_path}")
    return html_path


# ── STEP 5: SEND EMAIL VIA RESEND ────────────────────────────────────────────
def send_email(brief, html):
    """Send the brief as an HTML email via Resend (personal copy)."""
    print("📧 Sending email via Resend...")
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json={
            "from":    SEND_FROM_EMAIL,
            "to":      DELIVER_TO_EMAIL,
            "subject": f"Pacific Vector — {brief['date']}",
            "html":    html,
        },
        timeout=15,
    )
    if resp.status_code in (200, 201):
        print(f"  ✓ Brief emailed to {DELIVER_TO_EMAIL}")
    else:
        print(f"  ⚠️  Email failed: {resp.status_code} — {resp.text}")


# ── STEP 5b: BROADCAST TO SUBSCRIBER AUDIENCE ────────────────────────────────
def send_broadcast(brief, html):
    """Send the brief to the full Resend subscriber audience."""
    if not RESEND_AUDIENCE_ID:
        print("  ⏭️  RESEND_AUDIENCE_ID not set — skipping audience broadcast.")
        return

    print("📣 Broadcasting brief to subscriber audience...")
    resp = requests.post(
        "https://api.resend.com/broadcasts",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
        json={
            "audience_id": RESEND_AUDIENCE_ID,
            "from":        SEND_FROM_EMAIL,
            "subject":     f"Pacific Vector — {brief['date']}",
            "html":        html,
            "name":        f"Daily brief — {brief['date']}",
            "send":        True,
        },
        timeout=15,
    )
    if resp.status_code in (200, 201):
        print("  ✓ Broadcast sent to subscriber audience")
    else:
        print(f"  ⚠️  Broadcast failed: {resp.status_code} — {resp.text}")


# ── STEP 6: SEND FAILURE ALERT ────────────────────────────────────────────────
def send_alert(error_message):
    """Email an alert if the brief fails to generate."""
    print("🚨 Sending failure alert...")
    today = now_jst().strftime("%A, %d %B %Y")
    try:
        requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from":    SEND_FROM_EMAIL,
                "to":      [ALERT_EMAIL],
                "subject": f"⚠️ Pacific Vector failed — {today}",
                "html":    f"""
                    <div style="font-family: monospace; padding: 2rem; color: #0d0d0d;">
                        <h2 style="color: #c41e3a;">Pacific Vector — Brief Generation Failed</h2>
                        <p><strong>Date:</strong> {today}</p>
                        <p><strong>Error:</strong></p>
                        <pre style="background: #f5f5f5; padding: 1rem; font-size: 12px;">{error_message}</pre>
                        <p>Check GitHub Actions logs for details.</p>
                    </div>
                """,
            },
            timeout=15,
        )
        print("  ✓ Alert sent")
    except Exception as e:
        print(f"  ⚠️  Alert failed: {e}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════╗")
    print("║        PACIFIC VECTOR  v2.0          ║")
    print("║   Japan Geopolitical Intelligence    ║")
    print("╚══════════════════════════════════════╝\n")

    try:
        articles = fetch_articles()

        if len(articles) == 0:
            raise Exception("No articles collected from any RSS feed. All feeds may be down or blocked.")

        if len(articles) < 3:
            print(f"  ⚠️  Warning: only {len(articles)} articles collected. Brief may be thin.")

        brief     = generate_brief(articles)
        html      = render_html(brief)
        html_path = save_output(brief, html)
        send_email(brief, html)
        send_broadcast(brief, html)

        print(f"\n✅ Pacific Vector brief ready.")
        print(f"   Open: {html_path.resolve()}\n")

    except Exception as e:
        print(f"\n❌ Pacific Vector failed: {e}")
        send_alert(str(e))
        raise  # Re-raise so GitHub Actions marks the run as failed
