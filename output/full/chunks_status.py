import csv, os, glob, re
BASE=os.path.dirname(__file__)
done_full=[]; partial=[]; todo=[]
for n in range(1,114):
    cid=f"{n:03d}"; fp=os.path.join(BASE,"li_chunks",f"out_{cid}.csv")
    if not os.path.exists(fp): todo.append(cid); continue
    rows=list(csv.DictReader(open(fp,encoding="utf-8")))
    ns=sum(1 for r in rows if re.search(r"not searched|budget",(r.get("notes") or ""),re.I))
    if ns==0 and rows: done_full.append(cid)
    else: partial.append((cid,ns))
print(f"chunks fully processed : {len(done_full)}")
print(f"chunks partial (capped): {len(partial)}  -> {[c for c,_ in partial]}")
print(f"chunks not started     : {len(todo)}")
# write a todo list = partial + not-started
with open(os.path.join(BASE,"chunks_todo.txt"),"w") as f:
    for c,_ in partial: f.write(c+"\n")
    for c in todo: f.write(c+"\n")
print(f"wrote chunks_todo.txt ({len(partial)+len(todo)} chunks need (re)processing)")
