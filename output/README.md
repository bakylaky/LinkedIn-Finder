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

## Bank / AMC segment (higher-yield) — [`bank_amc_enriched.csv`](bank_amc_enriched.csv)
Full target pool: [`bank_amc_targets.csv`](bank_amc_targets.csv) = **204** appraisers at
national banks & AMCs (Wells Fargo, BofA/LandSafe, US Bank, Regions, JPMorgan Chase,
BMO, ServiceLink, Amrock, Dart, Opteon, Solidifi, Class Valuation, CoreLogic, Accurate
Group, First American, MountainSeed, Nationwide Appraisal Network, First Citizens).

**Progress: 48 of 204 researched.** Results so far:
- **15 LinkedIn URLs found** (11 High / Medium-High confidence), e.g. Sara Bartolini
  (Amrock, 10/10), Gregory Hartley (Regions), Janet Ingersoll (Solidifi), Jackson Reedy
  (Opteon), Rick Rokusek (BofA), Judy Bruton (BofA/LandSafe), Steve Faughn (Solidifi),
  Ali Boloorian (WF), Gina Stokes (US Bank).
- **2 employer-confirmed** (Nikole Avers = Dart Chief Appraiser; Antonio Collins = WF
  appraiser) where the person is confirmed but no public /in/ URL surfaced.
- Company domains filled for every row from the known employer domain.

**Observed pattern (guides where to spend effort):**
- **Hits** cluster at AMCs (Amrock, Solidifi, Opteon, Dart, Accurate, ServiceLink) and on
  **distinctive names** or **manager/chief-appraiser roles**.
- **Misses** cluster on **common names** among Wells Fargo / Chase field staff in large CA
  metros — many have no public profile, and common names can't be matched safely.

## Method notes / limitations
- LinkedIn blocks automated profile fetching, so matching relies on public search snippets
  (name + title + location) — this is deliberately conservative to avoid false positives.
- "None" in the LinkedIn column means *no high-confidence public match was found*, not that
  the person has no profile.
