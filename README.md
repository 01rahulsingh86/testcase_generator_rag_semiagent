# Test Case Generator (Groq-Powered)

Automatically generate API, UI, and functional test cases from your requirement documents, Swagger specifications, and UI flow definitions. Powered by Groq's LLM API for intelligent test case creation.

## Overview

This tool streamlines QA workflows by using advanced language models to analyze technical documentation and automatically generate structured, production-ready test cases. Extract test cases directly from your existing documentation and export them in CSV format—ready for manual testing, automation frameworks, or quality management platforms.


### Supported Test Case Types

| Type | Description | Source Documents |
|------|-------------|------------------|
| **API Tests** | Endpoint validation, payload testing, response verification, error handling | Swagger/OpenAPI (.json, .yaml) ONLY 1 SWAGGER AT A TIME RIGHT NOW(WIP) |
| **UI Tests** | Form validation, button states, navigation flows, user interactions | Requirements (.txt, .md, .docx) |
| **Functional/E2E Tests** | Complete user journeys combining UI and API flows | All text-based documents |

## Key Features

- **Intelligent Document Processing**: Automatically loads and processes Swagger definitions, requirements documents, and UI specifications
- **Clean CSV Export**: Excel-compatible output with proper escaping and formatting
- **Separated Logic**: Distinct handling of API, UI, and functional test scenarios
- **Groq Integration**: Leverages `llama-3.1-8b-instant` for fast, accurate test generation
- **Error Handling**: Graceful fallback processing for various document formats and LLM responses

## Project Structure

```
testcase_rag_minimal/
├── app.py                      # Main test case generator
├── ingest_docs.py              # Document processing module (optional)
├── requirements_docs/          # Input directory for source documents
│   ├── swagger_example.json
│   ├── requirement_doc_sample.txt
│   ├── ui_flows.md
│   └── (additional .txt/.md/.docx files)
├── outputs/                    # Generated test case CSVs
│   ├── api_testcases.csv
│   ├── ui_testcases.csv
│   └── functional_testcases.csv
├── requirements.txt
└── README.md
```

## Installation

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv rag_env
source rag_env/bin/activate  # On Windows: rag_env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install groq openpyxl
```

*Note: `openpyxl` is optional but recommended for Excel export functionality.*

### 3. Configure Groq API Key

```bash
export GROQ_API_KEY=your_groq_api_key_here
```

On Windows, use:
```bash
set GROQ_API_KEY=your_groq_api_key_here
```

Obtain your API key from [Groq Console](https://console.groq.com).

## Quick Start

### Prepare Your Documents

Place your source documents in the `requirements_docs/` folder:

| Document Type | Purpose | Format |
|---------------|---------|--------|
| Swagger/OpenAPI | API specification | `.json`, `.yaml` |
| Requirements | Feature and functional specifications | `.txt`, `.md` |
| UI Flows | User interface interactions and workflows | `.txt`, `.md`, `.docx` |

### Generate API Test Cases

```bash
python app.py \
  --query "Generate positive, negative, and validation API test cases strictly using endpoints from petstore-swagger.json." \
  --type api
```

Output: `outputs/api_testcases.csv`

### Generate UI Test Cases

```bash
python app.py \
  --query "Generate comprehensive UI test cases from requirement_doc_sample.txt and ui_flows.md. Include field validation, button states, and navigation scenarios." \
  --type ui
```

Output: `outputs/ui_testcases.csv`

### Generate Functional/E2E Test Cases

```bash
python app.py \
  --query "Generate functional test cases combining login, checkout, and payment flow." \
  --type functional
```

Output: `outputs/functional_testcases.csv`

## Output Format

### API Test Cases

| Test Case ID | Test Case Description | Preconditions | Endpoint | Method | Request Body | Expected Response | Remarks |
|---|---|---|---|---|---|---|---|
| API001 | Login with valid credentials | User registered with valid credentials | /login | POST | `{"email":"user@example.com","password":"Password@123"}` | 200 OK | Login successful |
| API002 | Login with invalid password | User registered | /login | POST | `{"email":"user@example.com","password":"wrongpass"}` | 401 Unauthorized | Error message displayed |

### UI Test Cases

| Test Case ID | Test Case Description | Preconditions | Steps | Expected Result | Remarks |
|---|---|---|---|---|---|
| UI001 | Verify login button disabled when fields empty | User on login page | 1. Leave email & password empty<br>2. Observe button state | Login button remains disabled | Validation working correctly |
| UI002 | Password visibility toggle functions | User on login page | 1. Click eye icon<br>2. Observe password field | Password text toggles visibility | UI interaction working correctly |

## How It Works

### Processing Modes

| Mode | Behavior |
|------|----------|
| `api` | Loads only Swagger/OpenAPI files (.json, .yaml) |
| `ui` | Loads non-Swagger documents (.txt, .md, .docx) |
| `functional` | Loads all document types together for end-to-end scenarios |

### Pipeline

1. **Document Ingestion**: Scans `requirements_docs/` and filters by file type based on selected mode
2. **LLM Processing**: Sends documents and query to Groq's `llama-3.1-8b-instant` model
3. **Parsing**: Extracts structured JSON from LLM response
4. **CSV Generation**: Formats output with proper escaping and quotes using Python's `csv.DictWriter`
5. **Export**: Saves clean CSV files to `outputs/` directory

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| No test cases generated | Documents not found in `requirements_docs/` | Verify filenames and folder location; check file extensions (.json, .yaml, .txt, .md, .docx) |
| CSV columns misaligned | JSON payloads contain commas | Tool automatically handles escaping; if issue persists, check LLM output format |
| "No valid CSV section found" | LLM response format unexpected | Tool falls back to structured parsing; review query clarity and document content |
| API key not recognized | Environment variable not set | Ensure `GROQ_API_KEY` is exported before running script |
| Blank output files | File encoding or format issues | Try converting documents to UTF-8; ensure text files use standard formatting |

## Extending the Tool

### Export to Excel Multi-Sheet Format

Combine all three CSV outputs into a single Excel workbook with separate tabs:

```python
from openpyxl import Workbook

def combine_csvs_to_excel():
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet
    
    for csv_file, sheet_name in [
        ('outputs/api_testcases.csv', 'API Tests'),
        ('outputs/ui_testcases.csv', 'UI Tests'),
        ('outputs/functional_testcases.csv', 'Functional Tests')
    ]:
        ws = wb.create_sheet(sheet_name)
        with open(csv_file) as f:
            for row in csv.reader(f):
                ws.append(row)
    
    wb.save('TestCases.xlsx')
    print("✅ Combined TestCases.xlsx created successfully")

combine_csvs_to_excel()
```

### Integration Opportunities

- **CI/CD Pipeline**: Generate tests automatically from spec updates
- **Test Management Integration**: Direct API import to TestRail, Zephyr, or Azure Test Plans
- **Excel Enhancement**: Add conditional formatting, data validation, and pivot tables
- **Custom Formatting**: Modify output templates for organization-specific requirements

## Example Workflow

```bash
# 1. Place your documents in requirements_docs/

# 2. Generate API test cases
python app.py --query "Generate API tests for login and checkout endpoints" --type api

# 3. Generate UI test cases
python app.py --query "Generate UI tests for login and checkout flows" --type ui

# 4. Generate functional test cases
python app.py --query "Generate E2E tests for complete checkout workflow" --type functional

# 5. Review outputs
open outputs/api_testcases.csv
open outputs/ui_testcases.csv
open outputs/functional_testcases.csv

# 6. Import to your QA management tool or automation framework
```

## Best Practices

- **Clear Documentation**: Use precise, detailed requirement documents for better test case generation
- **Specification Format**: Ensure Swagger/OpenAPI files are valid and well-structured
- **Query Specificity**: Include test types (positive, negative, edge cases) in your queries
- **Output Verification**: Review generated test cases before production use; validate against original requirements
- **Version Control**: Track test case specifications alongside your source documentation

## License

MIT © 2025 — Built for QA Automation Teams

Use responsibly. Always verify generated test cases against original specifications before production deployment.

## Support & Feedback

For issues, feature requests, or contributions, please refer to the project repository or contact your QA automation team.