# Pacific Vector — Roadmap

Single source of truth for build progress across all phases. Check items off as completed.

## North Star

Pacific Vector is an AI-powered geopolitical intelligence platform for organisations exposed to Asia-Pacific risk — not, ultimately, a newsletter. The daily brief is the wedge: it builds audience, trust, and brand. The curated source corpus is the moat: it compounds in value and is hard to replicate. The Monitor / Ask / Brief platform is the product: decision-grade, sourced, auditable intelligence — briefings, memos, and risk packs that professionals can put in front of clients and stand behind.

**How we get there:** Pacific Vector is, for now, an intelligence workshop, not a fixed product. We build the underlying machinery — source ingestion, translation/summarisation, classification, archive, source discipline, analytical format, feedback loop, and output flexibility — and let the daily brief be the proof that each piece works. The eventual commercial product (newsletter, monitoring service, briefing engine, dataset, or some combination) should emerge from this machinery rather than being fixed in advance.

Full concept: see `BUSINESS_CONCEPT.md`. Build philosophy: see `INTELLIGENCE_WORKSHOP.md`.

## Phase 1 — Stability ✔ COMPLETE
- [x] Replace NewsAPI with RSS feeds
- [x] Fix 0 articles crash (graceful exit + alert email)
- [x] Add failure alert emails
- [x] Fix GitHub Actions automation
- [x] Fix website showing old brief

## Phase 2 — Professional Website (current)
- [x] Fix broken RSS feeds (NHK, Reuters, East Asia Forum, Stimson)
- [x] Rotate exposed API keys (Anthropic + Resend) and update GitHub Secrets / Vercel env vars
- [x] Replace embedded GitHub personal access token in git remote URL with a credential helper / SSH, and rotate the token
- [x] Add favicon
- [x] Add social metadata (OG tags) — previews when shared on LinkedIn/X
- [x] Fix masthead date bug — daily brief generator now uses JST instead of UTC for date stamps
- [x] Build About page — who's behind Pacific Vector, why trust it
- [x] Build Contact page — professional contact form
- [x] Mobile layout review — ensure brief reads well on phone
- [x] Confirm SSL certificate clean — no security warnings on any browser
- [x] Update footer links — About, Archive, Contact, Subscribe
- [x] Transition workflow to Claude Cowork

## Phase 3 — Backend Dashboard & Growth Foundations
### Core delivery (fix first)
- [x] Wire up daily broadcast — send the brief to the full Resend audience, not just the personal inbox
- [x] Add unsubscribe link to every email (compliance + hygiene)
- [x] Add 404 page

### Analytics & insight
- [x] Enable Vercel Analytics
- [x] Professionalise subscribe form — collect organisation, role, industry, and signup source for marketing segmentation
- [x] Connect Resend dashboard (opens/clicks visibility)
- [x] UTM tracking
- [x] Subscriber export (CSV)
- [x] Build weekly stats email

### Growth foundations
- [x] SEO basics — meta descriptions, sitemap.xml, robots.txt per page
- [ ] Social share buttons on each story/brief

## Phase 4 — Content Quality (intelligence workshop machinery)
Per `INTELLIGENCE_WORKSHOP.md`, this phase is where the core machinery gets built — not just "make the brief better." Each item below maps to a workshop component.

### Configurable source registry (Supabase) — *source ingestion, classification, archive*
Replaces the old hard-coded RSS list with a real database, superseding the "source filtering text file" idea below.
- [x] Create Supabase project + `sources`, `topics`, `source_topics`, `articles` schema
- [x] Seed topic taxonomy (12 topics: Japan-China, Japan-US, domestic politics, defence, economic security, export controls, supply chains, semiconductors, Indo-Pacific/QUAD, Taiwan, China, South Korea)
- [x] Migrate the 7 existing RSS sources into the registry, classified by type/region/priority/reliability/topics
- [x] Build `/admin/sources` — password-gated UI to add, edit, activate/pause sources and assign topics without touching code
- [x] End-to-end test: add a new source (BBC News — Asia) through the admin UI and confirm it persists correctly
- [x] Integrate the daily pipeline to read active sources from Supabase instead of the hard-coded list (fallback retained during migration)
- [ ] Write each ingested article into `articles` with source metadata snapshotted at ingestion time
- [x] Build basic source-health view (last fetch, items in last 7 days, errors, dead/degraded feeds)
- [ ] Remove the hard-coded source list once the registry-driven pipeline is stable

### Other content quality items
- [ ] Fix and expand RSS sources further (NHK, Reuters, East Asia Forum, Stimson) — *source ingestion*
- [ ] Prompt refinement — *analytical format*
- [ ] Add keyword weighting — *classification*
- [ ] Add 'what to watch' section — *analytical format*
- [ ] Improve figure profiles — *analytical format*
- [ ] Track source links/citations for every claim — *source discipline*

### Noted for later (not actioned)
- Language as intelligence metadata — see `INTELLIGENCE_WORKSHOP.md`. Parked until a non-English source is actually added.

## Phase 5 — Growth Infrastructure
- [ ] SEO basics (page titles, meta descriptions, sitemap)
- [ ] Google Search Console
- [ ] Social sharing buttons
- [ ] LinkedIn brand page
- [ ] X account (@pacificvector)
- [ ] Auto-post to LinkedIn and X
- [ ] Referral mechanism
- [ ] Welcome email sequence

## Phase 6 — Business Feel
- [ ] Custom email template
- [ ] Privacy policy page
- [ ] Terms of use page
- [ ] Media kit (PDF)
- [ ] Pricing page
- [ ] Professional domain email (hello@pacific-vector.com)
- [ ] Stripe integration

## Phases 7-10 — Exploratory / revisit later

The phases below sketch one possible path (early users → Ask/RAG → Brief generation → commercial launch), written when the product shape felt more defined. Per `INTELLIGENCE_WORKSHOP.md`, we're no longer committing to this exact sequence — the right next product should emerge from the workshop machinery built in Phase 4, not be assumed in advance. Keeping these as a reference for ideas, not a fixed plan.

## Phase 7 — Early Users
- [ ] Identify 10 network contacts for free access
- [ ] Personal outreach to early users
- [ ] Collect structured feedback
- [ ] LinkedIn announcement post
- [ ] Submit to newsletter directories
- [ ] Approach 3 law firm design partners
- [ ] Milestone: 50 subscribers
- [ ] Milestone: 100 subscribers

## Phase 8 — Ask Pacific Vector (RAG v1)
- [ ] Set up vector database (Pinecone free tier)
- [ ] Build document ingestion pipeline
- [ ] Seed corpus with 50 foundation documents
- [ ] Build question-answering interface
- [ ] Every answer cites sources
- [ ] Launch Ask feature on website

## Phase 9 — Brief Generation Feature
- [ ] Design briefing pack format
- [ ] Build user input form
- [ ] Connect to corpus and daily news
- [ ] Generate cited briefing pack as PDF
- [ ] Test with law firm contacts
- [ ] Launch as premium feature

## Phase 10 — Commercial Launch
- [ ] Define pricing tiers
- [ ] Launch paid individual tier
- [ ] Approach 5 law firm design partners
- [ ] First paying customer
- [ ] Case study from first customer
- [ ] Seed round preparation
