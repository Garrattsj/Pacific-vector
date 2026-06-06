#!/usr/bin/env python3
"""
PACIFIC VECTOR — Daily Japan Geopolitical Brief Generator
Run this script each morning to generate your brief.
"""

import os
import json
import datetime
import requests
from pathlib import Path

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_KEY_HERE")
NEWS_API_KEY      = os.environ.get("NEWS_API_KEY",      "YOUR_NEWSAPI_KEY_HERE")
OUTPUT_DIR        = Path("./output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Approved sources — Pacific Vector only reads these
APPROVED_SOURCES = [
    "Japan Times",
    "NHK World",
    "The Diplomat",
    "Reuters",
    "Associated Press",
    "East Asia Forum",
    "Nikkei Asia",
    "CGTN",
    "Xinhua",
]

# Search queries targeting your four pillars
NEWS_QUERIES = [
    "Japan China relations geopolitics",
    "Japan United States alliance security",
    "Indo-Pacific QUAD strategy Japan",
    "Japan domestic politics LDP",
    "Japan Senkaku defense military",
    "Japan foreign policy diplomacy",
]

# ── STEP 1: FETCH NEWS ─────────────────────────────────────────────────────────
def fetch_articles():
    """Pull articles from NewsAPI across all pillars."""
    print("📡 Fetching news from approved sources...")
    articles = []
    seen_titles = set()

    for query in NEWS_QUERIES:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "from": (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
            "apiKey": NEWS_API_KEY,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            for a in data.get("articles", []):
                title = a.get("title", "")
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    articles.append({
                        "title":       title,
                        "source":      a.get("source", {}).get("name", "Unknown"),
                        "url":         a.get("url", ""),
                        "description": a.get("description", ""),
                        "content":     a.get("content", ""),
                        "publishedAt": a.get("publishedAt", ""),
                    })
        except Exception as e:
            print(f"  ⚠️  Query '{query}' failed: {e}")

    print(f"  ✓ {len(articles)} articles collected")
    return articles


# ── STEP 2: GENERATE BRIEF VIA CLAUDE ─────────────────────────────────────────
def generate_brief(articles):
    """Send articles to Claude and generate the Pacific Vector brief."""
    print("🧠 Sending to Claude for analysis...")

    today = datetime.datetime.now().strftime("%A, %d %B %Y")

    # Format articles for the prompt
    articles_text = ""
    for i, a in enumerate(articles[:40], 1):  # cap at 40 articles
        articles_text += f"""
[ARTICLE {i}]
Title: {a['title']}
Source: {a['source']}
URL: {a['url']}
Published: {a['publishedAt']}
Summary: {a['description']}
Content: {a['content'][:500] if a['content'] else 'N/A'}
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
    "background": "Career and political lineage in 1-2 sentences. Faction, who they owe.",
    "known_positions": "Their stance on China, US alliance, defence. Blunt.",
    "watch": "One thing to watch with this person right now."
  }}
}}

Include 2-4 stories per section where the articles support it. If a section has no relevant articles today, include 1 story with a note that coverage was limited.

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
        timeout=60,
    )
    result = resp.json()
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


# ── STEP 3: RENDER HTML ────────────────────────────────────────────────────────
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

  body {{
    background: var(--white);
    color: var(--ink);
    font-family: var(--mono);
    font-weight: 300;
    font-size: 13px;
    line-height: 1.75;
  }}

  a {{ color: inherit; text-decoration: none; }}

  .wrap {{
    max-width: 720px;
    margin: 0 auto;
    padding: 0 2rem;
  }}

  /* ── HEADER ── */
  header {{
    padding: 3rem 0 2rem;
    border-bottom: 1px solid var(--ink);
    margin-bottom: 2.5rem;
  }}

  .logo {{
    font-size: 1.1rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
  }}

  .logo-accent {{ color: var(--navy); }}

  .meta {{
    display: flex;
    justify-content: space-between;
    margin-top: 0.5rem;
    font-size: 0.72rem;
    color: var(--mid);
    letter-spacing: 0.08em;
  }}

  /* ── LEDE ── */
  .lede {{
    margin-bottom: 3rem;
    padding-left: 1rem;
    border-left: 2px solid var(--navy);
    font-size: 0.85rem;
    line-height: 1.8;
    color: var(--ink);
  }}

  /* ── PILLARS ── */
  .pillar {{
    margin-bottom: 3rem;
  }}

  .pillar-header {{
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--rule);
  }}

  .pillar-label {{
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--navy);
  }}

  /* ── STORIES ── */
  .story {{
    margin-bottom: 2rem;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--rule);
  }}

  .story:last-child {{
    border-bottom: none;
    padding-bottom: 0;
  }}

  .story-headline {{
    font-size: 0.88rem;
    font-weight: 500;
    line-height: 1.5;
    margin-bottom: 0.6rem;
    letter-spacing: 0.01em;
  }}

  .story-what {{
    font-size: 0.8rem;
    color: #444;
    margin-bottom: 0.8rem;
    line-height: 1.75;
  }}

  .so-what {{
    background: var(--navy-lt);
    border-left: 2px solid var(--navy);
    padding: 0.8rem 1rem;
    margin-bottom: 0.8rem;
  }}

  .so-what-label {{
    font-size: 0.62rem;
    font-weight: 500;
    color: var(--navy);
    letter-spacing: 0.12em;
    display: block;
    margin-bottom: 0.3rem;
  }}

  .so-what p {{
    font-size: 0.8rem;
    line-height: 1.75;
    color: var(--ink);
  }}

  .source-link {{
    font-size: 0.68rem;
    color: var(--mid);
    letter-spacing: 0.05em;
    transition: color 0.15s;
  }}

  .source-link:hover {{ color: var(--navy); }}

  /* ── PROFILE ── */
  .profile-card {{
    border: 1px solid var(--rule);
  }}

  .profile-name-block {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid var(--rule);
    background: var(--navy);
    color: var(--white);
  }}

  .profile-name {{
    font-size: 0.88rem;
    font-weight: 500;
    letter-spacing: 0.05em;
  }}

  .profile-title {{
    font-size: 0.68rem;
    color: #a0b8d0;
    letter-spacing: 0.05em;
  }}

  .profile-row {{
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 1rem;
    padding: 0.8rem 1rem;
    border-bottom: 1px solid var(--rule);
    align-items: start;
  }}

  .profile-row:last-child {{ border-bottom: none; }}

  .profile-label {{
    font-size: 0.62rem;
    font-weight: 500;
    color: var(--mid);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding-top: 0.15rem;
  }}

  .profile-row p {{
    font-size: 0.8rem;
    line-height: 1.75;
  }}

  .watch-row {{ background: #f5f8fc; }}
  .watch-row .profile-label {{ color: var(--navy); }}

  /* ── FOOTER ── */
  footer {{
    margin-top: 3rem;
    padding: 1.5rem 0 3rem;
    border-top: 1px solid var(--rule);
    font-size: 0.65rem;
    color: var(--mid);
    letter-spacing: 0.08em;
  }}

  @media (max-width: 600px) {{
    .profile-name-block {{ flex-direction: column; gap: 0.2rem; }}
    .profile-row {{ grid-template-columns: 1fr; gap: 0.2rem; }}
    .profile-label {{ padding-top: 0; }}
  }}
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
    PACIFIC VECTOR — All analysis grounded in sourced reporting. Follow links to verify. Generated {brief['date']}.
  </footer>

</div>
</body>
</html>"""

    return html


# ── STEP 4: SAVE OUTPUT ────────────────────────────────────────────────────────
def save_output(brief, html):
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Save HTML
    html_path = OUTPUT_DIR / f"pacific_vector_{today_str}.html"
    html_path.write_text(html, encoding="utf-8")

    # Save JSON (useful for email formatting later)
    json_path = OUTPUT_DIR / f"pacific_vector_{today_str}.json"
    json_path.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"  ✓ HTML saved → {html_path}")
    print(f"  ✓ JSON saved → {json_path}")
    return html_path

# ── STEP 5: SEND EMAIL VIA RESEND ─────────────────────────────────────────────
RESEND_API_KEY   = os.environ.get("RESEND_API_KEY", "YOUR_RESEND_KEY_HERE")
DELIVER_TO_EMAIL = ["stuartgarratt@hotmail.com"]
SEND_FROM_EMAIL  = "brief@pacific-vector.com"

def send_email(brief, html):
    """Send the brief as an HTML email via Resend."""
    print("📧 Sending email via Resend...")
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type":  "application/json",
        },
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


# ── MAIN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n╔══════════════════════════════════════╗")
    print("║        PACIFIC VECTOR  v1.0          ║")
    print("║   Japan Geopolitical Intelligence    ║")
    print("╚══════════════════════════════════════╝\n")

    articles  = fetch_articles()
    brief     = generate_brief(articles)
    html      = render_html(brief)
    html_path = save_output(brief, html)
    send_email(brief, html)

    print(f"\n✅ Pacific Vector brief ready.")
    print(f"   Open: {html_path.resolve()}\n")
