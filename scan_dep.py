!pip install transformers torch pyyaml

import os
import yaml
import json
from multi_lang_api_extractor import scan_repo, produced, consumed, constants
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# -----------------------------
# CONFIG
# -----------------------------
SRC_DIR = "./src"
CHUNK_SIZE = 50
OUTPUT_YAML = "api_summary.yaml"
PROMPT_DIR = "llm_prompts"
LLM_OUTPUT_DIR = "llm_outputs"
MODEL_NAME = "TheBloke/LLaMA-2-7B-Chat-GPTQ"  # example local llama
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

os.makedirs(PROMPT_DIR, exist_ok=True)
os.makedirs(LLM_OUTPUT_DIR, exist_ok=True)

# -----------------------------
# STEP 1: Extract APIs
# -----------------------------
print("🔹 Scanning repo for produced and consumed APIs...")
scan_repo(SRC_DIR)
for api in produced:
    if isinstance(api.get("path"), str) and api["path"] in constants:
        api["path"] = constants[api["path"]]
for api in consumed:
    if isinstance(api.get("target"), str) and api["target"] in constants:
        api["target"] = constants[api["target"]]

result = {"produced_apis": produced, "consumed_apis": consumed, "constants": constants}
with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
    yaml.dump(result, f, sort_keys=False, allow_unicode=True)
print(f"✅ Full API summary written to {OUTPUT_YAML}")

# -----------------------------
# STEP 2: Split and generate prompts
# -----------------------------
def chunk_list(lst, size):
    return [lst[i:i+size] for i in range(0, len(lst), size)]

produced_chunks = chunk_list(produced, CHUNK_SIZE)
consumed_chunks = chunk_list(consumed, CHUNK_SIZE)

prompt_template = """You are analyzing a multi-language codebase (Python, JS/TS, Java, Go).
Here is a list of APIs extracted from the codebase:
{data_chunk}
Please generate a structured summary in YAML with:
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
"""

def save_prompt(chunk, idx, prefix):
    chunk_json = json.dumps(chunk, indent=2)
    prompt_text = prompt_template.format(data_chunk=chunk_json)
    file_path = os.path.join(PROMPT_DIR, f"{prefix}_chunk_{idx}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(prompt_text)
    return file_path

prompt_files = []
for i, chunk in enumerate(produced_chunks):
    prompt_files.append(save_prompt(chunk, i, "produced"))
for i, chunk in enumerate(consumed_chunks):
    prompt_files.append(save_prompt(chunk, i, "consumed"))

# -----------------------------
# STEP 3: Load LLaMA (local) model
# -----------------------------
print(f"🔹 Loading model {MODEL_NAME} on {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, device_map="auto", torch_dtype=torch.float16)
model.eval()

def query_llm(prompt_text, max_tokens=2048):
    inputs = tokenizer(prompt_text, return_tensors="pt").to(DEVICE)
    output = model.generate(**inputs, max_new_tokens=max_tokens)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

# -----------------------------
# STEP 4: Process each prompt
# -----------------------------
for pf in prompt_files:
    with open(pf) as f:
        prompt_text = f.read()
    response = query_llm(prompt_text)
    output_file = os.path.join(LLM_OUTPUT_DIR, os.path.basename(pf).replace(".txt", "_llm.yaml"))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)
    print(f"💡 LLM output saved: {output_file}")

# -----------------------------
# STEP 5: Merge LLM outputs
# -----------------------------
merged = {"produced_apis": [], "consumed_apis": []}

for file in os.listdir(LLM_OUTPUT_DIR):
    if file.endswith("_llm.yaml"):
        with open(os.path.join(LLM_OUTPUT_DIR, file)) as f:
            try:
                data = yaml.safe_load(f)
                if data:
                    for api in data.get("produced_apis", []):
                        if "confidence" not in api:
                            api["confidence"] = 0.9 if "notes" in api else 0.8
                        if "notes" not in api:
                            api["notes"] = "Inferred by LLM or resolved from constants/env"
                        merged["produced_apis"].append(api)
                    for api in data.get("consumed_apis", []):
                        if "confidence" not in api:
                            api["confidence"] = 1.0 if "http" in api.get("target","") else 0.8
                        if "notes" not in api:
                            api["notes"] = "Direct URL detected" if "http" in api.get("target","") else "Inferred by LLM"
                        merged["consumed_apis"].append(api)
            except Exception as e:
                print(f"⚠️ Failed to load {file}: {e}")

with open("api_summary_final.yaml", "w", encoding="utf-8") as f:
    yaml.dump(merged, f, sort_keys=False, allow_unicode=True)

print("✅ Final merged API summary with confidence and notes saved to api_summary_final.yaml")

