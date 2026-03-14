"""
Fashion AI Orchestrator v2.0
=============================
Major improvements over v1:
- CTO agent makes SEPARATE calls per file (no more cramming everything into one JSON)
- Much higher token limits (8192) for code generation
- Robust code extraction that handles markdown code blocks, raw code, and JSON
- Better error handling and logging
- CDO and Creative agents also write files reliably
"""

import os
import sys
import json
import re
import datetime
import anthropic

# ─── Config ──────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS_PLANNING = 4096
MAX_TOKENS_CODE = 8192
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Helpers ─────────────────────────────────────────────────────────────────

def read_file(relative_path):
    """Read a file from the repo."""
    path = os.path.join(REPO_ROOT, relative_path)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(relative_path, content):
    """Write content to a file in the repo."""
    path = os.path.join(REPO_ROOT, relative_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✏️  Wrote: {relative_path}")


def extract_directive(ceo_md):
    """Extract the latest directive from CEO.md."""
    pattern = r"## 📋 New Directive\s*\n(.*?)(?=\n---|\n## |\Z)"
    match = re.search(pattern, ceo_md, re.DOTALL)
    if match:
        directive = match.group(1).strip()
        if directive and directive != "_No directive yet_":
            return directive
    return None


def call_agent(client, agent_name, system_prompt, user_message, max_tokens=MAX_TOKENS_PLANNING):
    """Call Claude API as a specific agent."""
    print(f"\n🤖 Calling {agent_name}...")
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        result = response.content[0].text
        print(f"  ✅ {agent_name} responded ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"  ❌ {agent_name} failed: {e}")
        return None


def parse_json_from_response(response):
    """Extract JSON from an agent response — tries multiple strategies."""
    if not response:
        return None

    # Strategy 1: Find JSON in markdown code block
    json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 2: Parse entire response as JSON
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 3: Find the largest JSON object in response
    brace_depth = 0
    start = None
    candidates = []
    for i, ch in enumerate(response):
        if ch == '{':
            if brace_depth == 0:
                start = i
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth == 0 and start is not None:
                candidates.append(response[start:i+1])
                start = None

    # Try candidates from largest to smallest
    candidates.sort(key=len, reverse=True)
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    return None


def extract_code_from_response(response):
    """Extract code content from a response that may contain markdown code blocks."""
    if not response:
        return None

    # Try to find code in markdown blocks
    code_match = re.search(
        r"```(?:jsx?|tsx?|html|css|sql|python|json|javascript|typescript)\s*\n(.*?)\n```",
        response, re.DOTALL
    )
    if code_match:
        return code_match.group(1).strip()

    # Try generic code block
    code_match = re.search(r"```\s*\n(.*?)\n```", response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # If response looks like raw code (starts with import, const, //, <, CREATE, etc.)
    stripped = response.strip()
    code_indicators = ['import ', 'export ', 'const ', 'function ', 'class ',
                       '<!DOCTYPE', '<html', '<div', '<svg', '//', '/*',
                       'CREATE ', 'ALTER ', 'INSERT ', 'SELECT ',
                       '{', 'from ', 'def ', 'import {']
    for indicator in code_indicators:
        if stripped.startswith(indicator):
            return stripped

    return stripped


def extract_file_list_from_plan(plan_response):
    """Extract a list of files to create from the CTO planning response."""
    parsed = parse_json_from_response(plan_response)
    files = []

    if parsed:
        # Look for tasks with file paths
        tasks = parsed.get("tasks", parsed.get("files", []))
        if isinstance(tasks, list):
            for task in tasks:
                if isinstance(task, dict):
                    fp = task.get("file_path", task.get("path", task.get("file", "")))
                    desc = task.get("description", task.get("desc", task.get("purpose", "")))
                    if fp:
                        files.append({"file_path": fp, "description": desc})

        # Also check for files_to_create
        ftc = parsed.get("files_to_create", [])
        if isinstance(ftc, list):
            for item in ftc:
                if isinstance(item, str):
                    files.append({"file_path": item, "description": ""})
                elif isinstance(item, dict):
                    fp = item.get("file_path", item.get("path", ""))
                    desc = item.get("description", "")
                    if fp:
                        files.append({"file_path": fp, "description": desc})

    # Also try to find file paths in plain text
    if not files:
        path_pattern = r'(?:src|database|docs)/[\w/.-]+\.(?:jsx?|tsx?|css|html|sql|json|md)'
        found_paths = re.findall(path_pattern, plan_response)
        for fp in found_paths:
            if fp not in [f["file_path"] for f in files]:
                files.append({"file_path": fp, "description": ""})

    return files


# ─── Agent Runners ───────────────────────────────────────────────────────────

def run_ceo(client, directive):
    """CEO Agent: Creates execution plan from directive."""
    system_prompt = read_file("agents/AGENT.md") or "You are the CEO agent."

    context_summary = ""
    for fpath in ["agents/cpo/backlog.md", "agents/cto/architecture.md", "agents/cdo/metrics.md"]:
        content = read_file(fpath)
        if content:
            context_summary += f"\n--- {fpath} ---\n{content[:1000]}\n"

    task = f"""The founder has issued a new directive:

\"\"\"{directive}\"\"\"

## Current Project State:
{context_summary}

Create an execution plan. Determine which agents need to be involved, in what order,
and what each agent should deliver. Output your plan as JSON following the format in your AGENT.md."""

    return call_agent(client, "CEO", system_prompt, task)


def run_cpo(client, directive, ceo_plan):
    """CPO Agent: Creates product specs and user stories."""
    system_prompt = read_file("agents/cpo/AGENT.md") or "You are the CPO agent."

    task = f"""FOUNDER DIRECTIVE: \"\"\"{directive}\"\"\"

CEO PLAN: \"\"\"{ceo_plan[:2000]}\"\"\"

Create product specifications with user stories and acceptance criteria.

IMPORTANT: You MUST output valid JSON with these exact fields:
{{
  "features": [...],
  "updated_backlog_md": "full markdown content for backlog.md",
  "updated_sprint_md": "full markdown content for current-sprint.md"
}}

Do NOT include any text before or after the JSON. Output ONLY the JSON object."""

    response = call_agent(client, "CPO", system_prompt, task)
    parsed = parse_json_from_response(response)

    if parsed:
        if "updated_backlog_md" in parsed:
            write_file("agents/cpo/backlog.md", parsed["updated_backlog_md"])
        if "updated_sprint_md" in parsed:
            write_file("agents/cpo/current-sprint.md", parsed["updated_sprint_md"])

    return response


def run_cdo(client, directive, ceo_plan, cpo_specs):
    """CDO Agent: Defines metrics, experiments, and data requirements."""
    system_prompt = read_file("agents/cdo/AGENT.md") or "You are the CDO agent."

    task = f"""FOUNDER DIRECTIVE: \"\"\"{directive}\"\"\"

CEO PLAN: \"\"\"{ceo_plan[:1500]}\"\"\"

CPO SPECS: \"\"\"{cpo_specs[:2000]}\"\"\"

Define success metrics, experiments, and data requirements.

IMPORTANT: You MUST output valid JSON with these exact fields:
{{
  "metrics": [...],
  "experiments": [...],
  "updated_metrics_md": "full markdown content for metrics.md",
  "updated_experiments_md": "full markdown content for experiments.md"
}}

Do NOT include any text before or after the JSON."""

    response = call_agent(client, "CDO", system_prompt, task)
    parsed = parse_json_from_response(response)

    if parsed:
        if "updated_metrics_md" in parsed:
            write_file("agents/cdo/metrics.md", parsed["updated_metrics_md"])
        if "updated_experiments_md" in parsed:
            write_file("agents/cdo/experiments.md", parsed["updated_experiments_md"])
        if "updated_model_md" in parsed:
            write_file("agents/cdo/models/recommendations.md", parsed["updated_model_md"])

    return response


def run_cto_planning(client, directive, cpo_specs, cdo_data):
    """CTO Agent Phase 1: Create a file plan — what files to create and why."""
    system_prompt = """You are the CTO of Fashion AI. Your job right now is ONLY to create a file plan.
List every file that needs to be created or modified, with its full path and a brief description.
Do NOT write any code yet — just plan the files."""

    existing_files = []
    src_dir = os.path.join(REPO_ROOT, "src")
    if os.path.exists(src_dir):
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                existing_files.append(os.path.relpath(os.path.join(root, f), REPO_ROOT))

    task = f"""DIRECTIVE: \"\"\"{directive}\"\"\"

CPO SPECS: \"\"\"{cpo_specs[:2000]}\"\"\"

CDO DATA: \"\"\"{cdo_data[:1500]}\"\"\"

EXISTING FILES: {json.dumps(existing_files)}

BRAND GUIDE: \"\"\"{(read_file('agents/creative/brand-guide.md') or '')[:1500]}\"\"\"

Create a file plan. Output ONLY a JSON object like this:
{{
  "tasks": [
    {{
      "file_path": "src/components/Auth.jsx",
      "description": "Authentication component with email, Google, Apple, Phone sign-in"
    }},
    {{
      "file_path": "database/migrations/001_initial_schema.sql",
      "description": "Supabase database schema with all tables and RLS policies"
    }}
  ]
}}

List ALL files that need to be created. Include src/, database/, docs/ files.
Output ONLY the JSON, nothing else."""

    response = call_agent(client, "CTO (Planning)", system_prompt, task)
    return response


def run_cto_write_file(client, file_path, file_description, directive, context_summary):
    """CTO Agent Phase 2: Write a single complete file."""
    # Determine file type for better prompting
    ext = os.path.splitext(file_path)[1]
    file_type_hints = {
        ".jsx": "React JSX component. Use functional components with hooks. Use modern ES6+ syntax.",
        ".js": "JavaScript module. Use ES6+ modules (import/export).",
        ".css": "CSS stylesheet. Follow the brand guide colors and typography.",
        ".html": "HTML file. Include all necessary script tags and CDN imports.",
        ".sql": "SQL file for Supabase/Postgres. Include CREATE TABLE, RLS policies, indexes.",
        ".md": "Markdown documentation file.",
        ".json": "JSON configuration file.",
    }

    system_prompt = f"""You are a senior full-stack engineer. Your ONLY job is to write the COMPLETE contents of one file: {file_path}

Rules:
- Output ONLY the file contents — no explanations, no markdown code fences, no commentary
- Write the COMPLETE file — no placeholders like "// add more here" or "// rest stays the same"
- The first character of your response should be the first character of the file
- The last character of your response should be the last character of the file
- {file_type_hints.get(ext, "Write complete, production-ready code.")}"""

    brand_guide = read_file("agents/creative/brand-guide.md") or ""
    color_theory = read_file("data/color-theory.json") or ""
    brands_data = read_file("data/brands.json") or ""

    # Build context based on file type
    extra_context = ""
    if ext in [".jsx", ".css", ".html"]:
        extra_context = f"\nBRAND GUIDE:\n{brand_guide[:2000]}"
    if ext == ".sql":
        extra_context = "\nUse uuid_generate_v4() for IDs. Add Row Level Security. Use timestamptz for dates."
    if "recommendation" in file_path.lower() or "api" in file_path.lower():
        extra_context += f"\nBRANDS DATA (sample):\n{brands_data[:2000]}"
        extra_context += f"\nCOLOR THEORY (sample):\n{color_theory[:2000]}"

    task = f"""Write the complete file: {file_path}
Description: {file_description}

PROJECT CONTEXT:
{directive[:1000]}

{context_summary[:1500]}
{extra_context}

Remember: Output ONLY the raw file contents. No markdown fences. No explanations. Start with the first line of code."""

    response = call_agent(client, f"CTO (Writing {file_path})", system_prompt, task, max_tokens=MAX_TOKENS_CODE)

    if response:
        # Clean up response — remove any accidental markdown fences
        code = extract_code_from_response(response)
        if code:
            write_file(file_path, code)
            return True

    return False


def run_creative(client, directive, written_files):
    """Creative Director Agent: Reviews design and writes brand-compliant updates."""
    system_prompt = read_file("agents/creative/AGENT.md") or "You are the Creative Director."

    # Read a few key UI files for review
    ui_previews = ""
    ui_files = [f for f in written_files if f.endswith((".jsx", ".css", ".html"))]
    for fp in ui_files[:3]:
        content = read_file(fp)
        if content:
            ui_previews += f"\n--- {fp} (first 2000 chars) ---\n{content[:2000]}\n"

    task = f"""Review the latest UI code for brand compliance and design quality.

DIRECTIVE: \"\"\"{directive[:500]}\"\"\"

BRAND GUIDE: \"\"\"{(read_file('agents/creative/brand-guide.md') or '')[:2000]}\"\"\"

FILES TO REVIEW:
{ui_previews if ui_previews else "(No UI files written yet)"}

Review for:
1. Brand guide compliance (colors, typography, spacing, tone)
2. Design quality (no generic AI aesthetics)
3. Copy quality (warm, personal, aspirational — never robotic)

Output JSON with:
{{
  "review_status": "approved|needs_changes",
  "feedback": [...],
  "updated_brand_guide_md": "updated brand guide if needed (or null)"
}}"""

    response = call_agent(client, "Creative Director", system_prompt, task)
    parsed = parse_json_from_response(response)

    if parsed:
        if parsed.get("updated_brand_guide_md"):
            write_file("agents/creative/brand-guide.md", parsed["updated_brand_guide_md"])

    return response


def run_qa(client, directive, written_files, all_outputs):
    """QA Agent: Final review gate."""
    system_prompt = read_file("agents/qa/AGENT.md") or "You are the QA agent."

    # Read written files for review
    file_previews = ""
    for fp in written_files[:5]:
        content = read_file(fp)
        if content:
            file_previews += f"\n--- {fp} (first 1500 chars) ---\n{content[:1500]}\n"

    task = f"""Review ALL changes from this pipeline run.

DIRECTIVE: \"\"\"{directive[:500]}\"\"\"

FILES CREATED: {json.dumps(written_files)}

FILE CONTENTS (previews):
{file_previews}

Run through your QA checklist. Output JSON with:
{{
  "review_status": "pass|fail|pass_with_notes",
  "ship_decision": "ship|no_ship|ship_with_followup",
  "blockers": [...],
  "notes": [...],
  "updated_release_log_md": "full markdown for release-log.md",
  "updated_test_cases_md": "full markdown for test-cases.md"
}}"""

    response = call_agent(client, "QA", system_prompt, task)
    parsed = parse_json_from_response(response)

    if parsed:
        if parsed.get("updated_release_log_md"):
            write_file("agents/qa/release-log.md", parsed["updated_release_log_md"])
        if parsed.get("updated_test_cases_md"):
            write_file("agents/qa/test-cases.md", parsed["updated_test_cases_md"])

    return response


def update_ceo_status(directive, written_files, qa_result):
    """Update CEO.md with status report."""
    ceo_md = read_file("CEO.md")
    today = datetime.date.today().isoformat()

    qa_parsed = parse_json_from_response(qa_result) if qa_result else None
    status = "✅"
    ship = "unknown"
    if qa_parsed:
        ship = qa_parsed.get("ship_decision", "unknown")
        if ship == "no_ship":
            status = "❌"
        elif ship == "ship_with_followup":
            status = "⚠️"

    run_count = len(re.findall(r"### Run \d+", ceo_md)) + 1
    files_list = "\n".join([f"  - `{f}`" for f in written_files]) if written_files else "  - No files written"

    report = f"""
### Run {run_count} — {today}
**Status**: {status} ({ship})
**Files Created/Updated**:
{files_list}

**QA Summary**: {qa_result[:400] if qa_result else 'No QA report generated'}

---
"""

    # Replace the awaiting first run placeholder or add to reports section
    if "Awaiting first run" in ceo_md:
        ceo_md = ceo_md.replace(
            "| — | — | Awaiting first run | ⏳ |",
            f"| {run_count} | {today} | Pipeline run | {status} |"
        )

    # Insert report before "## 📝 How To Use"
    if "## 📝 How To Use" in ceo_md:
        ceo_md = ceo_md.replace("## 📝 How To Use", report + "\n## 📝 How To Use")
    else:
        ceo_md += report

    write_file("CEO.md", ceo_md)


# ─── Main Pipeline ───────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🏢 Fashion AI — Agent Pipeline v2.0")
    print("=" * 60)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set. Exiting.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Step 1: Read directive
    ceo_md = read_file("CEO.md")
    if not ceo_md:
        print("❌ CEO.md not found. Exiting.")
        sys.exit(1)

    directive = extract_directive(ceo_md)
    if not directive:
        print("ℹ️  No new directive found in CEO.md. Nothing to do.")
        sys.exit(0)

    print(f"\n📋 Directive found ({len(directive)} chars)")
    all_outputs = ""
    written_files = []

    # Step 2: CEO creates plan
    ceo_plan = run_ceo(client, directive)
    if not ceo_plan:
        print("❌ CEO agent failed. Aborting.")
        sys.exit(1)
    all_outputs += f"CEO: {ceo_plan[:1000]}\n"

    # Step 3: CPO creates specs
    cpo_specs = run_cpo(client, directive, ceo_plan)
    all_outputs += f"CPO: {cpo_specs[:1000]}\n"

    # Step 4: CDO defines data requirements
    cdo_data = run_cdo(client, directive, ceo_plan, cpo_specs)
    all_outputs += f"CDO: {cdo_data[:1000]}\n"

    # Step 5: CTO PLANNING — determine what files to create
    print("\n" + "─" * 40)
    print("📐 CTO Planning Phase")
    print("─" * 40)
    cto_plan = run_cto_planning(client, directive, cpo_specs, cdo_data)
    file_list = extract_file_list_from_plan(cto_plan)

    if not file_list:
        print("  ⚠️  CTO plan didn't produce a clear file list. Trying to extract from directive...")
        # Fallback: extract file paths mentioned in the directive
        path_pattern = r'(?:src|database|docs)/[\w/.-]+\.(?:jsx?|tsx?|css|html|sql|json|md)'
        found_paths = re.findall(path_pattern, directive)
        file_list = [{"file_path": fp, "description": ""} for fp in found_paths]

    print(f"\n📁 Files to create: {len(file_list)}")
    for f in file_list:
        print(f"  → {f['file_path']}")

    # Step 6: CTO WRITING — write each file separately
    print("\n" + "─" * 40)
    print("💻 CTO Code Writing Phase")
    print("─" * 40)

    context_summary = f"CPO: {cpo_specs[:800]}\nCDO: {cdo_data[:800]}"

    for file_info in file_list:
        fp = file_info["file_path"]
        desc = file_info.get("description", "")
        success = run_cto_write_file(client, fp, desc, directive, context_summary)
        if success:
            written_files.append(fp)
        else:
            print(f"  ⚠️  Failed to write: {fp}")

    print(f"\n📊 Successfully wrote {len(written_files)}/{len(file_list)} files")

    # Step 7: Creative Director reviews
    creative_review = run_creative(client, directive, written_files)
    all_outputs += f"Creative: {creative_review[:500]}\n"

    # Step 8: QA reviews everything
    qa_result = run_qa(client, directive, written_files, all_outputs)

    # Step 9: Update CEO.md
    update_ceo_status(directive, written_files, qa_result)

    # Step 10: Write logs
    today = datetime.date.today().isoformat()
    changelog = read_file("docs/changelog.md") or "# Changelog\n"
    changelog += f"\n## {today}\n**Directive**: {directive[:200]}...\n**Files**: {json.dumps(written_files)}\n"
    write_file("docs/changelog.md", changelog)

    decisions_log = read_file("docs/decisions-log.md") or "# Decisions Log\n"
    decisions_log += f"\n## {today}\n**Plan**: {cto_plan[:1000]}\n**Written**: {json.dumps(written_files)}\n"
    write_file("docs/decisions-log.md", decisions_log)

    print("\n" + "=" * 60)
    print(f"✅ Pipeline complete! Wrote {len(written_files)} files.")
    print("=" * 60)


if __name__ == "__main__":
    main()