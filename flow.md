🔹 End-to-End Multi-Language API Analysis Pipeline
# Step 1 — Extract APIs

Run the upgraded Python script we just built:

python multi_lang_api_extractor.py


This produces a single api_summary.yaml containing:

produced_apis (exposed endpoints)

consumed_apis (external calls)

constants (resolved constants and environment variables)

#  Step 2 — Pre-process for LLM (Optional)

If the repo is extremely large, you can split the YAML into chunks:

import yaml
import json

with open("api_summary.yaml") as f:
    data = yaml.safe_load(f)

chunk_size = 50  # APIs per chunk
chunks = [data['produced_apis'][i:i+chunk_size] for i in range(0,len(data['produced_apis']),chunk_size)]

for idx, chunk in enumerate(chunks):
    with open(f"produced_chunk_{idx}.json", "w") as f:
        json.dump(chunk, f, indent=2)


This allows you to feed manageable pieces into the LLM.

Do the same for consumed_apis if needed.

# Step 3 — LLM Prompt Design

Use a structured, clear prompt to guide the LLM:

You are analyzing a codebase with multiple languages (Python, JS/TS, Java, Go).

I have provided a list of candidate APIs:
- produced_apis: endpoints defined in the repo
- consumed_apis: external APIs called by the repo
- constants: resolved constants and environment variables

Please generate a structured summary in YAML format with:

produced_apis:
  - name: <endpoint name/function>
    type: <REST/GraphQL/gRPC/etc.>
    method: <GET/POST/etc.>
    path: <resolved path>
    request: <brief description if evident>
    response: <brief description if evident>
    auth: <yes/no/description>
    source_files: [file1, file2]

consumed_apis:
  - name: <external API/service>
    type: <REST/SDK/other>
    purpose: <brief description if evident>
    where_used: [file1, file2]
    evidence: <code snippet or reference>


Feed either the whole YAML or chunks into the LLM with this prompt.

Ask the LLM to merge duplicates, fill in missing info, and explain relationships between produced and consumed APIs.

# Step 4 — Iterative Refinement

If the LLM reports unresolved paths or missing request/response info:

Feed nearby code snippets (function bodies, request handlers, serializers) for context.

Ask the LLM to infer request/response schemas from the code.

Repeat until the summary is complete.

# Step 5 — Final Output

You now have a single structured YAML summarizing:

All endpoints exposed by the repo (produced APIs)

All external APIs called (consumed APIs)

Resolved paths/URLs and references to constants

Optional inferred request/response details

This can be directly used for:

Documentation

Security reviews

Dependency audits

Automated API testing
