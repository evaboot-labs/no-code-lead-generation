# The n8n workflow

n8n asks Evaboot to export your Sales Navigator search every Monday at 8am, scores each lead and adds or updates it in your Google Sheet. The file is [`n8n/sales-navigator-to-google-sheets-scored.json`](../n8n/sales-navigator-to-google-sheets-scored.json). To embed a new `ICP.md` in it, run `python3 n8n/build_workflow.py`.

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

Back to the [README](../README.md).
