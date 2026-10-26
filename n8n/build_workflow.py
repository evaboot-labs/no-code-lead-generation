"""Build the n8n template JSON. Run: python3 n8n/build_workflow.py"""
import json
import uuid
from pathlib import Path

HERE = Path(__file__).parent
ICP = (HERE.parent / "ICP.md").read_text()
EVABOOT_CRED = {"evabootApi": {"id": "", "name": "Evaboot account"}}
OPENAI_CRED = {"openAiApi": {"id": "", "name": "OpenAI"}}
SHEETS_CRED = {"googleSheetsOAuth2Api": {"id": "", "name": "Google Sheets"}}
EVABOOT = "@evaboot-team/n8n-nodes-evaboot.evaboot"


JEV_CRED = {"httpHeaderAuth": {"id": "", "name": "Typesafe JEV"}}


def jev_body(lead_expr, icp_expr):
    """The same score question for Typesafe JEV. Pinned to a release so the levels keep scoring the same."""
    return f"""={{{{ JSON.stringify({{
  model: 'jev-1.14.0',
  state: {{ ideal_customer_profile: {icp_expr}, lead: {lead_expr} }},
  questions: {{ icp_fit: {{
    type: 'score',
    instructions: 'How well does `lead` match `ideal_customer_profile`?',
    criteria: [
      'No fit: Fails a disqualifier, or matches none of the must-haves.',
      'Weak fit: Matches one must-have. The other must-haves fail or are unknown.',
      'Partial fit: Matches most must-haves, but one fails or is unknown.',
      'Strong fit: Matches every must-have and no disqualifier.'
    ]
  }} }}
}}) }}}}"""


def to_jev(workflow, score_node, map_node):
    """Swap the OpenAI scoring node for Typesafe JEV. Everything else stays the same."""
    text = json.dumps(workflow, ensure_ascii=False)
    text = text.replace("the OpenAI Decisions API", "Typesafe JEV").replace("The OpenAI Decisions API", "Typesafe JEV").replace("**OpenAI**", "**Typesafe JEV** (Header Auth: name `Authorization`, value `Bearer YOUR_KEY`)")
    text = text.replace("an OpenAI API key", "a Typesafe JEV API key")
    jev = json.loads(text)
    jev["name"] += " (JEV)"
    for n in jev["nodes"]:
        if n["name"] == score_node:
            n["parameters"].update({"url": "https://api.typesafe.ai/v1/systemone", "authentication": "genericCredentialType",
                                    "genericAuthType": "httpHeaderAuth", "jsonBody": JEV_BODY})
            n["parameters"].pop("nodeCredentialType", None)
            n["credentials"] = JEV_CRED
        if n["name"] == map_node:
            n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace("$json.answers[0]", "$json.answers.icp_fit")
    return jev


def node(name, type_, version, position, parameters, **extra):
    return {"id": str(uuid.uuid5(uuid.NAMESPACE_URL, "nocode/" + name)), "name": name, "type": type_,
            "typeVersion": version, "position": position, "parameters": parameters, **extra}


def sticky(name, position, width, height, content, color=7):
    return node(name, "n8n-nodes-base.stickyNote", 1, position,
                {"color": color, "width": width, "height": height, "content": content})


def condition(left, operator, right=""):
    return {"id": str(uuid.uuid4()), "leftValue": left, "rightValue": right, "operator": operator}


DECISION_BODY = """={{ JSON.stringify({
  model: 'gpt-6-luna',
  input: [
    'Job title: ' + $json['Current Job'],
    'Company: ' + $json['Company Name'],
    'Company industry: ' + ($json['Company Industry'] || 'unknown'),
    'Company employees: ' + ($json['Company Employee Exact Count'] || 'unknown'),
    'Company location: ' + ($json['Company Location'] || 'unknown'),
    'Lead location: ' + ($json['Location'] || 'unknown'),
    'Sales team size: ' + ($json['Sales Team Size'] || 'unknown'),
    'Company description: ' + String($json['Company Description'] || '').slice(0, 600)
  ].join('\\n'),
  questions: [{
    type: 'score',
    name: 'icp_fit',
    instructions: 'How well does this lead match the ideal customer profile below?\\n\\n' + $('Your settings').first().json.icp,
    levels: [
      { label: 'No fit', description: 'Fails a disqualifier, or matches none of the must-haves.' },
      { label: 'Weak fit', description: 'Matches one must-have. The other must-haves fail or are unknown.' },
      { label: 'Partial fit', description: 'Matches most must-haves, but one fails or is unknown.' },
      { label: 'Strong fit', description: 'Matches every must-have and no disqualifier.' }
    ]
  }]
}) }}"""

BUILD_ROW = """// One sheet row per lead: the Evaboot data plus the AI fit score.
const lead = $('Keep matching leads with a safe email').item.json;
const answer = $json.answers[0];
const fits = ['No fit', 'Weak fit', 'Partial fit', 'Strong fit'];
return {
  'LinkedIn URL': lead['Linkedin URL Public'],
  'First name': lead['First Name'],
  'Last name': lead['Last Name'],
  'Job title': lead['Current Job'],
  'Company': lead['Company Name'],
  'Company domain': lead['Company Domain'],
  'Industry': lead['Company Industry'],
  'Employees': lead['Company Employee Exact Count'],
  'Company location': lead['Company Location'],
  'Email': lead['Email'],
  'ICP score': Math.round(answer.score / 3 * 100),
  'ICP fit': fits[Math.round(answer.score)],
  'Confidence': Math.round(answer.confidence * 100) / 100,
  'Added on': $now.toFormat('yyyy-LL-dd'),
};"""

JEV_BODY = jev_body("""[
      'Job title: ' + $json['Current Job'],
      'Company: ' + $json['Company Name'],
      'Company industry: ' + ($json['Company Industry'] || 'unknown'),
      'Company employees: ' + ($json['Company Employee Exact Count'] || 'unknown'),
      'Company location: ' + ($json['Company Location'] || 'unknown'),
      'Lead location: ' + ($json['Location'] || 'unknown'),
      'Sales team size: ' + ($json['Sales Team Size'] || 'unknown'),
      'Company description: ' + String($json['Company Description'] || '').slice(0, 600)
    ].join('\\n')""", "$('Your settings').first().json.icp")

OVERVIEW = """## Weekly lead list: Sales Navigator to Google Sheets, scored by AI

**Who it's for:** anyone who prospects in LinkedIn Sales Navigator and wants a fresh, ranked lead list every week without code.

**What it does:** every Monday, Evaboot exports your saved Sales Navigator search and finds verified emails. The workflow keeps the leads that really match your filters and have a safe email, scores each one against your ideal customer profile with the OpenAI Decisions API, and adds them to a Google Sheet with an ICP score from 0 to 100. A lead that is already in the sheet is updated, never duplicated.

### How to set up
1. Install the Evaboot node (Settings > Community nodes, `@evaboot-team/n8n-nodes-evaboot`).
2. Add credentials: **Evaboot** (API key from dash.evaboot.com > API key), **OpenAI**, **Google Sheets**.
3. Make a Google Sheet with a header row: LinkedIn URL, First name, Last name, Job title, Company, Company domain, Industry, Employees, Company location, Email, ICP score, ICP fit, Confidence, Added on.
4. Fill in **Your settings**: your Sales Navigator search URL, your ICP, and the sheet URL copied from the browser while the right tab is open (it ends with `gid=…`).
5. Click **Execute workflow** to test, then activate it.

### Good to know
Evaboot exports the whole search and charges one credit per lead, so keep the search focused. A 100-lead export takes about 5 minutes.

The same workflow for Make and as a Python script: github.com/evaboot-labs"""

nodes = [
    sticky("Template overview", [-820, -340], 540, 900, OVERVIEW),
    sticky("Step 1", [-240, -160], 700, 440,
           "### 1. Settings\nEvery Monday, or by hand with **Test run**. Put your Sales Navigator search, your ICP and your Google Sheet in **Your settings**."),
    sticky("Step 2", [500, -160], 900, 440,
           "### 2. Export with Evaboot\nEvaboot exports the search and finds verified emails. The workflow checks every 2 minutes until the export is done."),
    sticky("Step 3", [1440, -160], 1160, 440,
           "### 3. Filter, score and save\nKeeps leads that match your filters and have a **safe** email. The OpenAI Decisions API scores each one against your ICP, then the lead is added to the sheet, or updated if its LinkedIn URL is already there."),
    node("Every Monday at 8am", "n8n-nodes-base.scheduleTrigger", 1.2, [-200, -20],
         {"rule": {"interval": [{"field": "weeks", "triggerAtDay": [1], "triggerAtHour": 8}]}}),
    node("Test run", "n8n-nodes-base.manualTrigger", 1, [-200, 160], {}),
    node("Your settings", "n8n-nodes-base.set", 3.4, [40, 60], {
        "mode": "manual", "options": {},
        "assignments": {"assignments": [
            {"id": "url", "name": "salesNavigatorUrl", "type": "string",
             "value": "https://www.linkedin.com/sales/search/people?query=REPLACE_WITH_YOUR_SEARCH"},
            {"id": "icp", "name": "icp", "type": "string", "value": ICP},
            {"id": "sheet", "name": "sheetUrl", "type": "string",
             "value": "https://docs.google.com/spreadsheets/d/REPLACE_WITH_YOUR_SHEET_ID/edit?gid=REPLACE_WITH_THE_TAB_ID"},
        ]}}, executeOnce=True),
    node("Export Sales Navigator search", EVABOOT, 1, [560, 60], {
        "resource": "extraction", "operation": "createUrl",
        "searchName": "={{ 'Weekly lead list ' + $now.toFormat('yyyy-LL-dd') }}",
        "linkedinUrl": "={{ $json.salesNavigatorUrl }}"}, credentials=EVABOOT_CRED),
    node("Wait 2 minutes", "n8n-nodes-base.wait", 1.1, [780, 60], {"unit": "minutes", "amount": 2}),
    node("Check the export", EVABOOT, 1, [1000, 60], {
        "resource": "extraction", "operation": "get",
        "extractionId": "={{ $('Export Sales Navigator search').item.json.extraction_id }}"},
        credentials=EVABOOT_CRED),
    node("Export finished?", "n8n-nodes-base.if", 2.2, [1220, 60], {
        "options": {}, "conditions": {"options": {"version": 2, "caseSensitive": True, "typeValidation": "loose"},
        "combinator": "and", "conditions": [condition("={{ ['EXECUTED','FAILED','PAUSED'].includes($json.status) }}",
                                                      {"type": "boolean", "operation": "true", "singleValue": True})]}}),
    node("One item per lead", "n8n-nodes-base.splitOut", 1, [1480, 40], {"fieldToSplitOut": "prospects", "options": {}}),
    node("Keep matching leads with a safe email", "n8n-nodes-base.filter", 2.2, [1700, 40], {
        "options": {}, "conditions": {"options": {"version": 2, "caseSensitive": False, "typeValidation": "loose"},
        "combinator": "and", "conditions": [
            condition("={{ $json['Matches Filters'] }}", {"type": "string", "operation": "equals"}, "YES"),
            condition("={{ $json['Email Status'] }}", {"type": "string", "operation": "equals"}, "safe")]}}),
    node("Score against ICP", "n8n-nodes-base.httpRequest", 4.2, [1920, 40], {
        "method": "POST", "url": "https://api.openai.com/v1/decisions",
        "authentication": "predefinedCredentialType", "nodeCredentialType": "openAiApi",
        "sendBody": True, "specifyBody": "json", "jsonBody": DECISION_BODY, "options": {}},
        credentials=OPENAI_CRED),
    node("Build the sheet row", "n8n-nodes-base.code", 2, [2140, 40], {"mode": "runOnceForEachItem", "jsCode": BUILD_ROW}),
    node("Add or update in Google Sheets", "n8n-nodes-base.googleSheets", 4.5, [2360, 40], {
        "operation": "appendOrUpdate",
        "documentId": {"__rl": True, "mode": "url", "value": "={{ $('Your settings').first().json.sheetUrl }}"},
        "sheetName": {"__rl": True, "mode": "url", "value": "={{ $('Your settings').first().json.sheetUrl }}"},
        "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": ["LinkedIn URL"], "schema": []},
        "options": {}}, credentials=SHEETS_CRED),
]

conn = lambda *targets: {"main": [[{"node": t, "type": "main", "index": 0}] for t in targets]}
connections = {
    "Every Monday at 8am": conn("Your settings"),
    "Test run": conn("Your settings"),
    "Your settings": conn("Export Sales Navigator search"),
    "Export Sales Navigator search": conn("Wait 2 minutes"),
    "Wait 2 minutes": conn("Check the export"),
    "Check the export": conn("Export finished?"),
    "Export finished?": {"main": [[{"node": "One item per lead", "type": "main", "index": 0}],
                                  [{"node": "Wait 2 minutes", "type": "main", "index": 0}]]},
    "One item per lead": conn("Keep matching leads with a safe email"),
    "Keep matching leads with a safe email": conn("Score against ICP"),
    "Score against ICP": conn("Build the sheet row"),
    "Build the sheet row": conn("Add or update in Google Sheets"),
}

workflow = {"name": "Weekly lead list: Sales Navigator to Google Sheets, scored by AI",
            "nodes": nodes, "connections": connections, "settings": {"executionOrder": "v1"}}
out = HERE / "sales-navigator-to-google-sheets-scored.json"
out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
print(f"Wrote {out} ({len(nodes)} nodes)")
jev_out = HERE / "sales-navigator-to-google-sheets-scored-jev.json"
jev_out.write_text(json.dumps(to_jev(workflow, "Score against ICP", "Build the sheet row"), indent=2, ensure_ascii=False) + "\n")
print(f"Wrote {jev_out}")
