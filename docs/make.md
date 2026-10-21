# The Make scenario

Evaboot runs a weekly recurring export of your Sales Navigator search and pushes each batch to Make, which scores every lead and adds it to your Google Sheet as a new row. The file is [`make/evaboot-leads-to-google-sheets-scored.blueprint.json`](../make/evaboot-leads-to-google-sheets-scored.blueprint.json).

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

Back to the [README](../README.md).
