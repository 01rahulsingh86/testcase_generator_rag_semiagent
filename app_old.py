import os
import glob
import argparse
import re
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
# CSV Cleaner
# ==========================
def clean_csv_output(text):
    """Extract only CSV content from model response."""
    csv_pattern = r"(Test Case ID,.*)"
    match = re.search(csv_pattern, text, re.DOTALL)
    if not match:
        print("⚠️ No valid CSV section found, saving raw text.")
        return text.strip()

    csv_content = match.group(1)
    csv_content = re.sub(r"```(csv|CSV)?", "", csv_content)
    csv_content = re.sub(r"Here.*?CSV format:?","", csv_content, flags=re.IGNORECASE)
    return csv_content.strip()


# ==========================
# Document Loader
# ==========================
def load_documents(folder, mode):
    """Load and merge docs based on mode (API/UI)."""
    text_data = []
    for path in glob.glob(os.path.join(folder, "*")):
        fname = os.path.basename(path).lower()
        ext = os.path.splitext(path)[1].lower()

        if mode == "api":
            # API → only swagger files
            if ext in [".json", ".yaml", ".yml"] and "swagger" in fname:
                with open(path, "r", encoding="utf-8") as f:
                    text_data.append(f"\n# Swagger: {fname}\n{f.read()}\n")

        elif mode == "ui":
            # UI → everything except swagger
            if not ("swagger" in fname or ext in [".json", ".yaml", ".yml"]):
                with open(path, "r", encoding="utf-8") as f:
                    text_data.append(f"\n# Doc: {fname}\n{f.read()}\n")

        elif mode == "functional":
            # Functional → all textual docs
            if ext in [".txt", ".md", ".docx"]:
                with open(path, "r", encoding="utf-8") as f:
                    text_data.append(f"\n# Doc: {fname}\n{f.read()}\n")

    combined = "\n".join(text_data)
    print(f"📄 Loaded {len(text_data)} document(s) → {len(combined)} chars of context.")
    return combined


# ==========================
# Generate Test Cases
# ==========================
def generate_testcases(context, query, headers, model="llama-3.1-8b-instant"):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
You are a senior QA automation engineer.

Based on the context below, generate **only structured test cases** in CSV format.

For API:
- Use only endpoints and parameters found in the Swagger definition.
- Include positive, negative, boundary, and validation scenarios.
- Do not invent endpoints or payloads.

For UI:
- Cover field validation, button states, visibility, navigation, and behavioral scenarios.
- Include both positive and negative tests.
- Ignore API or endpoint-level details.

Output columns:
{', '.join(headers)}

Do not include markdown, commentary, or any explanation — only the CSV.

Context:
{context[:15000]}
"""

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    parser.add_argument("--docs", default="requirements_docs")
    parser.add_argument("--type", choices=["api", "ui", "functional"], required=True,
                        help="Choose test generation type: api / ui / functional")
    args = parser.parse_args()

    mode = args.type
    headers = {"api": API_HEADERS, "ui": UI_HEADERS, "functional": FUNC_HEADERS}[mode]

    print(f"🧩 Mode selected: {mode.upper()}")
    print(f"📂 Reading documents from: {args.docs}")

    context = load_documents(args.docs, mode)
    result = generate_testcases(context, args.query, headers)
    cleaned = clean_csv_output(result)

    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/{mode}_testcases.csv"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"✅ Test cases saved successfully → {output_path}")
