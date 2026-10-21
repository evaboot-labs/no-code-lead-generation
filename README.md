# No-code lead generation: Sales Navigator to Google Sheets, scored by AI

A weekly lead list without code. Evaboot exports your LinkedIn Sales Navigator search with
verified emails, an AI decision model scores every lead against your ideal customer profile,
and the leads land in a Google Sheet with an ICP score from 0 to 100.

Two ready-made versions, same result:

| | n8n | Make |
|---|---|---|
| File | [`n8n/sales-navigator-to-google-sheets-scored.json`](n8n/sales-navigator-to-google-sheets-scored.json) | [`make/evaboot-leads-to-google-sheets-scored.blueprint.json`](make/evaboot-leads-to-google-sheets-scored.blueprint.json) |
| Who starts the run | n8n, every Monday, asks Evaboot to export the search | Evaboot runs a weekly recurring export and pushes it to Make |
| Duplicates | A lead already in the sheet is updated | Every lead is added as a new row |

Built by [Evaboot](https://evaboot.com). More workflows: [github.com/evaboot-labs](https://github.com/evaboot-labs).

## What you need

- An [Evaboot](https://evaboot.com) account with LinkedIn Sales Navigator connected.
- An [OpenAI API key](https://platform.openai.com/api-keys) (scoring 1,000 leads costs about 8 cents).
- A Google Sheet with this header row:

  ```
  LinkedIn URL, First name, Last name, Job title, Company, Company domain, Industry, Employees, Company location, Email, ICP score, ICP fit, Confidence, Added on
  ```

- Your ideal customer profile. Start from [`ICP.md`](ICP.md) and replace every line.

Evaboot exports the whole search and uses one credit per lead, so keep the search focused.
A search with the "Changed jobs in the past 90 days" filter brings new people every week.

## n8n

1. Install the Evaboot node: **Settings > Community nodes**, package `@evaboot-team/n8n-nodes-evaboot`
   (it is a verified node, so it also works on n8n Cloud).
2. Create a new workflow, open the **…** menu next to its name and choose **Import from file**.
3. Add three credentials: **Evaboot** (API key from dash.evaboot.com > API key), **OpenAI** and **Google Sheets**.
4. Open **Your settings** and fill in:
   - your Sales Navigator search URL,
   - your ICP (paste your `ICP.md`),
   - the Google Sheet URL, copied while the right tab is open (it ends with `gid=…`).
5. Click **Execute workflow** to test, then **Publish** to run it every Monday at 8am.

The workflow keeps only leads that match your Sales Navigator filters and have a **safe** email,
then scores each one with the OpenAI Decisions API.

## Make

1. In Make, create a scenario, open the **…** menu and choose **Import Blueprint**.
2. Open the first module (**Evaboot export finished**), click **Add**, and copy the webhook URL.
3. Open **Build the OpenAI request**, click **Add data structure > Generate**, and paste the
   example below. Then put your ICP after "ideal customer profile below:" in **instructions**.

   ```json
   {"model": "gpt-6-luna", "input": "lead", "questions": [{"type": "score", "name": "icp_fit", "instructions": "text", "levels": [{"label": "No fit", "description": "text"}]}]}
   ```

4. Open **Score against ICP**, and replace `YOUR_OPENAI_API_KEY` in the Authorization header.
5. Open **Add to the lead sheet**, connect Google, and choose your sheet and tab.
6. Turn the scenario on.
7. In Evaboot, open **Integrations > New integration > Make**, paste the webhook URL, and choose to
   push the runs of a **recurring export** of your Sales Navigator search (weekly).

To test it once, push any finished export to the Make integration from Evaboot.

## How the score works

Each lead goes to the [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions)
(model `gpt-6-luna`) as one `score` question with four levels: No fit, Weak fit, Partial fit and
Strong fit. The answer is a score from 0 to 3 and a confidence. The workflows store it as:

| Column | Example | Meaning |
|---|---|---|
| ICP score | 83 | score ÷ 3 × 100 |
| ICP fit | Strong fit | the nearest level |
| Confidence | 0.5 | how sure the model is, 0 to 1 |

Sort the sheet by **ICP score**, not only by the label: an 80 can still be "Partial fit".
For the same scoring with a Python script, HubSpot and an AI coding agent, see
[ai-driven-lead-scoring](https://github.com/evaboot-labs/ai-driven-lead-scoring).

## License

MIT
