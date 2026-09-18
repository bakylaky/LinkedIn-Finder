import json, csv, os
base=os.path.dirname(__file__)
targets=list(csv.DictReader(open(os.path.join(base,"regional_targets.csv"))))
F=json.load(open(os.path.join(base,".regional_findings.json")))
domain={"WAIV Valuation":"waiv.com","True Footage":"truefootage.tech","Property Sciences":"propsci.com",
 "Accurity Consolidated":"accurity.com","RSDS Valuations":"rsdsllc.com",
 "Definitive Valuations":"definitivevaluations.com","Griffin Appraisals":"",
 "EFIRD Appraisals":"efirdappraisals.com","Martin Appraisal Group":""}
cols=["#","Firm","First Name","Middle Name","Last Name","Suffix","Lic State","License #","Title","City","State","Phone",
      "LinkedIn URL","LinkedIn Confidence","LinkedIn Notes","Company Domain","Email (found)"]
out=[]
for pos,t in enumerate(targets,1):
    if str(pos) not in F: continue
    url,conf,notes,email=F[str(pos)]
    out.append([pos,t["Firm"],t["First"],t["Middle"],t["Last"],t["Suffix"],t["LicState"],t["License#"],
                t["Title"],t["City"],t["State"],t["Phone"],url,conf,notes,domain.get(t["Firm"],""),email])
with open(os.path.join(base,"regional_enriched.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(cols); w.writerows(out)
print(f"built regional_enriched.csv: {len(out)} rows, {sum(1 for r in out if r[12])} with URL")
