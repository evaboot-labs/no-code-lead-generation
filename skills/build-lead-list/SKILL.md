---
name: build-lead-list
description: Set up a weekly scored lead list for the user - Evaboot exports a Sales Navigator search with verified emails, an AI decision model scores each lead against ICP.md, and the leads land in a Google Sheet - with the n8n workflow or the Make scenario in this repo. Use when the user asks for a lead list, to score Sales Navigator leads, or to send leads to Google Sheets without code.
---

# Build a weekly scored lead list

Run this inside a clone of `evaboot-labs/no-code-lead-generation`. The user ends with an n8n workflow or a Make scenario that fills a Google Sheet with Sales Navigator leads, each scored 0 to 100 against their ideal customer profile.

## Step 0: accounts

Check, one by one, that the user has:

1. **An Evaboot account with Sales Navigator connected.** If not, send them to https://dash.evaboot.com/accounts/signup/?last_click_origin=no-code-lead-generation-repo and the Evaboot Chrome extension (https://dash.evaboot.com/install/).
2. **An OpenAI API key** (https://platform.openai.com/api-keys). Scoring 1,000 leads costs about 8 cents.
3. **A Google Sheet** whose first row is exactly:

   ```
   LinkedIn URL, First name, Last name, Job title, Company, Company domain, Industry, Employees, Company location, Email, ICP score, ICP fit, Confidence, Added on
   ```

4. **n8n or Make.** Either works; step 2 helps choose.

The user enters every key in n8n or Make credentials. Never ask for a key in the chat.

## Step 1: the ideal customer profile

Read `ICP.md`. If it still holds the example (B2B software, 11 to 500 employees, Sales and Growth buyers), interview the user and rewrite it:

- company must-haves: industry, size, location, business model;
- buyer must-haves: function and seniority;
- positive signals, which raise the fit without being required;
- disqualifiers, which always mean No fit.

Write each criterion so a stranger could answer yes or no from a LinkedIn profile. Keep the file short: the model reads all of it for every lead. Show the new `ICP.md` and get a yes before going on.

Then ask for the Sales Navigator search URL. Advise a focused search: Evaboot exports the whole search and uses one credit per lead. A "Changed jobs in the past 90 days" filter brings new people every week.

## Step 2: n8n or Make

| | n8n | Make |
|---|---|---|
| Who starts the run | n8n, every Monday at 8am, asks Evaboot to export the search | an Evaboot weekly recurring export pushes each batch to Make |
| Duplicates | a lead already in the sheet is updated | every lead is added as a new row |

Recommend the tool the user already pays for. With neither, recommend n8n: it never adds duplicate rows.

## Step 3a: the n8n path

1. Rebuild the workflow so it carries the new ICP: `python3 n8n/build_workflow.py`. It writes `n8n/sales-navigator-to-google-sheets-scored.json`.
2. Walk the user through `docs/n8n.md`: install the Evaboot community node, import the file, add the three credentials (Evaboot, OpenAI, Google Sheets).
3. In **Your settings**, the user pastes the Sales Navigator URL and the Google Sheet URL (copied with the right tab open, ending in `gid=…`).

## Step 3b: the Make path

Walk the user through `docs/make.md`: import the blueprint, copy the webhook URL, generate the data structure, paste the ICP into **instructions**, put the OpenAI key in the **Score against ICP** header, connect Google, turn the scenario on, then create the Evaboot Make integration and the weekly recurring export of the search.

## Step 4: the first run

Before the first run, tell the user how many leads the search returns and that each one costs one Evaboot credit. Run only after a yes:

- n8n: **Execute workflow** once, then **Publish** for the Monday schedule.
- Make: push one finished Evaboot export to the Make integration.

Check the sheet: every row has an ICP score, a fit and a confidence. Tell the user to sort by **ICP score**, not only by the fit label.

## Step 5: finish

End with a table: tool, workflow or scenario name, sheet, search, schedule, and what each run costs. Mention [ai-driven-lead-scoring](https://github.com/evaboot-labs/ai-driven-lead-scoring) for the same scoring in HubSpot.

## Safety rules

- Confirm before anything that spends Evaboot credits or creates a recurring export.
- Never ask for, read or store the OpenAI, Google or Evaboot key. The user enters them in n8n or Make.
- Never commit `.env`.
