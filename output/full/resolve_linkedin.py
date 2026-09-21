#!/usr/bin/env python3
"""Resolve LinkedIn profile URLs for every appraiser via Firecrawl /v1/search (curl).
Resumable: skips row_ids already in li_firecrawl.tsv. Writes: row_id\turl\tconfidence\ttitle\temail"""
import subprocess, threading, os, json, re, time, sys
from concurrent.futures import ThreadPoolExecutor

BASE=os.path.dirname(__file__)
PEOPLE=os.path.join(BASE,"people.csv")
OUT=os.path.join(BASE,"li_firecrawl.tsv")
API="https://api.firecrawl.dev/v1/search"

# Firecrawl API key: from env, else a gitignored key file. Empty => keyless free tier
# (a few hundred searches then a ~5h lockout, so it can't sweep the full list alone).
KEY=os.environ.get("FIRECRAWL_API_KEY","").strip()
_KEYFILE=os.path.join(BASE,".firecrawl_key")
if not KEY and os.path.exists(_KEYFILE):
    try: KEY=open(_KEYFILE,encoding="utf-8").read().strip()
    except Exception: KEY=""
WORKERS=int(os.environ.get("FIRECRAWL_WORKERS", "6" if KEY else "4"))
STOP=threading.Event()   # set when quota/credits are exhausted -> halt the run gracefully
GENERIC={"appraisal","appraisals","appraiser","real","estate","valuation","valuations","services",
         "service","group","company","inc","llc","the","and","associates","company,","of","co",
         "residential","commercial","properties","property","home","bank","na"}
EMAIL_RE=re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
lock=threading.Lock()

def norm(s): return re.sub(r"[^a-z0-9]","",(s or "").lower())

NICK=[{"mike","michael"},{"bill","will","william"},{"bob","rob","robert","bobby"},{"jim","jimmy","james"},
 {"joe","joey","joseph"},{"tom","tommy","thomas"},{"dave","david"},{"dan","danny","daniel"},
 {"chris","christopher"},{"matt","matthew"},{"tony","anthony"},{"rick","rich","richard","dick"},
 {"fred","frederick","freddie"},{"ken","kenny","kenneth"},{"ron","ronnie","ronald"},{"don","donnie","donald"},
 {"steve","steven","stephen"},{"jeff","jeffrey","jeffery"},{"greg","gregory"},{"ed","eddie","edward"},
 {"sam","samuel"},{"ben","benjamin","benjaman"},{"andy","drew","andrew"},{"nick","nicholas"},
 {"pat","patrick","patricia"},{"tim","timothy"},{"kathy","katherine","catherine","kate"},
 {"liz","beth","betty","elizabeth"},{"sue","susan","susie"},{"jen","jenny","jennifer"},
 {"deb","debbie","deborah"},{"kim","kimberly"},{"chuck","charlie","charles"},{"hank","henry"},
 {"larry","lawrence"},{"terry","terrence","terrance"},{"jack","john","johnny","jonathan"},
 {"gene","eugene"},{"peggy","meg","margaret"},{"cindy","cynthia"},{"becky","rebecca"},{"tem","temp"}]
def first_match(a,b):
    a=norm(a); b=norm(b)
    if not a or not b: return False
    if a==b: return True
    if (a.startswith(b) or b.startswith(a)) and min(len(a),len(b))>=3: return True
    for s in NICK:
        if a in s and b in s: return True
    return False

def search(query, tries=4):
    body=json.dumps({"query":query,"limit":5})
    cmd=["curl","-s","-X","POST",API,"-H","Content-Type: application/json"]
    if KEY: cmd+=["-H",f"Authorization: Bearer {KEY}"]
    cmd+=["-d",body,"--max-time","40"]
    for i in range(tries):
        if STOP.is_set(): return None
        try:
            r=subprocess.run(cmd,capture_output=True,text=True,timeout=50,errors="ignore")
            d=json.loads(r.stdout)
            if isinstance(d,dict) and d.get("data") is not None:
                return d["data"]
            # error response: distinguish credit/quota exhaustion (STOP) from transient RPM (backoff)
            if isinstance(d,dict):
                reason=str(d.get("reason","")).lower()
                err=str(d.get("error","")).lower()
                exhausted = (reason=="credits" or "insufficient" in err or "out of credit" in err
                             or "quota" in err or "upgrade" in err or "payment" in err
                             or ("credit" in err and "rate limit" not in err))
                if exhausted:
                    STOP.set()          # credits gone -> don't churn, halt the whole run
                    return None
                # transient (RPM 429 etc.): honor retry_after if given, capped
                ra=d.get("retry_after_seconds")
                if isinstance(ra,(int,float)) and 0<ra<=60:
                    time.sleep(ra); continue
            time.sleep(2*(i+1))         # transient -> backoff and retry
        except Exception:
            time.sleep(2*(i+1))
    return None

def score(person, results):
    first=norm(person["First"]); last=norm(person["Last"].split(",")[0])
    city=(person["City"] or "").lower(); state=(person["State"] or "").upper()
    comp=person["Company"] or ""
    comp_tokens={norm(t) for t in re.split(r"[^A-Za-z0-9]+",comp) if len(t)>=4 and norm(t) not in GENERIC}
    comp_tokens-={first,last}   # a firm named after the person shouldn't self-corroborate
    best=None
    for r in results or []:
        url=(r.get("url") or "").split("?")[0].split("#")[0].rstrip("/")
        m=re.match(r"https?://([a-z]{2,3}\.)?linkedin\.com/in/([A-Za-z0-9_%-]+)$",url)
        if not m: continue
        slug=norm(m.group(2))
        title=(r.get("title") or ""); desc=(r.get("description") or "")
        blob=norm(title+" "+desc); dl=(title+" "+desc).lower()
        if not last or last not in (norm(title)+slug): continue      # last name must appear
        # the profile's own first name (leading token of the title) must match ours
        prof_first=re.split(r"[^A-Za-z]+", title.strip()+" ")[0]
        if not first_match(first, prof_first):   # profile's own first name must match ours
            continue
        rank_first = 2 if norm(first)==norm(prof_first) else 1
        appr_title = any(k in title.lower() for k in ["apprais","valuation","valuer"])
        appr = appr_title or any(k in dl for k in ["apprais","valuation","valuer"])
        loc  = bool((city and city in dl) or (state and re.search(r"\b"+re.escape(state)+r"\b",title+" "+desc)))
        compm= any(t and t in blob for t in comp_tokens)
        if   appr_title and (loc or compm): conf="High"
        elif appr:                          conf="Medium"   # appraiser signal (often in description)
        elif compm:                         conf="Low"      # name+company, no explicit appraiser word
        else:                               continue         # name-only / loc-only -> too weak, skip
        rankkey=( conf=="High", conf=="Medium", appr_title, appr, bool(loc or compm), rank_first )
        cand=(rankkey,url,conf,title.replace("\t"," ").strip())
        if best is None or cand[0]>best[0]: best=cand
    if not best: return ("","none","","")
    # email from any result description
    email=""
    for r in results or []:
        mm=EMAIL_RE.search((r.get("description") or "")+" "+(r.get("title") or ""))
        if mm: email=mm.group(0); break
    return (best[1],best[2],best[3],email)

def work(person):
    if STOP.is_set(): return
    rid=person["row_id"]
    q=f'{person["First"]} {person["Last"].split(",")[0]} appraiser {person["City"]} {person["State"]} {person["Company"]} linkedin'
    res=search(q)
    if res is None:
        return  # transient failure / quota stop -> leave unrecorded so it retries on the next run
    url,conf,title,email=score(person,res)
    line="\t".join([rid,url,conf,title,email])+"\n"
    with lock:
        with open(OUT,"a",encoding="utf-8") as f: f.write(line)

def main():
    import csv
    people=list(csv.DictReader(open(PEOPLE)))
    done=set()
    if os.path.exists(OUT):
        for l in open(OUT,encoding="utf-8"):
            rid=l.split("\t",1)[0].strip()
            if rid: done.add(rid)
    todo=[p for p in people if p["row_id"] not in done]
    print(f"to process: {len(todo)} (already done {len(done)}) | key={'yes' if KEY else 'NO (keyless)'} workers={WORKERS}", flush=True)
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(work, todo))
    if STOP.is_set():
        print("STOPPED: Firecrawl quota/credits exhausted. Resume after reset, or set "
              "FIRECRAWL_API_KEY / write output/full/.firecrawl_key and rerun.", flush=True)
        sys.exit(3)
    print("linkedin resolve done", flush=True)

if __name__=="__main__":
    main()
