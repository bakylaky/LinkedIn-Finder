# LinkedIn Finder — First 10 records

Source: `active_with_company.csv` (11,209 active residential appraisers). This is the
enrichment of **records 1–10** (all alphabetically-first, Alabama-licensed appraisers).

Deliverable: [`enriched_first10.csv`](enriched_first10.csv)

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

## Method notes / limitations
- LinkedIn blocks automated profile fetching, so matching relies on public search snippets
  (name + title + location) — this is deliberately conservative to avoid false positives.
- "None" in the LinkedIn column means *no high-confidence public match was found*, not that
  the person has no profile.
