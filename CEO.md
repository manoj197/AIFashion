# 👔 Fashion AI — CEO Command Center

> **You are the founder. This is your only interface.**
> Write your directive below under `## 📋 New Directive`. Push to `main`. The agent chain handles the rest.

---

## 📋 New Directive

Build the initial Fashion AI application — an AI-powered style recommendation app that:
1. Asks users a style quiz (gender, skin tone, style vibe, occasion, budget)
2. Matches colors to their skin tone using color theory
3. Recommends complete outfits from hidden gem / underdog brands (NOT mainstream brands)
4. Uses current 2025-2026 fashion trends
5. Is mobile-first, beautiful, and feels like a luxury editorial experience

This is our MVP. Make it a single-page React app that calls the Claude API for personalized recommendations.

---

## 📊 Status Reports

_Status reports from the CEO agent will appear here after each pipeline run._

| Run | Date | Directive Summary | Status |
|-----|------|-------------------|--------|
| 6 | 2026-03-14 | Build a mobile-first React MVP that uses AI to recommend luxury outfits from underdog brands based on personalized style quizzes and color theory matching. | ❌ |

---



### Run 6 — 2026-03-14
**Directive**: Build a mobile-first React MVP that uses AI to recommend luxury outfits from underdog brands based on personalized style quizzes and color theory matching.
**Status**: ❌

**QA Summary**: ```json
{
  "review_status": "fail",
  "blockers": [
    {
      "severity": "critical",
      "description": "No actual code has been implemented - src/ directory is empty with only a README placeholder",
      "file": "src/",
      "fix_suggestion": "CTO Agent needs to implement the React application architecture and Frontend Agent needs to build the UI components"
    },
    {
      "severity": "critical",
      "description": "Missing all data files required for the application (brands.json,

---

## 📝 How To Use

1. Write your directive above under `## 📋 New Directive`
2. Commit and push to `main`
3. GitHub Actions triggers the agent pipeline automatically
4. Check back here for the status report (auto-updated by CEO agent)
5. Review changes in `src/`, `agents/`, and `docs/`

### Example Directives

```
Add a feature where users can upload a selfie and we auto-detect skin tone.
```

```
The recommendations feel too generic. Make them more personalized based on style vibe.
Acceptance criteria: users with "minimal" style should get at least 60% different brands
than users with "streetwear" style.
```

```
Add a "save outfit" feature so users can bookmark recommendations and revisit them later.
```

```
Our conversion data shows users drop off at the skin tone step. Simplify it.
```
