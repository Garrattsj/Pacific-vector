# Pacific Vector — Roadmap

Single source of truth for build progress across all phases. Check items off as completed.

## North Star

Pacific Vector is an AI-powered geopolitical intelligence platform for organisations exposed to Asia-Pacific risk — not, ultimately, a newsletter. The daily brief is the wedge: it builds audience, trust, and brand. The curated source corpus is the moat: it compounds in value and is hard to replicate. The Monitor / Ask / Brief platform is the product: decision-grade, sourced, auditable intelligence — briefings, memos, and risk packs that professionals can put in front of clients and stand behind.

Full concept: see `BUSINESS_CONCEPT.md`.

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
- [ ] Connect Resend dashboard (opens/clicks visibility)
- [ ] UTM tracking
- [ ] Subscriber export (CSV)
- [ ] Build weekly stats email

### Growth foundations
- [x] SEO basics — meta descriptions, sitemap.xml, robots.txt per page
- [ ] Social share buttons on each story/brief

## Phase 4 — Content Quality
- [ ] Fix and expand RSS sources further (NHK, Reuters, East Asia Forum, Stimson)
- [ ] Source filtering text file (turn sources on/off without editing code)
- [ ] Prompt refinement
- [ ] Add keyword weighting
- [ ] Add 'what to watch' section
- [ ] Improve figure profiles

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
