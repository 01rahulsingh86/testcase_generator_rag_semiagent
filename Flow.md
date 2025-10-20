flowchart TD
    Start([Start: Run app.py]) --> Input["⚙️ Input Arguments<br/>--query<br/>--type api/ui/functional"]
    
    Input --> LoadDocs["📁 Load Documents<br/>from requirements_docs/"]
    
    LoadDocs --> FilterCheck{Select Mode}
    
    FilterCheck -->|API Mode| LoadAPI["Load Swagger/OpenAPI<br/>Files Only<br/>✓ .json, .yaml"]
    FilterCheck -->|UI Mode| LoadUI["Load Non-Swagger Docs<br/>✓ .txt, .md, .docx<br/>✗ Swagger files"]
    FilterCheck -->|Functional Mode| LoadAll["Load All Document Types<br/>✓ .json, .yaml, .txt,<br/>.md, .docx"]
    
    LoadAPI --> PrepDocs["🔄 Prepare Document Content<br/>Extract text & structure"]
    LoadUI --> PrepDocs
    LoadAll --> PrepDocs
    
    PrepDocs --> BuildPrompt["🎯 Build LLM Prompt<br/>Query + Document Context<br/>+ Mode-Specific Instructions"]
    
    BuildPrompt --> CallGroq["🧠 Call Groq API<br/>Model: llama-3.1-8b-instant<br/>Send Prompt & Docs"]
    
    CallGroq --> GroqResponse["📨 Receive LLM Response<br/>Structured JSON<br/>or CSV format"]
    
    GroqResponse --> ParseJSON{Response<br/>Format Check}
    
    ParseJSON -->|Valid JSON| ExtractJSON["✓ Extract Test Cases<br/>from JSON Object"]
    ParseJSON -->|CSV Format| ParseCSV["✓ Parse CSV<br/>Structure"]
    ParseJSON -->|Invalid/Mixed| Cleanup["⚠️ Clean & Extract<br/>Fallback Processing"]
    
    ExtractJSON --> ValidateData["✅ Validate Test Data<br/>Check columns<br/>Verify structure"]
    ParseCSV --> ValidateData
    Cleanup --> ValidateData
    
    ValidateData --> QuotePayloads["🔐 Quote JSON Payloads<br/>Escape commas<br/>Format properly"]
    
    QuotePayloads --> BuildCSV["📊 Build CSV Rows<br/>using DictWriter<br/>Proper escaping"]
    
    BuildCSV --> WriteFile["💾 Write CSV File<br/>to outputs/ folder"]
    
    WriteFile --> GenOutput{Test Type?}
    
    GenOutput -->|api| OutAPI["outputs/<br/>api_testcases.csv"]
    GenOutput -->|ui| OutUI["outputs/<br/>ui_testcases.csv"]
    GenOutput -->|functional| OutFunct["outputs/<br/>functional_testcases.csv"]
    
    OutAPI --> Success["✅ SUCCESS<br/>Test Cases Generated"]
    OutUI --> Success
    OutFunct --> Success
    
    Success --> Review["👀 Review Output<br/>Verify test cases<br/>Check CSV format"]
    
    Review --> End(["🎉 Complete<br/>Ready for QA"])
    
    style Start fill:#90EE90
    style End fill:#87CEEB
    style CallGroq fill:#FFB6C1
    style Success fill:#98FB98
    style BuildCSV fill:#DDA0DD
    style WriteFile fill:#F0E68C