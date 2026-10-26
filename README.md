<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/banner-dark.png">
  <img src=".github/assets/banner-light.png" alt="Sales Navigator search, Evaboot export, AI decision model, Google Sheet: a scored lead list every week" width="1280">
</picture>

# No-code lead generation

A scored lead list every week, without code. Evaboot exports your Sales Navigator search with verified emails, an AI decision model scores every lead against your ideal customer profile, and the leads land in a Google Sheet.

[![Works with Claude Code · Codex · Cursor](https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor-5719D9)](AGENTS.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-5719D9)](LICENSE)
[![Use this template](https://img.shields.io/badge/template-use%20this%20template-5719D9)](https://github.com/evaboot-labs/no-code-lead-generation/generate)

[![An AI Agent rewrites the ideal customer profile, picks n8n and lists the import steps](.github/assets/demo.gif)](.github/assets/demo.mp4)

<sub>The full run, at real speed: [demo.mp4](.github/assets/demo.mp4)</sub>

## Set it up in one prompt

Paste this into Claude Code, Codex or Cursor:

```text
Set up the Evaboot no-code lead list for me. Clone
https://github.com/evaboot-labs/no-code-lead-generation, read AGENTS.md and follow the
build-lead-list skill. Ask me about my ideal customer and whether I use n8n or Make, and
confirm with me before anything that spends Evaboot credits.
```

<details>
<summary>Or install the skill</summary>

Claude Code:

```text
/plugin marketplace add evaboot-labs/no-code-lead-generation
/plugin install no-code-lead-generation@evaboot-labs-no-code-lead-generation
```

Codex, Cursor and other agents:

```bash
npx skills add evaboot-labs/no-code-lead-generation
```

</details>

## How it works

**1. Save a focused search.** Evaboot exports the whole search, so keep it narrow.

<img src=".github/assets/screenshots/1-saved-search.png" alt="A focused Sales Navigator lead search" width="800">

**2. Import the workflow.** n8n or Make, with your Evaboot, OpenAI and Google credentials.

<img src=".github/assets/screenshots/2-workflow.png" alt="The imported n8n workflow" width="800">

**3. Get a scored sheet every week.** Each lead has an ICP score, a fit and a confidence.

<img src=".github/assets/screenshots/3-scored-sheet.png" alt="The Google Sheet with ICP score, fit and confidence filled in" width="800">

## n8n or Make, same sheet

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".github/assets/templates-dark.png">
  <img src=".github/assets/templates-light.png" alt="Two templates: n8n asks Evaboot every Monday and updates known leads; Make receives a weekly Evaboot export and adds every lead as a new row" width="1280">
</picture>

Both score each lead against [`ICP.md`](ICP.md) with the OpenAI Decisions API: [how the score works](docs/scoring.md). Each template also has a Typesafe JEV copy, for teams with a JEV key.

## What you need

- **An Evaboot account** with LinkedIn Sales Navigator connected. [Create one](https://dash.evaboot.com/accounts/signup/?last_click_origin=no-code-lead-generation-repo).
- **An OpenAI API key.** Scoring 1,000 leads costs about 8 cents.
- **A Google Sheet** with the header row from [the skill](skills/build-lead-list/SKILL.md).
- **n8n or Make.**
- **Cost:** one Evaboot credit per lead exported, plus the OpenAI cost.

## Go further

| Page | For |
|---|---|
| [n8n workflow](docs/n8n.md) | Install the Evaboot node, import, fill in your settings |
| [Make scenario](docs/make.md) | Import the blueprint and connect a weekly Evaboot export |
| [How the score works](docs/scoring.md) | The ICP score, fit and confidence columns |

---

Agents: start at [AGENTS.md](AGENTS.md) · Built by [Evaboot](https://evaboot.com) · More workflows at [github.com/evaboot-labs](https://github.com/evaboot-labs) · [MIT license](LICENSE)
