# Agent instructions

This repo sets up a weekly lead list without code: Evaboot exports a LinkedIn Sales Navigator search with verified emails, an AI decision model (the OpenAI Decisions API) scores each lead against `ICP.md`, and the leads land in a Google Sheet with an ICP score from 0 to 100. It ships two ready-made versions, an n8n workflow and a Make scenario. When the user asks for a lead list, to score Sales Navigator leads, or to send them to Google Sheets:

1. Follow the skill in `skills/build-lead-list/SKILL.md` step by step.
2. Read `ICP.md` first and interview the user if it still holds the example.
3. For the setup clicks, follow `docs/n8n.md` or `docs/make.md`. `docs/scoring.md` explains the score columns.
4. After editing `ICP.md` on the n8n path, run `python3 n8n/build_workflow.py` so the workflow file carries the new profile.

Confirm with the user before every call that saves, sends or changes anything, and before any run that spends Evaboot credits or creates a recurring export. Never ask for or handle another tool's API key: the user connects Evaboot, OpenAI and Google in n8n or Make. Never commit `.env`.
