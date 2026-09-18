#!/usr/bin/env python3
"""Join people + resolved company domains + all LinkedIn results (agent chunks + earlier
hand-verified bank/AMC & regional passes) into master_enriched.csv. Marks not-searched rows."""
import csv, os, glob, re

BASE=os.path.dirname(__file__)
ROOT=os.path.dirname(BASE)  # output/
people=list(csv.DictReader(open(os.path.join(BASE,"people.csv"))))

# --- best verified domain per company from domain_probe.tsv ---
rank={"HIT_strong":3,"HIT_weak":2,"HIT_slug":1}
best={}
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

# curated employer domains (banks/AMCs/known firms) as fallback by keyword
CURATED=[("wells fargo","wellsfargo.com"),("bank of america","bankofamerica.com"),("landsafe","bankofamerica.com"),
 ("us bank","usbank.com"),("u.s. bank","usbank.com"),("regions","regions.com"),("truist","truist.com"),
 ("jpmorgan","jpmorganchase.com"),("jp morgan","jpmorganchase.com"),("j.p.morgan","jpmorganchase.com"),
 ("pnc","pnc.com"),("bmo","bmo.com"),("huntington","huntington.com"),("first citizens","firstcitizens.com"),
 ("first horizon","firsthorizon.com"),("synovus","synovus.com"),("gate city","gatecity.bank"),
 ("servicelink","servicelink.com"),("amrock","amrock.com"),("corelogic","corelogic.com"),
 ("class valuation","classvaluation.com"),("dart appraisal","dartappraisal.com"),("mountainseed","mountainseed.com"),
 ("rally appraisal","rallyappraisal.com"),("first american","firstam.com"),("solidifi","solidifi.com"),
 ("opteon","opteonsolutions.com"),("pcv murcor","pcvmurcor.com"),("accurate group","accurategroup.com"),
 ("consolidated analytics","consolidatedanalytics.com"),("nationwide appraisal","nationwideappraisalnetwork.com"),
 ("waiv","waiv.com"),("property sciences","propsci.com"),("accurity","accurity.com"),("rsds","rsdsllc.com"),
 ("true footage","truefootage.tech"),("efird","efirdappraisals.com"),("definitive valuation","definitivevaluations.com")]
def curated_domain(company):
    c=company.lower()
    for kw,dom in CURATED:
        if kw in c: return dom
    return ""

# --- LinkedIn from agent chunk outputs (row_id keyed) ---
li={}
def is_unsearched(notes):
    return bool(re.search(r"not searched|budget", notes or "", re.I))
for fp in sorted(glob.glob(os.path.join(BASE,"li_chunks","out_*.csv"))):
    try:
        for r in csv.DictReader(open(fp,encoding="utf-8")):
            rid=(r.get("row_id") or "").strip()
            if not rid: continue
            url=(r.get("linkedin_url") or "").strip()
            conf=(r.get("confidence") or "").strip()
            notes=(r.get("notes") or "").strip()
            email=(r.get("email") or "").strip()
            if not url and is_unsearched(notes):
                conf="not-searched"
            li[rid]={"url":url,"conf":conf,"notes":notes,"email":email,"src":"agent"}
    except Exception as e:
        print("skip",fp,e)

# --- overlay earlier hand-verified passes, matched by (first,last,city,state) ---
def key(first,last,city,state):
    return (re.sub(r'[^a-z]','',(first or '').lower()),
            re.sub(r'[^a-z]','',(last or '').split(',')[0].lower()),
            re.sub(r'[^a-z]','',(city or '').lower()),
            (state or '').strip().upper())
person_key={}
for r in people:
    person_key[key(r["First"],r["Last"],r["City"],r["State"])]=r["row_id"]

def overlay(path):
    if not os.path.exists(path): return 0
    n=0
    for r in csv.DictReader(open(path,encoding="utf-8")):
        k=key(r.get("First Name",""),r.get("Last Name",""),r.get("City",""),r.get("State",""))
        rid=person_key.get(k)
        if not rid: continue
        url=(r.get("LinkedIn URL") or "").strip()
        conf=(r.get("LinkedIn Confidence") or "").strip()
        notes=(r.get("LinkedIn Notes") or "").strip()
        email=(r.get("Email (found)") or "").strip()
        # only overlay when the hand pass adds signal (url / employer-confirmed / email)
        if url or email or conf.lower().startswith("employer") or conf in ("High","High (10/10)","Medium-High","Medium","Low"):
            li[rid]={"url":url,"conf":conf,"notes":notes+" [hand-verified]","email":email,"src":"hand"}
            n+=1
    return n
oc=overlay(os.path.join(ROOT,"bank_amc_enriched.csv"))+overlay(os.path.join(ROOT,"regional_enriched.csv"))

cols=["row_id","First","Middle","Last","Suffix","Lic State","License #","Title","Company","City","State","Zip","Phone",
      "LinkedIn URL","LinkedIn Confidence","LinkedIn Notes","Company Domain","Email"]
out=[]
for r in people:
    rid=r["row_id"]; l=li.get(rid,{})
    dom=company_domain.get(r["Company"].strip(),"") or curated_domain(r["Company"])
    out.append([rid,r["First"],r["Middle"],r["Last"],r["Suffix"],r["LicState"],r["License#"],r["Title"],
                r["Company"],r["City"],r["State"],r["Zip"],r["Phone"],
                l.get("url",""),l.get("conf",""),l.get("notes",""),dom,l.get("email","")])
with open(os.path.join(BASE,"master_enriched.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(cols); w.writerows(out)

n=len(out)
dom=sum(1 for x in out if x[16])
url=sum(1 for x in out if x[13])
empc=sum(1 for x in out if str(x[14]).lower().startswith("employer"))
notsr=sum(1 for x in out if x[14]=="not-searched")
liproc=sum(1 for x in out if x[14] and x[14]!="not-searched")
print(f"master_enriched.csv: {n} rows")
print(f"  company domain filled : {dom} ({100*dom//n}%)")
print(f"  LinkedIn URL          : {url}")
print(f"  employer-confirmed    : {empc}")
print(f"  LinkedIn processed    : {liproc}   (not-searched placeholders: {notsr})")
print(f"  hand-verified overlaid: {oc}")
