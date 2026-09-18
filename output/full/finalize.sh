#!/bin/bash
cd /home/user/LinkedIn-Finder
while pgrep -f resolve_domains.py >/dev/null; do sleep 30; done
python3 output/full/build_master.py > output/full/final_stats.txt 2>&1
git add -A
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "Finalize full-list company domains (resolver complete)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_013HLmLBfTRYBsQvsFoR8CJV"
git push -u origin claude/tender-mayer-w6l8v0 2>&1 | tail -1
