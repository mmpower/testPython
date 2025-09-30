Step-by-step conversational prompts

Step 1 – Context setup

I will provide you with the codebase of a GitHub repository in chunks. Your job is to help me analyze it. First, I want you to carefully read the files I provide, but do not summarize yet. Simply confirm when you’ve received and processed each file.

Step 2 – Identify frameworks & structure

Based on the files I’ve sent so far, identify which framework(s) or libraries are being used for web services or API definition (e.g., Flask, Express, FastAPI, Spring). Tell me how this repo is likely exposing endpoints.

Step 3 – Extract produced APIs

Now, look at the code again and extract all API endpoints that this repo exposes. For each endpoint, give me:

HTTP method (GET/POST/etc.)

Path/route

Input parameters (query/body)

Output/response structure

Source file and function where it is defined

Step 4 – Extract consumed APIs

Next, identify any external APIs or services that this codebase calls. Look for:

External HTTP calls (e.g., axios, requests, fetch)

SDKs or API clients (e.g., Stripe, Twilio, Google APIs)

Hardcoded URLs or API keys
For each, explain the purpose and where it’s used in the repo.

Step 5 – Consolidate into structured summary

Please organize your findings into the following YAML format:

produced_apis:
  - name: <API name/route>
    type: <REST/GraphQL/etc.>
    method: <GET/POST/etc.>
    path: </api/...>
    request: <brief description>
    response: <brief description>
    source_files: [file1, file2]

consumed_apis:
  - name: <API or service>
    type: <REST/SDK/other>
    purpose: <brief description>
    where_used: [file1, file2]



# one-shot prompt

Single-shot Prompt

You are given the full contents of a GitHub repository.
Your task is to analyze the repository to determine what APIs it produces and what APIs it consumes.

Perform the following steps:

Produced APIs (Exposed by this repo)

List all API endpoints, their type (REST, GraphQL, gRPC, WebSocket, etc.), and their HTTP methods (GET/POST/etc.).

For each endpoint, describe:

Path or route

Input parameters (query/body)

Response structure (success/error)

Authentication/authorization if applicable

Cite the source files and functions where each endpoint is defined.

Consumed APIs (External dependencies)

Identify all external APIs or services that this codebase calls.

Look for:

Outbound HTTP requests (axios, requests, fetch, etc.)

SDKs or official clients (e.g., Stripe, Twilio, Google Maps)

Hardcoded URLs or API endpoints

For each, explain its purpose (e.g., “Stripe API for payments,” “Google Maps API for geocoding”).

Cite the relevant source files where they are invoked.

Supporting Evidence

For both produced and consumed APIs, provide code snippets or references to confirm your findings.

Structured Summary

Present results in the following YAML format:

produced_apis:
  - name: <API name or function>
    type: <REST/GraphQL/etc.>
    method: <GET/POST/etc.>
    path: </api/...>
    request: <brief description of inputs>
    response: <brief description of outputs>
    auth: <yes/no/description>
    source_files: [file1, file2]

consumed_apis:
  - name: <External API or service>
    type: <REST/SDK/other>
    purpose: <brief description>
    where_used: [file1, file2]
    evidence: <code snippet or reference>


Be as detailed and precise as possible. If an API is partially implemented or only referenced, note that explicitly.


