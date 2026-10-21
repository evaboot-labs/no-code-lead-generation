# How the score works

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

Back to the [README](../README.md).
