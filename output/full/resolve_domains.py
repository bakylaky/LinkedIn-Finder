#!/usr/bin/env python3
import subprocess, threading, os
from concurrent.futures import ThreadPoolExecutor

BASE=os.path.dirname(__file__)
CANDS=os.path.join(BASE,"company_candidates.tsv")
OUT=os.path.join(BASE,"domain_probe.tsv")
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
BAD=["for sale","buy this domain","domain is for sale","parkingcrew","sedoparking","hugedomains",
     "godaddy.com/forsale","afternic","dan.com","this domain","domain parking","namecheap parking",
     "courtesy of","related searches","is for sale"]
STRONG=["apprais","valuation","valuations"]
WEAK=["real estate","property","home value","residential","comparable"]

lock=threading.Lock()
done=set()
if os.path.exists(OUT):
    for l in open(OUT,encoding="utf-8"):
        p=l.split("\t")
        if len(p)>=2: done.add((p[0],p[1]))

def _curl(url):
    try:
        r=subprocess.run(["curl","-sL","--max-time","15","--connect-timeout","8","-A",UA,
                          "-w","\n__CODE__%{http_code}\n__URL__%{url_effective}",url],
                         capture_output=True, text=True, timeout=25, errors="ignore")
        return r.stdout or ""
    except Exception:
        return ""

def probe(company, domain):
    dslug=domain[:-4]
    branded = any(t in dslug for t in ["apprais","valuation","valuations","valuate"])
    out=_curl("https://"+domain)
    def parse(out):
        code=""; final=""
        for line in out.splitlines():
            if line.startswith("__CODE__"): code=line[8:].strip()
            elif line.startswith("__URL__"): final=line[7:].strip()
        return code, final, out.lower()
    code,final,body=parse(out)
    # retry www when apex fails or is blank
    if (not code or code=="000" or code.startswith(("4","5")) or len(body)<200) and not domain.startswith("www."):
        out2=_curl("https://www."+domain)
        c2,f2,b2=parse(out2)
        if c2 and c2!="000" and not c2.startswith(("4","5")) and len(b2)>=len(body):
            code,final,body=c2,f2,b2
    if not code or code=="000" or code.startswith(("4","5")):
        return (company,domain,"dead",code or "000")
    fl=final.lower()
    if any(b in fl for b in ["godaddy","sedo","afternic","hugedomains","dan.com","bodis","parking"]):
        return (company,domain,"parked","redir")
    if any(b in body for b in BAD):
        return (company,domain,"parked","body")
    if any(k in body for k in STRONG):
        return (company,domain,"HIT_strong",code)
    if any(k in body for k in WEAK):
        return (company,domain,"HIT_weak",code)
    if len(body)<200:
        # resolves but JS/empty: accept only if the domain itself is appraisal-branded
        return (company,domain,("HIT_slug" if branded else "empty"),code)
    return (company,domain,("HIT_slug" if branded else "nomatch"),code)

def work(line):
    line=line.rstrip("\n")
    if "\t" not in line: return
    company,domain=line.split("\t",1)
    if (company,domain) in done: return
    res=probe(company,domain)
    with lock:
        with open(OUT,"a",encoding="utf-8") as f:
            f.write("\t".join(res)+"\n")

def main():
    lines=[l for l in open(CANDS,encoding="utf-8")]
    with ThreadPoolExecutor(max_workers=16) as ex:
        list(ex.map(work, lines))
    print("probe done")

if __name__=="__main__":
    main()
