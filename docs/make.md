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


## Use JEV instead of OpenAI

If you have a [Typesafe JEV](https://typesafe.ai) key, import
[`make/evaboot-leads-to-google-sheets-scored-jev.blueprint.json`](../make/evaboot-leads-to-google-sheets-scored-jev.blueprint.json)
and follow the same steps, with two changes. In step 3, generate the data structure from this
example. In step 4, replace `YOUR_JEV_API_KEY`.

```json
{"model": "jev-1.14.0", "state": {"ideal_customer_profile": "text", "lead": "text"}, "questions": {"icp_fit": {"type": "score", "instructions": "text", "criteria": ["text"]}}}
```

Your ICP goes in **state > ideal_customer_profile**. The template is pinned to `jev-1.14.0`, so
a new JEV release does not move your scores.

Back to the [README](../README.md).
