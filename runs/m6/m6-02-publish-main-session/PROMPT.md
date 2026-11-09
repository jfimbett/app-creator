# PROMPT — m6-02-publish-main-session

- Sender: the instructor (owner of the repository), typed into the top-level Claude Code session on 2026-11-09
- Receiver: top-level Claude Code session (Opus 5.5), working directly in the main checkout
- Starting commit: 5b9d905 on main (tag `m6` was at c44982a, before the audio remix)
- Context: M6 had been reported done and not pushed. The instructor then reported no sound and a hydration error
  (follow-up 2: the server's stale build cache was cleared and the music remixed), said the video had no voice and
  asked to stop the server (follow-up 3: they chose to keep the video as it is). The assistant had asked whether to move
  the local, unpublished tag `m6` to the remixed commit. The text below is the exact next instruction.

<!-- DISPATCH:BEGIN -->
ok commit and push m6, and make sure all branches are properly explained, witht heir prompts recorded etc. just like we did with m1 and m2
<!-- DISPATCH:END -->

## Decisions recorded before work

- **Tag `m6`:** "push m6" after the remix is read as publishing M6 as the instructor last reviewed it. The tag and the
  branch `milestone/06-polish-and-launch` were local and never published, so they are moved to the final M6 commit (the
  one that adds this record and the branch documentation), which includes the audible video. Nothing published is
  rewritten.
- **Branch documentation:** README.md (branches and tags table), CLASSROOM.md, START-HERE.md, milestones/README.md and
  milestones/PROMPT-INDEX.md are brought up to date for M6 and every published branch, as the instruction asks.
- **What is pushed:** `main`, `milestone/06-polish-and-launch` and tag `m6`. Local `work/*` branches stay unpublished.
  No force push; no other branch, tag or remote setting changes.
