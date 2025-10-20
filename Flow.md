# Test Case Generator - Process Flow

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         START: Run app.py                                   │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INPUT ARGUMENTS PROCESSING                               │
│  • --query: Test case generation instructions                               │
│  • --type: api | ui | functional                                           │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              STEP 1: LOAD DOCUMENTS FROM requirements_docs/                 │
│  Scan folder for available documents and metadata                           │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │   API MODE   │  │   UI MODE    │  │ FUNCTIONAL   │
        │   Filter:    │  │   Filter:    │  │   MODE       │
        │ ✓ .json      │  │ ✗ .json      │  │   Filter:    │
        │ ✓ .yaml      │  │ ✗ .yaml      │  │ ✓ All files  │
        │ ✗ Others     │  │ ✓ .txt       │  │              │
        │              │  │ ✓ .md        │  │              │
        │              │  │ ✓ .docx      │  │              │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                 │                 │
               └─────────────────┬─────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: PREPARE DOCUMENT CONTENT                                           │
│  • Extract text from documents                                              │
│  • Parse structure (headers, sections, code blocks)                         │
│  • Validate file encoding (UTF-8)                                           │
│  • Create document context dictionary                                       │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: BUILD LLM PROMPT                                                   │
│  • Combine user query with loaded documents                                 │
│  • Add mode-specific instructions                                           │
│  • Include CSV column schema                                                │
│  • Attach example test case format                                          │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: CALL GROQ API                                                      │
│  • Initialize Groq client with API key                                      │
│  • Send message to llama-3.1-8b-instant                                     │
│  • Model processes documents and generates test cases                       │
│  • Receive structured response                                              │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: PARSE LLM RESPONSE                                                 │
│  Response type detection:                                                   │
└────────────────────────────────┬────────────────────────────────────────────┘
                     ┌───────────┼───────────┐
                     │           │           │
                     ▼           ▼           ▼
            ┌─────────────────┐ ┌─────────────────┐ ┌──────────────┐
            │  Valid JSON     │ │   CSV Format    │ │  Mixed/Error │
            │  Response       │ │   Response      │ │  Fallback    │
            │  • Extract      │ │  • Parse CSV    │ │  Processing  │
            │    test_cases[] │ │  • Split rows   │ │              │
            │  • Validate     │ │  • Extract cols │ │              │
            │    structure    │ │                 │ │              │
            └────────┬────────┘ └────────┬────────┘ └──────┬───────┘
                     │                  │                 │
                     └──────────────────┬─────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: VALIDATE TEST DATA                                                 │
│  • Verify required columns present                                          │
│  • Check data types and formats                                             │
│  • Validate endpoint URLs (API tests)                                       │
│  • Ensure non-empty test case IDs                                           │
│  • Handle missing or malformed data                                         │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: QUOTE & ESCAPE JSON PAYLOADS                                       │
│  • Identify JSON fields in request/response bodies                          │
│  • Escape special characters (quotes, commas, newlines)                     │
│  • Wrap complex payloads in double quotes                                   │
│  • Ensure CSV compatibility without column breaks                           │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: BUILD CSV STRUCTURE                                                │
│  • Use Python csv.DictWriter for proper formatting                          │
│  • Define column order (standard QA test case format)                       │
│  • Create row dictionaries from parsed test data                            │
│  • Apply quoting strategy (QUOTE_MINIMAL for efficiency)                    │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: WRITE OUTPUT FILE                                                  │
│  • Create outputs/ directory if needed                                      │
│  • Write CSV header row                                                     │
│  • Write all test case rows                                                 │
│  • Close file handle                                                        │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
                    ▼            ▼            ▼
        ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
        │  API Mode        │ │  UI Mode         │ │  Functional Mode │
        │  Output:         │ │  Output:         │ │  Output:         │
        │ api_testcases.   │ │ ui_testcases.    │ │ functional_test  │
        │ csv              │ │ csv              │ │ cases.csv        │
        └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
                 │                    │                    │
                 └────────────────────┬────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ✅ SUCCESS: TEST CASES GENERATED                         │
│  • CSV file created and validated                                           │
│  • File size and row count logged                                           │
│  • Output path displayed to user                                            │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   USER REVIEW & QUALITY ASSURANCE                           │
│  • Open generated CSV in Excel or text editor                               │
│  • Verify test case content against requirements                            │
│  • Check for formatting issues or incomplete data                           │
│  • Adjust manually if needed                                                │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              🎉 READY FOR QA DEPLOYMENT                                     │
│  • Import to test management system (TestRail, Zephyr, Azure)               │
│  • Feed to test automation framework                                        │
│  • Distribute to QA team for manual execution                               │
│  • Archive with requirement documentation                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Process Breakdown

### Phase 1: Input & Configuration
**What Happens:**
- User executes `python app.py --query "..." --type api/ui/functional`
- Application parses command-line arguments
- Validates API key availability in environment

**Key Functions:**
```
parse_arguments() → config dict
validate_groq_api_key() → bool
```

---

### Phase 2: Document Selection & Loading
**What Happens:**
- Scans `requirements_docs/` directory
- Filters files based on selected mode:
  - **API**: Only `.json`, `.yaml` (Swagger/OpenAPI)
  - **UI**: Only `.txt`, `.md`, `.docx` (excludes Swagger)
  - **Functional**: All file types

**Key Functions:**
```
load_documents(mode) → dict
filter_files_by_mode(files, mode) → filtered_files
extract_text_from_file(filepath) → text
```

---

### Phase 3: Content Preparation
**What Happens:**
- Extracts readable text from various file formats
- Handles encoding issues gracefully
- Structures content with file metadata (filename, type)
- Limits context to avoid token overflow

**Key Functions:**
```
read_swagger_file(path) → dict
read_text_document(path) → str
read_docx_file(path) → str
prepare_context(docs) → formatted_context
```

---

### Phase 4: Prompt Engineering
**What Happens:**
- Combines user query with document context
- Adds mode-specific instructions
- Includes CSV schema and examples
- Structures prompt for optimal LLM output

**Example Prompt Structure:**
```
You are a QA test case expert. Generate [API/UI/Functional] test cases.

Documents:
[Document 1]
[Document 2]

Requirements:
- Generate [test type] test cases
- Output as JSON with this schema: {...}
- Include positive, negative, edge cases
- Each test case must have: ID, Description, Steps, Expected Result

User Query: {user_query}

Response (JSON only, no markdown):
```

---

### Phase 5: LLM Processing
**What Happens:**
- Sends complete prompt to Groq API
- Uses `llama-3.1-8b-instant` model (fast, cost-effective)
- Model analyzes documents and generates test cases
- Receives structured response

**API Call:**
```python
client.messages.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=4096
)
```

---

### Phase 6: Response Parsing
**What Happens:**
- Detects response format (JSON, CSV, or mixed)
- Extracts test case data
- Handles malformed responses with fallback logic

**Decision Tree:**
```
Response Format?
├─ Valid JSON
│  └─ Extract from test_cases array
├─ CSV Format
│  └─ Parse row by row
└─ Mixed/Invalid
   └─ Extract structured lines + fallback
```

---

### Phase 7: Data Validation
**What Happens:**
- Verifies all required columns present
- Checks data integrity
- Validates syntax for endpoint URLs (API tests)
- Logs warnings for incomplete data

**Validation Rules:**
- API Tests: Must have Endpoint, Method, Request Body, Expected Response
- UI Tests: Must have Steps, Expected Result
- Functional Tests: Combined API + UI requirements

---

### Phase 8: JSON Payload Escaping
**What Happens:**
- Identifies JSON payloads in test data
- Escapes special characters
- Wraps complex structures in quotes
- Ensures CSV compatibility

**Example:**
```
Input:  {"email":"user@test.com","password":"Pass@123"}
Output: "{""email"":""user@test.com"",""password"":""Pass@123""}"
```

---

### Phase 9: CSV Generation
**What Happens:**
- Uses `csv.DictWriter` for proper formatting
- Writes header row
- Writes all test case data rows
- Applies consistent quoting strategy

**Output Columns (API):**
```
Test Case ID | Description | Preconditions | Endpoint | Method | 
Request Body | Expected Response | Remarks
```

**Output Columns (UI):**
```
Test Case ID | Description | Preconditions | Steps | 
Expected Result | Remarks
```

---

### Phase 10: File Output
**What Happens:**
- Creates `outputs/` directory if needed
- Writes CSV file with appropriate name
- Validates file write success
- Logs completion message

**Output Files:**
- `outputs/api_testcases.csv` (API mode)
- `outputs/ui_testcases.csv` (UI mode)
- `outputs/functional_testcases.csv` (Functional mode)

---

### Phase 11: Post-Generation Review
**What Happens:**
- User opens generated CSV
- Reviews test case quality
- Verifies against original requirements
- Makes manual adjustments if needed

**QA Checks:**
- [ ] All required columns populated
- [ ] Test case IDs are unique
- [ ] Descriptions are clear and concise
- [ ] Steps are detailed and actionable
- [ ] Expected results are specific
- [ ] JSON payloads properly formatted
- [ ] No duplicate test cases

---

## Error Handling Flow

```
┌──────────────────────┐
│ Operation Fails      │
└──────┬───────────────┘
       │
       ▼
   Is error
   recoverable?
   /         \
  /           \
 YES          NO
 │            │
 ▼            ▼
Apply     Log Error +
Fallback  Exit with
Logic     Status Code
 │            │
 └───┬────────┘
     │
     ▼
Continue or
Fail Gracefully
```

---

## Performance Considerations

| Stage | Bottleneck | Mitigation |
|-------|-----------|-----------|
| Document Loading | Large files (>10MB) | Stream reading, size validation |
| LLM Processing | API latency | 30-60s typical, timeout handling |
| CSV Generation | Large datasets (>10K rows) | Batch writing, memory optimization |
| File I/O | Disk speed | Local SSD recommended |

---

## Integration Points

### Pre-Generation
- **CI/CD Trigger**: Git webhook on spec updates
- **Document Upload**: REST API to add new requirements

### Post-Generation
- **TestRail Import**: API integration via `python-testrail`
- **Jira Integration**: Create test issues from CSV
- **Excel Export**: Combine CSVs into multi-sheet workbook
- **Git Commit**: Auto-commit test cases to version control

---

## Success Criteria

✅ **Green Flags:**
- CSV file created without errors
- All expected columns present
- Test case IDs are sequential/valid
- JSON payloads properly escaped
- File size > 1KB (contains data)

⚠️ **Yellow Flags:**
- Warnings during parsing (recovered gracefully)
- Some columns with sparse data
- Model response required fallback processing

❌ **Red Flags:**
- Empty CSV file generated
- Missing required columns
- Malformed JSON payloads in output
- File write failure