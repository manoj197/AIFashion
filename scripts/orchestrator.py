"""
Fashion AI Orchestrator
=======================
Reads CEO.md directives, chains Claude API calls through the agent hierarchy,
writes outputs back to repo files.

Triggered by GitHub Actions when CEO.md is updated.
"""

import os
import sys
import json
import re
import datetime
import anthropic

# ─── Config ──────────────────────────────────────────────────────────────────

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096
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


def call_agent(client, agent_name, system_prompt, user_message, context_files=None):
    """Call Claude API as a specific agent."""
    context = ""
    if context_files:
        for filepath, content in context_files.items():
            if content:
                context += f"\n\n--- FILE: {filepath} ---\n{content}\n"

    full_message = user_message
    if context:
        full_message = f"## Project Context\n{context}\n\n## Your Task\n{user_message}"

    print(f"\n🤖 Calling {agent_name}...")

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": full_message}]
        )
        result = response.content[0].text
        print(f"  ✅ {agent_name} responded ({len(result)} chars)")
        return result
    except Exception as e:
        print(f"  ❌ {agent_name} failed: {e}")
        return None


def parse_json_from_response(response):
    """Extract JSON from an agent response that may contain markdown."""
    if not response:
        return None
    # Try to find JSON block in markdown
    json_match = re.search(r"```(?:json)?\s*\n(.*?)\n```", response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    # Try parsing the whole response as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    # Try finding any JSON object in the response
    json_match = re.search(r"\{.*\}", response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    return None


# ─── Agent Runners ───────────────────────────────────────────────────────────

def run_ceo(client, directive):
    """CEO Agent: Creates execution plan from directive."""
    system_prompt = read_file("agents/AGENT.md") or "You are the CEO agent."
    context = {
        "agents/cpo/backlog.md": read_file("agents/cpo/backlog.md"),
        "agents/cto/architecture.md": read_file("agents/cto/architecture.md"),
        "agents/cdo/metrics.md": read_file("agents/cdo/metrics.md"),
    }
    task = f"""The founder has issued a new directive:

\"\"\"{directive}\"\"\"

Create an execution plan. Determine which agents need to be involved, in what order,
and what each agent should deliver. Output your plan as JSON following the format
in your AGENT.md. Also include a field "summary" with a 1-sentence interpretation
of the directive."""

    response = call_agent(client, "CEO", system_prompt, task, context)
    return response


def run_cpo(client, directive, ceo_plan):
    """CPO Agent: Creates product specs and user stories."""
    system_prompt = read_file("agents/cpo/AGENT.md") or "You are the CPO agent."
    context = {
        "agents/cpo/backlog.md": read_file("agents/cpo/backlog.md"),
        "agents/cpo/current-sprint.md": read_file("agents/cpo/current-sprint.md"),
        "agents/cdo/metrics.md": read_file("agents/cdo/metrics.md"),
    }
    task = f"""The CEO has assigned you the following based on a founder directive.

FOUNDER DIRECTIVE: \"\"\"{directive}\"\"\"

CEO PLAN: \"\"\"{ceo_plan}\"\"\"

Create product specifications with user stories and acceptance criteria.
Output as JSON per your AGENT.md format.
Also output an updated backlog in markdown format in a field called "updated_backlog_md".
Also output an updated sprint in markdown format in a field called "updated_sprint_md"."""

    response = call_agent(client, "CPO", system_prompt, task, context)
    parsed = parse_json_from_response(response)

    # Write CPO outputs
    if parsed:
        if "updated_backlog_md" in parsed:
            write_file("agents/cpo/backlog.md", parsed["updated_backlog_md"])
        if "updated_sprint_md" in parsed:
            write_file("agents/cpo/current-sprint.md", parsed["updated_sprint_md"])

    return response


def run_cdo(client, directive, ceo_plan, cpo_specs):
    """CDO Agent: Defines metrics, experiments, and data requirements."""
    system_prompt = read_file("agents/cdo/AGENT.md") or "You are the CDO agent."
    context = {
        "agents/cdo/metrics.md": read_file("agents/cdo/metrics.md"),
        "agents/cdo/experiments.md": read_file("agents/cdo/experiments.md"),
        "agents/cdo/models/recommendations.md": read_file("agents/cdo/models/recommendations.md"),
        "data/brands.json": read_file("data/brands.json")[:3000],  # Truncate for context
        "data/color-theory.json": read_file("data/color-theory.json")[:2000],
        "data/trends.json": read_file("data/trends.json")[:2000],
    }
    task = f"""The CEO has a directive that needs your data expertise.

FOUNDER DIRECTIVE: \"\"\"{directive}\"\"\"

CEO PLAN: \"\"\"{ceo_plan}\"\"\"

CPO SPECS: \"\"\"{cpo_specs}\"\"\"

Define success metrics, any experiments to run, and data/prompt changes needed.
If the recommendation engine prompt needs updating, include the new prompt.
If data files (brands.json, color-theory.json, trends.json) need updates, describe what to change.
Output as JSON per your AGENT.md format.
Also output updated metrics markdown in a field called "updated_metrics_md".
Also output updated experiments markdown in a field called "updated_experiments_md".
If the recommendation model doc needs updating, include it as "updated_model_md"."""

    response = call_agent(client, "CDO", system_prompt, task, context)
    parsed = parse_json_from_response(response)

    if parsed:
        if "updated_metrics_md" in parsed:
            write_file("agents/cdo/metrics.md", parsed["updated_metrics_md"])
        if "updated_experiments_md" in parsed:
            write_file("agents/cdo/experiments.md", parsed["updated_experiments_md"])
        if "updated_model_md" in parsed:
            write_file("agents/cdo/models/recommendations.md", parsed["updated_model_md"])

    return response


def run_cto(client, directive, ceo_plan, cpo_specs, cdo_data):
    """CTO Agent: Creates engineering tasks and writes code."""
    system_prompt = read_file("agents/cto/AGENT.md") or "You are the CTO agent."

    # Gather existing source files for context
    src_files = {}
    src_dir = os.path.join(REPO_ROOT, "src")
    if os.path.exists(src_dir):
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                filepath = os.path.join(root, f)
                rel = os.path.relpath(filepath, REPO_ROOT)
                try:
                    with open(filepath, "r") as fh:
                        content = fh.read()
                        if len(content) < 5000:  # Only include files under 5k chars
                            src_files[rel] = content
                except:
                    pass

    context = {
        "agents/cto/architecture.md": read_file("agents/cto/architecture.md"),
        "agents/creative/brand-guide.md": read_file("agents/creative/brand-guide.md"),
        **src_files
    }
    task = f"""The CEO has a directive that needs engineering work.

FOUNDER DIRECTIVE: \"\"\"{directive}\"\"\"

CEO PLAN: \"\"\"{ceo_plan}\"\"\"

CPO SPECS: \"\"\"{cpo_specs}\"\"\"

CDO DATA REQUIREMENTS: \"\"\"{cdo_data}\"\"\"

Break this into engineering tasks. For each task that involves writing code,
include the COMPLETE file content (no shortcuts like '// rest stays the same').

IMPORTANT: Follow the brand guide in agents/creative/brand-guide.md for all UI work.

Output as JSON with this structure:
{{
  "architecture_decisions": [...],
  "tasks": [
    {{
      "id": "FE-001",
      "agent": "frontend",
      "description": "...",
      "file_path": "src/components/Example.jsx",
      "code": "// complete file content here"
    }}
  ],
  "updated_architecture_md": "... updated architecture doc ...",
  "updated_frontend_tasks_md": "... updated frontend tasks ...",
  "updated_backend_tasks_md": "... updated backend tasks ..."
}}"""

    response = call_agent(client, "CTO", system_prompt, task, context)
    parsed = parse_json_from_response(response)

    if parsed:
        # Write task tracking files
        if "updated_architecture_md" in parsed:
            write_file("agents/cto/architecture.md", parsed["updated_architecture_md"])
        if "updated_frontend_tasks_md" in parsed:
            write_file("agents/cto/tasks/frontend.md", parsed["updated_frontend_tasks_md"])
        if "updated_backend_tasks_md" in parsed:
            write_file("agents/cto/tasks/backend.md", parsed["updated_backend_tasks_md"])

        # Write actual code files
        tasks = parsed.get("tasks", [])
        for task_item in tasks:
            if "file_path" in task_item and "code" in task_item:
                write_file(task_item["file_path"], task_item["code"])

    return response


def run_creative(client, directive, cto_output):
    """Creative Director Agent: Reviews design and copy quality."""
    system_prompt = read_file("agents/creative/AGENT.md") or "You are the Creative Director."
    context = {
        "agents/creative/brand-guide.md": read_file("agents/creative/brand-guide.md"),
    }

    # Include any new UI files for review
    src_dir = os.path.join(REPO_ROOT, "src")
    if os.path.exists(src_dir):
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                if f.endswith((".jsx", ".css", ".html")):
                    filepath = os.path.join(root, f)
                    rel = os.path.relpath(filepath, REPO_ROOT)
                    try:
                        with open(filepath, "r") as fh:
                            content = fh.read()
                            if len(content) < 5000:
                                context[rel] = content
                    except:
                        pass

    task = f"""Review the latest changes for brand compliance and design quality.

DIRECTIVE CONTEXT: \"\"\"{directive}\"\"\"

CTO OUTPUT: \"\"\"{cto_output[:3000]}\"\"\"

Review all UI code and copy for:
1. Brand guide compliance (colors, typography, spacing, tone)
2. Design quality (no generic AI aesthetics)
3. Copy quality (warm, personal, aspirational — never robotic)

If anything needs fixing, provide the corrected code.
Output as JSON per your AGENT.md format.
If brand guide needs updating, include "updated_brand_guide_md"."""

    response = call_agent(client, "Creative Director", system_prompt, task, context)
    parsed = parse_json_from_response(response)

    if parsed:
        if "updated_brand_guide_md" in parsed:
            write_file("agents/creative/brand-guide.md", parsed["updated_brand_guide_md"])
        # Apply any code fixes from creative review
        if "code_fixes" in parsed:
            for fix in parsed["code_fixes"]:
                if "file_path" in fix and "code" in fix:
                    write_file(fix["file_path"], fix["code"])

    return response


def run_qa(client, directive, all_outputs):
    """QA Agent: Final review gate."""
    system_prompt = read_file("agents/qa/AGENT.md") or "You are the QA agent."
    context = {
        "agents/qa/test-cases.md": read_file("agents/qa/test-cases.md"),
        "agents/creative/brand-guide.md": read_file("agents/creative/brand-guide.md"),
    }

    # Include current source for review
    src_dir = os.path.join(REPO_ROOT, "src")
    if os.path.exists(src_dir):
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                filepath = os.path.join(root, f)
                rel = os.path.relpath(filepath, REPO_ROOT)
                try:
                    with open(filepath, "r") as fh:
                        content = fh.read()
                        if len(content) < 5000:
                            context[rel] = content
                except:
                    pass

    task = f"""Review ALL changes from this pipeline run.

DIRECTIVE: \"\"\"{directive}\"\"\"

AGENT OUTPUTS SUMMARY:
{all_outputs[:4000]}

Run through your QA checklist. Check code quality, UI quality, recommendation quality, and data quality.
Output as JSON per your AGENT.md format.
Also include "updated_release_log_md" with the updated release log.
Also include "updated_test_cases_md" if new test cases are needed."""

    response = call_agent(client, "QA", system_prompt, task, context)
    parsed = parse_json_from_response(response)

    if parsed:
        if "updated_release_log_md" in parsed:
            write_file("agents/qa/release-log.md", parsed["updated_release_log_md"])
        if "updated_test_cases_md" in parsed:
            write_file("agents/qa/test-cases.md", parsed["updated_test_cases_md"])

    return response


def update_ceo_status(directive, ceo_plan, qa_result):
    """Update CEO.md with status report."""
    ceo_md = read_file("CEO.md")
    today = datetime.date.today().isoformat()

    # Parse QA result for status
    qa_parsed = parse_json_from_response(qa_result) if qa_result else None
    status = "✅"
    if qa_parsed:
        ship = qa_parsed.get("ship_decision", "unknown")
        if ship == "no_ship":
            status = "❌"
        elif ship == "ship_with_followup":
            status = "⚠️"

    # Extract summary from CEO plan
    ceo_parsed = parse_json_from_response(ceo_plan) if ceo_plan else None
    summary = "Directive processed"
    if ceo_parsed and "directive_summary" in ceo_parsed:
        summary = ceo_parsed["directive_summary"]

    # Count existing runs
    run_count = ceo_md.count("| ") - 2  # subtract header rows
    run_num = max(run_count, 1)

    # Add status row to table
    new_row = f"| {run_num} | {today} | {summary} | {status} |"
    ceo_md = ceo_md.replace(
        "| — | — | Awaiting first run | ⏳ |",
        new_row
    )

    # Also append to existing table if first run marker is gone
    if "Awaiting first run" not in ceo_md and new_row not in ceo_md:
        table_end = ceo_md.rfind("|")
        if table_end > 0:
            # Find end of the table row
            next_newline = ceo_md.find("\n", table_end)
            if next_newline > 0:
                ceo_md = ceo_md[:next_newline] + "\n" + new_row + ceo_md[next_newline:]

    # Add detailed report
    report = f"""

### Run {run_num} — {today}
**Directive**: {summary}
**Status**: {status}

**QA Summary**: {qa_result[:500] if qa_result else 'No QA report generated'}

---
"""
    # Insert report before "## 📝 How To Use"
    ceo_md = ceo_md.replace(
        "## 📝 How To Use",
        report + "\n## 📝 How To Use"
    )

    write_file("CEO.md", ceo_md)


# ─── Main Pipeline ───────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🏢 Fashion AI — Agent Pipeline Starting")
    print("=" * 60)

    # Check for API key
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

    print(f"\n📋 Directive found:\n{directive[:200]}...")

    # Step 2: CEO creates plan
    ceo_plan = run_ceo(client, directive)
    if not ceo_plan:
        print("❌ CEO agent failed. Aborting pipeline.")
        sys.exit(1)

    all_outputs = f"CEO PLAN:\n{ceo_plan}\n\n"

    # Step 3: CPO creates specs
    cpo_specs = run_cpo(client, directive, ceo_plan)
    all_outputs += f"CPO SPECS:\n{cpo_specs}\n\n"

    # Step 4: CDO defines data requirements
    cdo_data = run_cdo(client, directive, ceo_plan, cpo_specs)
    all_outputs += f"CDO DATA:\n{cdo_data}\n\n"

    # Step 5: CTO creates engineering tasks and writes code
    cto_output = run_cto(client, directive, ceo_plan, cpo_specs, cdo_data)
    all_outputs += f"CTO OUTPUT:\n{cto_output}\n\n"

    # Step 6: Creative Director reviews
    creative_review = run_creative(client, directive, cto_output)
    all_outputs += f"CREATIVE REVIEW:\n{creative_review}\n\n"

    # Step 7: QA reviews everything
    qa_result = run_qa(client, directive, all_outputs)
    all_outputs += f"QA RESULT:\n{qa_result}\n\n"

    # Step 8: Update CEO.md with status report
    update_ceo_status(directive, ceo_plan, qa_result)

    # Step 9: Write full pipeline log
    today = datetime.date.today().isoformat()
    changelog = read_file("docs/changelog.md") or "# Changelog\n"
    changelog += f"\n## {today}\n**Directive**: {directive[:100]}...\n**Pipeline**: Complete\n"
    write_file("docs/changelog.md", changelog)

    decisions_log = read_file("docs/decisions-log.md") or "# Decisions Log\n"
    decisions_log += f"\n## {today}\n{all_outputs[:2000]}\n"
    write_file("docs/decisions-log.md", decisions_log)

    print("\n" + "=" * 60)
    print("✅ Pipeline complete! Check CEO.md for status report.")
    print("=" * 60)


if __name__ == "__main__":
    main()
