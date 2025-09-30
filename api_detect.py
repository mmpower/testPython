import os
import re
import ast
import yaml

produced = []
consumed = []
constants = {}

# -----------------------------
# HELPER
# -----------------------------
def resolve_value(val):
    """Resolve constants or environment placeholders."""
    if isinstance(val, str):
        # Env variable
        env_match = re.match(r"<ENV:(.*?)>", val)
        if env_match:
            env_name = env_match.group(1)
            return os.getenv(env_name, f"<UNRESOLVED_ENV:{env_name}>")
        # Normal constant
        return constants.get(val, val)
    return val

# -----------------------------
# PYTHON PARSERS
# -----------------------------
def parse_python_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
        # Constants
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                        constants[target.id] = node.value.value
        # Produced APIs
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Call) and hasattr(dec.func,'attr'):
                        if dec.func.attr in ["get","post","put","delete","route"]:
                            route_path = None
                            if dec.args:
                                if isinstance(dec.args[0], ast.Name):
                                    route_path = resolve_value(dec.args[0].id)
                                elif isinstance(dec.args[0], ast.Constant):
                                    route_path = dec.args[0].value
                            produced.append({"file": path,"function": node.name,"method":dec.func.attr.upper(),"path":route_path})
        # Consumed APIs
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func,'attr'):
                if node.func.attr in ["get","post","put","delete"]:
                    if hasattr(node.func.value,'id') and node.func.value.id in ["requests","httpx"]:
                        url_arg = None
                        if node.args:
                            if isinstance(node.args[0], ast.Name):
                                url_arg = resolve_value(node.args[0].id)
                            elif isinstance(node.args[0], ast.Constant):
                                url_arg = node.args[0].value
                        consumed.append({"file":path,"method":node.func.attr.upper(),"target":url_arg})
    except:
        pass

# -----------------------------
# JS / TS PARSER
# -----------------------------
def parse_js_file(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            content = f.read()
        # Constants
        for m in re.finditer(r"(const|let|var)\s+(\w+)\s*=\s*['\"](.*?)['\"]", content):
            constants[m.group(2)] = m.group(3)
        # Produced APIs
        for m in re.finditer(r"(app|router)\.(get|post|put|delete)\(['\"](.*?)['\"]", content):
            path_val = m.group(3)
            if path_val in constants:
                path_val = constants[path_val]
            produced.append({"file": path,"method":m.group(2).upper(),"path":path_val})
        # Consumed APIs (axios/fetch)
        for m in re.finditer(r"(axios|fetch)\.?(get|post)?\(['\"](.*?)['\"]", content):
            url = m.group(3)
            if url in constants:
                url = constants[url]
            consumed.append({"file":path,"method":m.group(2).upper() if m.group(2) else "UNKNOWN","target":url})
        # Environment variables
        for m in re.finditer(r"process\.env\.(\w+)", content):
            val = os.getenv(m.group(1), f"<UNRESOLVED_ENV:{m.group(1)}>")
            constants[m.group(1)] = val
    except:
        pass

# -----------------------------
# JAVA PARSER
# -----------------------------
def parse_java_file(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            content = f.read()
        # Produced APIs
        for m in re.finditer(r"@(GetMapping|PostMapping|RequestMapping)\([\"'](.*?)['\"]", content):
            method = "GET" if "GetMapping" in m.group(1) else "POST" if "PostMapping" in m.group(1) else "UNKNOWN"
            produced.append({"file": path,"method": method,"path": m.group(2)})
        # Consumed APIs
        for m in re.finditer(r"(getForObject|postForObject|get|post)\((\"https?://.*?)\"", content):
            consumed.append({"file": path,"method":"UNKNOWN","target": m.group(2)})
    except:
        pass

# -----------------------------
# GO PARSER
# -----------------------------
def parse_go_file(path):
    try:
        with open(path,"r",encoding="utf-8") as f:
            content = f.read()
        # Constants
        for m in re.finditer(r'const\s+(\w+)\s*=\s*"(.+?)"', content):
            constants[m.group(1)] = m.group(2)
        # Produced APIs
        for m in re.finditer(r'(http\.HandleFunc|mux\.Handle|router\.(GET|POST|PUT|DELETE))\(["`](.*?)["`]', content):
            method = m.group(2).upper() if m.group(2) else "UNKNOWN"
            path_val = m.group(3)
            if path_val in constants:
                path_val = constants[path_val]
            produced.append({"file": path,"method":method,"path":path_val})
        # Consumed APIs
        for m in re.finditer(r'(http\.Get|http\.Post)\(["`](http.*?)["`]', content):
            url = m.group(2)
            if url in constants:
                url = constants[url]
            consumed.append({"file": path,"method":"UNKNOWN","target":url})
    except:
        pass

# -----------------------------
# MAIN SCAN FUNCTION
# -----------------------------
def scan_repo(root_dir="./src"):
    for root, _, files in os.walk(root_dir):
        for file in files:
            full = os.path.join(root,file)
            if file.endswith(".py"):
                parse_python_file(full)
            elif file.endswith(".js") or file.endswith(".ts"):
                parse_js_file(full)
            elif file.endswith(".java"):
                parse_java_file(full)
            elif file.endswith(".go"):
                parse_go_file(full)

if __name__=="__main__":
    scan_repo("./src")
    # Resolve any remaining constants
    for api in produced:
        if isinstance(api.get("path"), str) and api["path"] in constants:
            api["path"] = constants[api["path"]]
    for api in consumed:
        if isinstance(api.get("target"), str) and api["target"] in constants:
            api["target"] = constants[api["target"]]

    result = {"produced_apis": produced,"consumed_apis": consumed,"constants": constants}
    with open("api_summary.yaml","w",encoding="utf-8") as f:
        yaml.dump(result,f,sort_keys=False,allow_unicode=True)
    print("✅ Multi-language API summary with constant/env resolution written to api_summary.yaml")
