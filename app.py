import os
import glob
import argparse
import re
import csv
import json
from groq import Groq

# ==========================
# CSV Header Definitions
# ==========================
API_HEADERS = [
    "Test Case ID", "Test Case Description", "Preconditions",
    "Endpoint", "Method", "Request Body", "Expected Response", "Remarks"
]

UI_HEADERS = [
    "Test Case ID", "Test Case Description", "Preconditions",
    "Steps", "Expected Result", "Remarks"
]

FUNC_HEADERS = [
    "Test Case ID", "Test Case Description", "Preconditions",
    "Test Steps", "Expected Outcome", "Remarks"
]

# ==========================
# Prepocess Swagger / Docs
# ==========================
def preprocess_swagger(raw_json_str):
    """Flatten $ref definitions in Swagger to make them readable by LLMs."""
    try:
        data = json.loads(raw_json_str)
        defs = data.get("definitions", {})
        textified_defs = []

        for name, definition in defs.items():
            schema_desc = json.dumps(definition, indent=2)
            textified_defs.append(f"### Definition: {name}\n{schema_desc}\n")

        paths = data.get("paths", {})
        path_texts = []
        for path, methods in paths.items():
            path_texts.append(f"\nEndpoint: {path}")
            for method, meta in methods.items():
                desc = meta.get("summary", "")
                params = json.dumps(meta.get("parameters", []), indent=2)
                responses = json.dumps(meta.get("responses", {}), indent=2)
                path_texts.append(f"Method: {method.upper()}\nSummary: {desc}\nParams: {params}\nResponses: {responses}\n")

        full_text = "\n".join(textified_defs + path_texts)
        return full_text
    except Exception as e:
        print(f"⚠️ Swagger preprocessing failed: {e}")
        return raw_json_str


# ==========================
# Load Documents
# ==========================
def load_documents(folder, mode):
    """Load documents selectively depending on mode."""
    text_data = []
    for path in glob.glob(os.path.join(folder, "*")):
        fname = os.path.basename(path).lower()
        ext = os.path.splitext(path)[1].lower()

        # ✅ For API mode → only Swagger files
        if mode == "api" and "swagger" in fname and ext in [".json", ".yaml", ".yml"]:
            with open(path, "r", encoding="utf-8") as f:
                raw_swagger = f.read()
                processed_swagger = preprocess_swagger(raw_swagger)
                text_data.append(f"\n# Swagger: {fname}\n{processed_swagger}\n")


        # ✅ For UI mode → everything except Swagger
        elif mode == "ui" and not ("swagger" in fname or ext in [".json", ".yaml", ".yml"]):
            with open(path, "r", encoding="utf-8") as f:
                text_data.append(f"\n# UI Doc: {fname}\n{f.read()}\n")

        # ✅ For Functional mode → text-based documents
        elif mode == "functional" and ext in [".txt", ".md", ".docx"]:
            with open(path, "r", encoding="utf-8") as f:
                text_data.append(f"\n# Functional Doc: {fname}\n{f.read()}\n")

    combined = "\n".join(text_data)
    print(f"📄 Loaded {len(text_data)} document(s) → {len(combined)} characters of context.")
    return combined


# ==========================
# CSV Cleaner & Writer
# ==========================
def clean_and_save_csv(text, headers, output_path):
    """Parse JSON or CSV-like model output and write clean CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Try parsing JSON if the model responded in structured format
    if "[" in text and "]" in text and "{" in text:
        try:
            json_data = json.loads(re.search(r"\[.*\]", text, re.DOTALL).group(0))
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for row in json_data:
                    writer.writerow({h: row.get(h, "") for h in headers})
            print(f"✅ Parsed JSON and saved → {output_path}")
            return
        except Exception as e:
            print(f"⚠️ JSON parse failed: {e}, falling back to CSV text...")

    # Fall back to raw CSV extraction
    csv_pattern = r"(Test Case ID,.*)"
    match = re.search(csv_pattern, text, re.DOTALL)
    csv_content = match.group(1) if match else text

    csv_content = re.sub(r"```(csv|CSV)?", "", csv_content)
    csv_content = re.sub(r"Here.*?CSV format:?","", csv_content, flags=re.IGNORECASE)
    csv_content = csv_content.strip()

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    print(f"✅ Saved fallback CSV → {output_path}")


# ==========================
# Test Case Generation
# ==========================
def generate_testcases(context, query, headers, mode, model="llama-3.1-8b-instant"):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Mode-specific prompt tuning
    if mode == "api":
        instructions = f"""
Generate API test cases strictly and only using endpoints and schemas found in the Swagger definition.
Include:
- Positive, negative, boundary and validation tests.
- Do NOT invent endpoints not listed in Swagger.
Return output as JSON array with fields: {', '.join(headers)}.
"""
    elif mode == "ui":
        instructions = f"""
Generate comprehensive UI test cases based on the provided documentation.
Cover:
- Field validations (e.g. password rules, required fields)
- Button enable/disable states
- Navigation and UI element visibility
Return output as JSON array with fields: {', '.join(headers)}.
"""
    else:
        instructions = f"""
Generate functional test cases that combine multiple UI and API interactions end-to-end.
Include preconditions, steps and expected outcomes.
Return output as JSON array with fields: {', '.join(headers)}.
"""

    prompt = f"""
You are a senior QA automation engineer.
{instructions}

Context:
{context[:15000]}
"""

    print("⚙️ Generating test cases using Groq...")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


# ==========================
# Main Entrypoint
# ==========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate test cases via Groq API")
    parser.add_argument("--query", type=str, required=True, help="Instruction for test generation")
    parser.add_argument("--docs", default="requirements_docs", help="Path to documents folder")
    parser.add_argument("--type", choices=["api", "ui", "functional"], required=True,
                        help="Choose test generation type: api / ui / functional")
    args = parser.parse_args()

    mode = args.type
    headers = {"api": API_HEADERS, "ui": UI_HEADERS, "functional": FUNC_HEADERS}[mode]

    print(f"🧩 Mode selected: {mode.upper()}")
    print(f"📂 Reading from folder: {args.docs}")

    context = load_documents(args.docs, mode)
    result = generate_testcases(context, args.query, headers, mode)

    output_path = f"outputs/{mode}_testcases.csv"
    clean_and_save_csv(result, headers, output_path)

    print(f"\n✅ All done! Final file saved at: {output_path}\n")
