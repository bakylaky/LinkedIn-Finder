# Full-list enrichment — status & how to resume

Two background resolvers fill `master_enriched.csv` for all 11,209 appraisers. A watcher
(`finalize2.sh`) commits a progress snapshot every ~4 min and a FINAL commit when both finish.

## Channels (why these, given the constraints)
- **Company domains** — `resolve_domains.py` → `domain_probe.tsv`. Uses `curl` (uncapped).
- **LinkedIn** — `resolve_linkedin.py` → `li_firecrawl.tsv`. Queries **Firecrawl `/v1/search`** via
  `curl` (uncapped — the built-in WebSearch tool is hard-capped at 200/session, which is why we
  don't use it here). Strict scoring: first+last name match (with nicknames), appraiser signal,
  location/company corroboration; confidence High / Medium / Low, else blank.

## Resume after a container recycle (new session)
Both resolvers are **resumable** — they skip row_ids/domains already recorded in their output
files (which are committed to this branch). In a fresh session:

```bash
cd /home/user/LinkedIn-Finder
git pull origin claude/tender-mayer-w6l8v0
nohup python3 output/full/resolve_linkedin.py  > output/full/li_resolve.log 2>&1 &   # if LinkedIn incomplete
nohup python3 output/full/resolve_domains.py   > output/full/resolve.log   2>&1 &    # if domains incomplete
nohup bash    output/full/finalize2.sh         > output/full/finalize2.log 2>&1 &    # periodic commit + final merge
```
Check progress: `wc -l output/full/li_firecrawl.tsv output/full/domain_probe.tsv`.
Rebuild the deliverable anytime: `python3 output/full/build_master.py` → `master_enriched.csv`.

## Deliverable
`output/full/master_enriched.csv` — 11,209 rows: identity + Company Domain + LinkedIn URL +
confidence + notes + email. Precedence for LinkedIn: hand-verified (bank/AMC + regional passes)
> Firecrawl > earlier agent chunks.
