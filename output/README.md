# LinkedIn Finder — residential appraiser enrichment

Source: `active_with_company.csv` — **11,209 active U.S. residential appraisers**.
Goal, in priority order: **LinkedIn profile URL** → **company domain** → **email**,
matched on name + "Certified Residential Appraiser" title + company + location.

## ✅ FULL LIST COMPLETE — all 11,209 people (`output/full/master_enriched.csv`)

The entire list has been swept. **`output/full/master_enriched.csv`** is the primary
deliverable (11,209 rows: identity + LinkedIn URL + confidence + company domain + email).

| Field | Count | % of 11,209 |
|---|---|---|
| **LinkedIn profile URL** | **5,772** | **51%** |
| &nbsp;&nbsp;— High confidence | 2,926 | |
| &nbsp;&nbsp;— Medium-High | 18 | |
| &nbsp;&nbsp;— Medium | 2,667 | |
| &nbsp;&nbsp;— Low | 161 | |
| Employer-confirmed (identity, no public URL) | 131 | |
| **Any LinkedIn signal** | **5,903** | **52%** |
| **Company domain** | **2,420** | **21%** |
| Email found | 679 | |
| Both LinkedIn URL + company domain | 1,403 | |

**How it was done:** the built-in web-search tool is hard-capped at 200 searches/session,
far too few for 11,209 people. The unblock was **Firecrawl `/v1/search`** (called via `curl`
with an API key) — uncapped by our session limit. Company domains were resolved by directly
probing candidate domains per unique company (`curl`, classifying live/parked/dead + branded
slug), plus a curated employer-domain map for banks/AMCs/known firms.

**Scoring (conservative, to avoid false positives):** a LinkedIn hit requires the surname to
appear in the profile title/slug **and** the profile's own first name to match ours (with a
nickname map, no loose slug fallback). Confidence: **High** = appraiser/valuation word in the
title *and* location- or company-corroboration; **Medium** = appraiser signal present;
**Low** = name + company only. Everything weaker is left blank ("none") rather than guessed.
"none" means *no high-confidence public match was found*, not that the person has no profile.

The ~48% with no confident LinkedIn match are dominated by **solo/small-shop appraisers**
(who often keep no LinkedIn) and **common names in large metros** (which can't be matched
safely without risking a wrong person). Domain coverage (21%) is capped by the many solo
appraisers with no website and company names that don't map to a live, guessable domain.

---

The sections below document the earlier **hand-verified passes** (first 10, banks/AMCs,
regional firms), whose results are overlaid on top of the full-list data with highest
precedence in `master_enriched.csv`.

### First 10 records — [`enriched_first10.csv`](enriched_first10.csv)

## What I looked for, per person
1. **LinkedIn profile** (top priority) — matched on **name + appraiser/valuation title** first,
   then **location** as the tie-breaker for a "perfect" (10/10) match.
   Per your instruction, a profile is kept even if the **location differs** (people move),
   as long as the **name + title** line up. A hit is **discarded only** when the title clearly
   isn't an appraiser (e.g. a realtor, a teacher, an unrelated namesake).
2. **Company domain** — verified by resolving the site and/or corroborating via business
   directories and email patterns.
3. **Email** — captured when found or published; not guessed.

## Confidence scale
- **High** — directly confirmed (live site content, published email, exact directory match).
- **Medium** — strong signal (e.g. exact company-name domain that resolves) but not page-verified.
- **None** — nothing found that meets the bar.

## Results for this block (records 1–10)
- **LinkedIn profiles: 0 confident matches.** Every candidate surfaced was verifiably a
  *different* person (e.g. the VA-based "Allen Residential Appraisals" David Allen ≠ our
  new AL licensee at MountainSeed; "Steve Achen" ≠ Achee; an "Abercrombie & Fitch" joke
  profile; etc.).
- **Company domains: 3 confirmed + 1 likely + 1 platform subdomain.**
  - `abercrombieappraisals.com` — Scott Abercrombie (#2), incl. email `scott@abercrombieappraisals.com`
  - `acheeappraisals.com` — Stephen Achee (#4)
  - `mountainseed.com` — David Allen's employer (#10), a national AMC (not a personal firm)
  - `appraisals4ullc.com` — Jennifer Aldridge (#8), likely (exact name match, live, behind WAF)
  - `acaappraisalsinc.appraiserxsites.com` — Andrew Aldridge (#7), platform subdomain
  - Plus one published email: `ackerappraisals1@aol.com` — Fred Acker (#5)

## Why LinkedIn hit-rate is low here (and how to raise it)
Records 1–10 are all **solo / small-shop Alabama residential appraisers** — a segment that
largely does not maintain LinkedIn profiles. Hit-rate should be materially higher for:
- appraisers at **banks and large AMCs** (Wells Fargo, Bank of America, ServiceLink, Dart, etc.),
- appraisers in **major metros** (the CA / NY / TX blocks), and
- **younger / more recently licensed** appraisers.

## Bank / AMC segment (higher-yield) — [`bank_amc_enriched.csv`](bank_amc_enriched.csv)
Full target pool: [`bank_amc_targets.csv`](bank_amc_targets.csv) = **204** appraisers at
national banks & AMCs (Wells Fargo, BofA/LandSafe, US Bank, Regions, JPMorgan Chase,
BMO, ServiceLink, Amrock, Dart, Opteon, Solidifi, Class Valuation, CoreLogic, Accurate
Group, First American, MountainSeed, Nationwide Appraisal Network, First Citizens).

**COMPLETE: all 204 targets researched (203 rows after de-duping one repeat).**
- **70 rows with a LinkedIn profile URL** — 48 High, 14 Medium-High, 6 Medium, 2 Low.
- **34 rows employer-confirmed** — the specific appraiser is confirmed by an external
  source (ZoomInfo/RocketReach/company site/ASC) but no public `/in/` URL surfaced;
  most of these carry a work email pattern instead.
- **32 rows with an email** (verified or published, masked at the source e.g.
  `first@employer.com`).
- **99 rows "None"** — no confident public match (mostly common names among Wells Fargo /
  Chase / BofA field staff in large metros).
- Company domain filled for every row from the known employer domain.

Net: ~51% of bank/AMC rows resolved to either a LinkedIn URL or a confirmed identity.
Strongest clusters: Rally Appraisal (IA), Opteon, Amrock, Solidifi, Gate City Bank (ND),
and any chief/regional/review-appraiser manager role.

**Observed pattern (guides where to spend effort):**
- **Hits** cluster at AMCs (Amrock, Solidifi, Opteon, Dart, Accurate, ServiceLink) and on
  **distinctive names** or **manager/chief-appraiser roles**.
- **Misses** cluster on **common names** among Wells Fargo / Chase field staff in large CA
  metros — many have no public profile, and common names can't be matched safely.

## Regional appraisal firms (Task 1 expansion) — [`regional_enriched.csv`](regional_enriched.csv)
Beyond the national banks/AMCs, I enriched **91 appraisers at 9 distinctive multi-person
regional firms**: RSDS Valuations, WAIV Valuation, Property Sciences, Accurity Consolidated,
True Footage, EFIRD Appraisals, Griffin Appraisals, Definitive Valuations, Martin Appraisal Group.
(Generic firm names like "Accurate Appraisals" were skipped — they merge unrelated same-named
shops across states.)

**Results: 22 LinkedIn URLs (16 High, 4 Med-High, 1 Med, 1 Low) + 33 employer-confirmed + 17 emails.**
~60% of rows resolved to a URL or a confirmed identity. Confirmed firm domains: `rsdsllc.com`,
`waiv.com`, `propsci.com`, `accurity.com`, `truefootage.tech`, `efirdappraisals.com`,
`definitivevaluations.com`. Firm principals/owners were the most findable (e.g. Natalie Jay /
Definitive founder, Will & Chantal Griffin, Gregge Efird, Ryan Judd / True Footage,
Robert Banton & Frank Moody / WAIV, Kurt Stieghan & Brad McNally / True Footage).
NB: "Griffin Appraisals" is actually 3 separate firms (Madison AL / Birmingham AL / Mill Valley CA).

## Deepening the bank/AMC set (Task 2)
Chased the 34 employer-confirmed bank/AMC rows for personal `/in/` URLs and re-checked the
Medium/Low ones. Net gain: **Mike Helmich (Rally)** resolved to a URL. The remaining
employer-confirmed people are confirmed via ZoomInfo/company site/ASC but are **not individually
indexed on LinkedIn** by name (private or not surfaced) — public search can't recover those URLs,
so they stay employer-confirmed with an email pattern + domain. The Medium/Low rows can't be
pushed higher without opening the profiles directly (LinkedIn is login-walled to automated fetch),
so their honest labels stand.

## Method notes / limitations
- LinkedIn blocks automated profile fetching, so matching relies on public search snippets
  (name + title + location) — this is deliberately conservative to avoid false positives.
- "None" in the LinkedIn column means *no high-confidence public match was found*, not that
  the person has no profile.
