# 👔 Fashion AI

**An AI-powered fashion recommendation platform built and managed by an autonomous agent hierarchy.**

You talk to the CEO. The CEO delegates to a chain of AI agents. They build, design, test, and ship.

---

## 🧠 How It Works

```
You (Founder)
  └── CEO.md ← Write directives here
        └── CEO Agent (orchestrator)
              ├── CPO Agent → Product specs, user stories
              ├── CTO Agent → Architecture, code
              │     ├── Frontend Agent → UI components
              │     └── Backend Agent → API, data logic
              ├── CDO Agent → Metrics, experiments, ML
              │     ├── Analytics Agent → KPIs, funnels
              │     └── ML Agent → Recommendation engine
              ├── Creative Director → Brand, design, copy
              └── QA Agent → Testing, release gates
```

When you push a change to `CEO.md`, GitHub Actions triggers the full agent pipeline. Each agent reads its instructions, does its work, and writes results back to the repo. You check `CEO.md` for the status report.

---

## 🚀 Setup (5 minutes)

### 1. Create a GitHub repo

```bash
# Clone or download this folder, then:
cd fashion-ai
git init
git add -A
git commit -m "Initial commit — Fashion AI agent org"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fashion-ai.git
git push -u origin main
```

### 2. Get a Claude API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an account (or sign in)
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)

### 3. Add the API key to GitHub

1. Go to your repo on GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: paste your API key
6. Click **Add secret**

### 4. Give your first directive

Edit `CEO.md` — your first directive is already written there. Just push to `main`:

```bash
git push origin main
```

### 5. Watch it run

1. Go to your repo → **Actions** tab
2. You'll see "CEO Agent Pipeline" running
3. Wait 2-5 minutes
4. Pull the changes: `git pull`
5. Check `CEO.md` for the status report

---

## 📋 Giving Directives

Edit the `## 📋 New Directive` section in `CEO.md`:

```markdown
## 📋 New Directive

Add a "save outfit" feature so users can bookmark recommendations
and revisit them later. Store saved outfits in localStorage.
```

Then commit and push. The pipeline handles the rest.

### Tips for Good Directives

- **Be specific**: "Add dark mode" is good. "Make it better" is vague.
- **Include acceptance criteria**: "Users with 'minimal' style should see 60% different brands than 'streetwear' users"
- **Reference data**: "Our funnel data shows drop-off at skin tone step — simplify it"
- **One thing at a time**: The agents work best with focused directives

---

## 📁 Repo Structure

```
fashion-ai/
├── CEO.md                          ← YOUR INTERFACE
├── agents/
│   ├── AGENT.md                    ← CEO agent brain
│   ├── cpo/                        ← Product management
│   │   ├── AGENT.md
│   │   ├── backlog.md
│   │   └── current-sprint.md
│   ├── cto/                        ← Engineering
│   │   ├── AGENT.md
│   │   ├── architecture.md
│   │   └── tasks/
│   ├── cdo/                        ← Data & ML
│   │   ├── AGENT.md
│   │   ├── metrics.md
│   │   ├── experiments.md
│   │   └── models/
│   ├── creative/                   ← Design & Brand
│   │   ├── AGENT.md
│   │   └── brand-guide.md
│   └── qa/                         ← Quality & Testing
│       ├── AGENT.md
│       ├── test-cases.md
│       └── release-log.md
├── src/                            ← Application code (written by agents)
├── data/
│   ├── brands.json                 ← Hidden gem brand database
│   ├── color-theory.json           ← Skin tone color mappings
│   └── trends.json                 ← Fashion trend data
├── scripts/
│   ├── orchestrator.py             ← Pipeline brain
│   └── run_local.sh                ← Run locally without GitHub Actions
├── docs/
│   ├── decisions-log.md            ← Why we built what we built
│   └── changelog.md                ← What changed and when
└── .github/workflows/
    └── ceo-pipeline.yml            ← GitHub Actions trigger
```

---

## 🏃 Running Locally (Optional)

If you want to run the pipeline without pushing to GitHub:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

---

## 💰 Cost Estimate

Each pipeline run makes ~7-8 Claude API calls (Sonnet 4). Typical costs:

| Directive Complexity | API Calls | Est. Cost |
|---------------------|-----------|-----------|
| Simple (copy change) | 5-6 | ~$0.20 |
| Medium (new feature) | 7-8 | ~$0.50-$1.00 |
| Complex (major rework) | 8-10 | ~$1.00-$2.00 |

At moderate usage (5-10 directives/week), expect ~$5-$20/month.

---

## 🛠️ Customizing Agents

Each agent's behavior is defined in its `AGENT.md` file. You can edit these to change how agents think:

- **Want stricter QA?** Edit `agents/qa/AGENT.md` to add more checklist items
- **Want a different design style?** Edit `agents/creative/brand-guide.md`
- **Want more data rigor?** Edit `agents/cdo/AGENT.md` to require more metrics
- **Want to add a new agent?** Create a new folder under `agents/` and update `orchestrator.py`

---

## ⚠️ Known Limitations

- Agents can make mistakes — always review code before deploying to production
- Large features may need 2-3 directive cycles to get right
- The CTO agent sometimes truncates code — if a file looks incomplete, re-run the directive
- No real-time collaboration — agents work sequentially, not in parallel
- API rate limits apply — if you run many directives quickly, you may hit limits

---

## 🗺️ Roadmap

- [ ] **Parallel agent execution** — run independent agents simultaneously
- [ ] **Agent memory** — agents remember decisions across runs
- [ ] **PR-based workflow** — agents create PRs instead of committing to main
- [ ] **Slack integration** — get notified when pipeline completes
- [ ] **Cost tracking** — track API spend per directive
- [ ] **Multi-model support** — use different models for different agents

---

Built with ❤️ and Claude by a founder who'd rather write one sentence than manage a team.
