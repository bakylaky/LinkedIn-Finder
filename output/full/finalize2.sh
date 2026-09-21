#!/bin/bash
# Self-healing watcher: keeps the two resolvers alive, snapshots progress to git every ~3.5 min,
# stops when both are complete. Survives being re-launched (resolvers skip already-done rows).
cd /home/user/LinkedIn-Finder
RL="output/full/resolve_linkedin.py"; RD="output/full/resolve_domains.py"
BR="claude/tender-mayer-w6l8v0"
snap(){
  python3 output/full/build_master.py > output/full/final_stats.txt 2>&1
  git add -A
  git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "Progress snapshot: domains + LinkedIn resolving

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_013HLmLBfTRYBsQvsFoR8CJV" 2>/dev/null
  for i in 1 2 3 4; do git push origin "$BR" >/dev/null 2>&1 && break || sleep $((i*3)); done
}
last=-1
while true; do
  li=$(wc -l < output/full/li_firecrawl.tsv 2>/dev/null); li=${li:-0}
  dm=$(wc -l < output/full/domain_probe.tsv 2>/dev/null); dm=${dm:-0}
  if ! pgrep -f resolve_linkedin.py >/dev/null && [ "$li" -lt 11150 ] && [ "$li" -gt "$last" ]; then
     setsid bash -c "cd /home/user/LinkedIn-Finder && python3 $RL >> output/full/li_resolve.log 2>&1" </dev/null >/dev/null 2>&1 &
  fi
  if ! pgrep -f resolve_domains.py >/dev/null && [ "$dm" -lt 18486 ]; then
     setsid bash -c "cd /home/user/LinkedIn-Finder && python3 $RD >> output/full/resolve.log 2>&1" </dev/null >/dev/null 2>&1 &
  fi
  snap
  if ! pgrep -f 'resolve_linkedin.py|resolve_domains.py' >/dev/null && [ "$li" -le "$last" ] && [ "$dm" -ge 18486 ]; then
     break
  fi
  last=$li
  sleep 200
done
snap
echo done > output/full/finalize2.done
