import json, csv, os
base=os.path.dirname(__file__)
targets=list(csv.DictReader(open(os.path.join(base,"bank_amc_targets.csv"))))
F=json.load(open(os.path.join(base,".findings.json")))
domain={"MountainSeed":"mountainseed.com","Synovus":"synovus.com","Dart Appraisal":"dartappraisal.com",
 "Amrock":"amrock.com","ServiceLink":"servicelink.com","Regions Bank":"regions.com","Solidifi":"solidifi.com",
 "Wells Fargo":"wellsfargo.com","Opteon":"opteonsolutions.com","Bank of America":"bankofamerica.com",
 "US Bank":"usbank.com","Class Valuation":"classvaluation.com","JPMorgan Chase":"jpmorganchase.com","BMO":"bmo.com",
 "Nationwide Appraisal Network":"nationwideappraisalnetwork.com","First Citizens Bank":"firstcitizens.com",
 "Accurate Group":"accurategroup.com","First American":"firstam.com","CoreLogic":"corelogic.com",
 "Rally Appraisal":"rallyappraisal.com","PCV Murcor":"pcvmurcor.com","Consolidated Analytics":"consolidatedanalytics.com"}
cols=["#","Employer Type","Employer","First Name","Middle Name","Last Name","Suffix","Lic State","License #",
      "Title","City","State","Phone","LinkedIn URL","LinkedIn Confidence","LinkedIn Notes","Company Domain","Email (found)"]
out=[]
for pos,t in enumerate(targets, start=1):
    if pos==17: continue
    if str(pos) not in F: continue
    url,conf,notes,email=F[str(pos)]
    out.append([pos,t["EmployerType"],t["Employer"],t["First"],t["Middle"],t["Last"],t["Suffix"],
                t["LicState"],t["License#"],t["Title"],t["City"],t["State"],t["Phone"],
                url,conf,notes,domain.get(t["Employer"],""),email])
with open(os.path.join(base,"bank_amc_enriched.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(cols); w.writerows(out)
urls=sum(1 for r in out if r[13])
print(f"built bank_amc_enriched.csv: {len(out)} rows, {urls} with LinkedIn URL")
