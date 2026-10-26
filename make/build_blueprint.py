"""Build the Make blueprint. Run: python3 make/build_blueprint.py
Writes make/evaboot-leads-to-google-sheets-scored.blueprint.json (the public template).
Also writes the Typesafe JEV copy (…-jev.blueprint.json).
With --test HOOK_ID CONNECTION_ID SPREADSHEET_ID SHEET_NAME KEY DATA_STRUCTURE_ID [jev] it prints a filled copy instead.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ICP = (HERE.parent / "ICP.md").read_text()

LEVELS = [
    ("No fit", "Fails a disqualifier, or matches none of the must-haves."),
    ("Weak fit", "Matches one must-have. The other must-haves fail or are unknown."),
    ("Partial fit", "Matches most must-haves, but one fails or is unknown."),
    ("Strong fit", "Matches every must-have and no disqualifier."),
]

LEAD_TEXT = "\n".join([
    "Job title: {{2.`Current Job`}}",
    "Company: {{2.`Company Name`}}",
    "Company industry: {{ifempty(2.`Company Industry`; \"unknown\")}}",
    "Company employees: {{ifempty(2.`Company Employee Exact Count`; \"unknown\")}}",
    "Company location: {{ifempty(2.`Company Location`; \"unknown\")}}",
    "Lead location: {{ifempty(2.Location; \"unknown\")}}",
    "Sales team size: {{ifempty(2.`Sales Team Size`; \"unknown\")}}",
    "Company description: {{substring(2.`Company Description`; 0; 600)}}",
])


def jev_request():
    """The same score question for Typesafe JEV, pinned to a release so the levels keep scoring the same."""
    return {"model": "jev-1.14.0", "state": {"ideal_customer_profile": ICP, "lead": LEAD_TEXT},
            "questions": {"icp_fit": {"type": "score",
                                      "instructions": "How well does `lead` match `ideal_customer_profile`?",
                                      "criteria": [f"{l}: {d}" for l, d in LEVELS]}}}


def blueprint(hook, connection, spreadsheet, sheet, openai_key, data_structure=None, jev=False):
    answer = "3.data.answers.icp_fit" if jev else "3.data.answers[1]"
    flow = [
        {"id": 1, "module": "gateway:CustomWebHook", "version": 1,
         "parameters": {"hook": hook, "maxResults": 1}, "mapper": {},
         "metadata": {"designer": {"x": 0, "y": 0, "name": "Evaboot export finished"}}},
        {"id": 2, "module": "builtin:BasicFeeder", "version": 1, "parameters": {},
         "mapper": {"array": "{{1.prospects}}"},
         "metadata": {"designer": {"x": 300, "y": 0, "name": "One bundle per lead"}}},
        {"id": 5, "module": "json:CreateJSON", "version": 1,
         "parameters": {"type": data_structure, "space": ""},
         "filter": {"name": "Matching leads with a safe email", "conditions": [[
             {"a": "{{2.`Matches Filters`}}", "b": "YES", "o": "text:equal:ci"},
             {"a": "{{2.`Email Status`}}", "b": "safe", "o": "text:equal:ci"}]]},
         "mapper": jev_request() if jev else {"model": "gpt-6-luna", "input": LEAD_TEXT, "questions": [{
             "type": "score", "name": "icp_fit",
             "instructions": "How well does this lead match the ideal customer profile below?\n\n" + ICP,
             "levels": [{"label": l, "description": d} for l, d in LEVELS]}]},
         "metadata": {"designer": {"x": 600, "y": 0, "name": "Build the JEV request" if jev else "Build the OpenAI request"}}},
        {"id": 3, "module": "http:ActionSendData", "version": 3,
         "parameters": {"handleErrors": False, "useNewZLibDeCompress": True},
         "mapper": {"url": "https://api.typesafe.ai/v1/systemone" if jev else "https://api.openai.com/v1/decisions", "serializeUrl": False, "method": "post",
                    "headers": [{"name": "Authorization", "value": "Bearer " + openai_key}],
                    "qs": [], "bodyType": "raw", "parseResponse": True, "authUser": "", "authPass": "",
                    "timeout": "", "shareCookies": False, "ca": "", "rejectUnauthorized": True,
                    "followRedirect": True, "useQuerystring": False, "gzip": True, "useMtls": False,
                    "contentType": "application/json", "data": "{{5.json}}", "followAllRedirects": False},
         "metadata": {"designer": {"x": 900, "y": 0, "name": "Score against ICP (Typesafe JEV)" if jev else "Score against ICP (OpenAI Decisions)"}}},
        {"id": 4, "module": "google-sheets:addRow", "version": 2,
         "parameters": {"__IMTCONN__": connection},
         "mapper": {"from": "drive", "mode": "select", "spreadsheetId": spreadsheet, "sheetId": sheet,
                    "includesHeaders": True, "insertDataOption": "INSERT_ROWS", "useColumnHeaders": False,
                    "valueInputOption": "USER_ENTERED", "insertUnformatted": False,
                    "values": {
                        "0": "{{2.`Linkedin URL Public`}}", "1": "{{2.`First Name`}}", "2": "{{2.`Last Name`}}",
                        "3": "{{2.`Current Job`}}", "4": "{{2.`Company Name`}}", "5": "{{2.`Company Domain`}}",
                        "6": "{{2.`Company Industry`}}", "7": "{{2.`Company Employee Exact Count`}}",
                        "8": "{{2.`Company Location`}}", "9": "{{2.Email}}",
                        "10": f"{{{{if({answer}.type = \"score\"; round({answer}.score / 3 * 100); \"\")}}}}",
                        "11": f"{{{{if({answer}.type = \"score\"; get(split(\"No fit,Weak fit,Partial fit,Strong fit\"; \",\"); round({answer}.score) + 1); \"Not scored\")}}}}",
                        "12": f"{{{{if({answer}.type = \"score\"; round({answer}.confidence * 100) / 100; \"\")}}}}",
                        "13": "{{formatDate(now; \"YYYY-MM-DD\")}}"}},
         "metadata": {"designer": {"x": 1200, "y": 0, "name": "Add to the lead sheet"}}},
    ]
    return {"name": "Weekly lead list: Evaboot to Google Sheets, scored by AI" + (" (JEV)" if jev else ""), "flow": flow,
            "metadata": {"instant": True, "version": 1,
                         "scenario": {"roundtrips": 1, "maxErrors": 3, "autoCommit": True, "sequential": False,
                                      "confidential": False, "dataloss": False, "dlq": False},
                         "designer": {"orphans": []}}}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        hook, conn, sheet_id, sheet_name, key, ds = sys.argv[2:8]
        print(json.dumps(blueprint(int(hook), int(conn), "/" + sheet_id, sheet_name, key, int(ds), jev=sys.argv[8:] == ["jev"])))
    else:
        out = HERE / "evaboot-leads-to-google-sheets-scored.blueprint.json"
        out.write_text(json.dumps(blueprint(None, None, "", "Sheet1", "YOUR_OPENAI_API_KEY"), indent=2) + "\n")
        print(f"Wrote {out}")
        jev_out = HERE / "evaboot-leads-to-google-sheets-scored-jev.blueprint.json"
        jev_out.write_text(json.dumps(blueprint(None, None, "", "Sheet1", "YOUR_JEV_API_KEY", jev=True), indent=2) + "\n")
        print(f"Wrote {jev_out}")
