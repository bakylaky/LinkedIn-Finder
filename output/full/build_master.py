#!/usr/bin/env python3
"""Join people + resolved company domains + LinkedIn chunk results into master_enriched.csv."""
import csv, os, glob

BASE=os.path.dirname(__file__)
people=list(csv.DictReader(open(os.path.join(BASE,"people.csv"))))

# --- best domain per company from domain_probe.tsv ---
rank={"HIT_strong":3,"HIT_weak":2,"HIT_slug":1}
best={}  # company -> (score, domain)
probe=os.path.join(BASE,"domain_probe.tsv")
if os.path.exists(probe):
    for line in open(probe,encoding="utf-8"):
        p=line.rstrip("\n").split("\t")
        if len(p)<3: continue
        company,domain,verdict=p[0],p[1],p[2]
        s=rank.get(verdict,0)
        if s==0: continue
        if company not in best or s>best[company][0]:
            best[company]=(s,domain)
company_domain={c:d for c,(s,d) in best.items()}

# --- linkedin from chunk outputs ---
li={}  # row_id -> dict
for fp in sorted(glob.glob(os.path.join(BASE,"li_chunks","out_*.csv"))):
    try:
        for r in csv.DictReader(open(fp,encoding="utf-8")):
            rid=(r.get("row_id") or "").strip()
            if rid:
                li[rid]={"url":(r.get("linkedin_url") or "").strip(),
                         "conf":(r.get("confidence") or "").strip(),
                         "notes":(r.get("notes") or "").strip(),
                         "email":(r.get("email") or "").strip()}
    except Exception as e:
        print("skip",fp,e)

cols=["row_id","First","Middle","Last","Suffix","Lic State","License #","Title","Company","City","State","Zip","Phone",
      "LinkedIn URL","LinkedIn Confidence","LinkedIn Notes","Company Domain","Email"]
out=[]
for r in people:
    rid=r["row_id"]
    l=li.get(rid,{})
    out.append([rid,r["First"],r["Middle"],r["Last"],r["Suffix"],r["LicState"],r["License#"],r["Title"],
                r["Company"],r["City"],r["State"],r["Zip"],r["Phone"],
                l.get("url",""),l.get("conf",""),l.get("notes",""),
                company_domain.get(r["Company"].strip(),""),l.get("email","")])
with open(os.path.join(BASE,"master_enriched.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(cols); w.writerows(out)

n=len(out)
dom=sum(1 for x in out if x[16])
url=sum(1 for x in out if x[13])
liproc=len(li)
print(f"master_enriched.csv: {n} rows | company-domain filled: {dom} | linkedin URL: {url} | people LinkedIn-processed: {liproc}")
