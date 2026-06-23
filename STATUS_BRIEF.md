# Pacific Vector — Status Brief (for concept workshopping)

*Written 2026-06-20. Purpose: bring an outside conversation up to speed so it can help think through where this goes next.*

## What it is today

Pacific Vector is a daily Japan geopolitical intelligence briefing, delivered by email and published on a website (pacific-vector.com). Each morning (07:00 JST), an automated pipeline pulls from RSS feeds (NHK, Reuters, East Asia Forum, Stimson, and others), uses an AI model to synthesise the day's developments into a structured brief — covering Japan-China relations, Japan-US/security, Indo-Pacific/QUAD, domestic politics, and a daily profile of a relevant figure — and sends it to a subscriber list via Resend, while also publishing it to the site. The system runs unattended via GitHub Actions.

It is currently free, pre-revenue, and has a small but real subscriber base collected through organic and direct outreach.

## Where it sits strategically

Two framing documents (`BUSINESS_CONCEPT.md` and `INTELLIGENCE_WORKSHOP.md`) capture the current thinking, in tension with each other on purpose:

**The ambition** (`BUSINESS_CONCEPT.md`): Pacific Vector is not meant to stay a newsletter. The long-term vision is a decision-grade geopolitical intelligence platform for organisations with Asia-Pacific exposure (law firms, advisory firms, corporates, investors) — a "Monitor / Ask / Brief" product where users get daily monitoring, can ask sourced questions against a trusted corpus, and can generate citable briefing packs/memos they can put in front of clients. The moat is imagined as the curated source corpus plus expert annotation, not the AI model itself.

**The discipline** (`INTELLIGENCE_WORKSHOP.md`, written more recently after the operator's own doubts about how clear the market opportunity actually is): rather than commit to that exact product shape now, the build should focus on underlying machinery — source ingestion, translation/summarisation, classification, archive, source discipline, consistent analytical format, a feedback loop on what's useful vs. noise, and output flexibility (the same system should be able to produce daily briefs, weekly summaries, trackers, memos, or other products). The daily brief is the visible proof the machinery works; the eventual commercial product should emerge from repeated use rather than being assumed upfront.

In short: ambition is "Bloomberg Terminal for Asia-Pacific risk." Current discipline is "build the workshop, not the storefront, and let use reveal the product." These aren't fully reconciled, and that's an open question worth workshopping.

## What's actually built (by phase)

- **Phase 1 (Stability)** — complete. RSS-based pipeline replaced an earlier NewsAPI dependency; crash handling, failure alerts, and automation are solid.
- **Phase 2 (Professional Website)** — complete. Branded site with favicon, OG metadata, About/Contact pages, mobile-responsive, SSL clean.
- **Phase 3 (Backend Dashboard & Growth Foundations)** — complete except social share buttons (deliberately deprioritised). This phase added: broadcast-to-full-audience delivery (not just the operator's inbox), unsubscribe links, a 404 page, Vercel Analytics, an upgraded subscribe form that captures organisation/role/industry/signup-source for segmentation, Resend dashboard open/click tracking, UTM attribution capture, a subscriber CSV export endpoint, and an automated weekly stats email (active subscribers, new signups, unsubscribes, top industries/sources).
- **Phase 4 (Content Quality / workshop machinery)** — not started. This is explicitly reframed as building the actual workshop components: expanding and making RSS sources configurable without code changes, refining the AI prompt and analytical format, adding keyword-based classification, persisting every item and brief into a searchable archive, and tracking source citations for every claim. Two workshop components — translation/summarisation (not yet relevant, no non-English sources ingested yet) and a feedback loop (no mechanism yet to learn which items are useful vs. noise) — aren't represented in the roadmap yet.
- **Phases 5-6** (growth infrastructure, "business feel" — pricing page, privacy policy, Stripe, etc.) — not started, lower priority for now.
- **Phases 7-10** (early users, an Ask/RAG feature, a brief-generation feature, commercial launch) — explicitly marked exploratory/not committed. These were sketched when the product shape felt clearer; they're being held loosely rather than treated as a fixed sequence, pending what Phase 4's machinery reveals.

## Open questions worth workshopping

1. Is "build the machinery and let the product emerge" actually the right sequencing, or does it risk drifting indefinitely without a forcing function to test commercial demand?
2. What's the minimum version of "Ask" or "Brief" (from the original Monitor/Ask/Brief concept) that could be tested cheaply, without building a full RAG pipeline, just to get real signal on whether professional users would pay for it?
3. Given the operator's own stated doubts about market clarity, what would be the cheapest, fastest way to validate (or invalidate) demand from the target wedge — law firms, advisory firms, corporate risk teams — before investing further in Phase 4's archive/classification work?
4. Is Japan-only scope the right constraint long-term, or does the corpus/moat argument only really work once it expands across Northeast Asia or the broader Indo-Pacific?
5. The business concept names "source-grounded, auditable intelligence" as the core differentiator from generic AI tools — what would it take to prove that differentiation concretely (e.g. a side-by-side comparison, a citation audit) rather than assert it?
