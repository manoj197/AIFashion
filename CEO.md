# 👔 Fashion AI — CEO Command Center

> **You are the founder. This is your only interface.**
> Write your directive below under `## 📋 New Directive`. Push to `main`. The agent chain handles the rest.

---

## 📋 New Directive

### PHASE 1: Full-Stack Foundation — Supabase + Auth + Database + Frontend

We are building a production-grade full-stack application. NO JSON file databases. We use Supabase (hosted Postgres) for everything.

---

#### 1. DATABASE SCHEMA (Supabase/Postgres)

Create a SQL migration file at `database/migrations/001_initial_schema.sql` with these tables:

**users_profile** (extends Supabase auth.users)
- id (uuid, references auth.users)
- display_name (text)
- email (text)
- gender (text: women/men/nonbinary)
- skin_tone (text: fair/light/medium/olive/tan/deep)
- undertone (text: cool/warm/neutral)
- style_vibes (text array, up to 3)
- preferred_occasion (text)
- budget_tier (text: thrifty/moderate/premium/luxury)
- onboarding_completed (boolean, default false)
- created_at (timestamptz)
- updated_at (timestamptz)

**saved_outfits**
- id (uuid, primary key)
- user_id (uuid, references users_profile)
- outfit_name (text)
- outfit_data (jsonb — full outfit with pieces, brands, prices)
- occasion (text)
- created_at (timestamptz)

**user_feedback**
- id (uuid, primary key)
- user_id (uuid, references users_profile)
- outfit_data (jsonb)
- action (text: save/dismiss/like/dislike)
- quiz_answers (jsonb — snapshot of user profile at time of feedback)
- created_at (timestamptz)

**recommendation_logs**
- id (uuid, primary key)
- user_id (uuid, references users_profile)
- request_payload (jsonb — what we sent to Claude API)
- response_payload (jsonb — what Claude returned)
- latency_ms (integer)
- model_version (text)
- created_at (timestamptz)

This table is CRITICAL for the ML pipeline — we log every recommendation request and response so we can train models on what works.

**brand_interactions**
- id (uuid, primary key)
- user_id (uuid, references users_profile)
- brand_name (text)
- interaction_type (text: recommended/saved/dismissed/clicked)
- context (jsonb — skin_tone, style_vibe, occasion at time of interaction)
- created_at (timestamptz)

Add Row Level Security (RLS) policies so users can only read/write their own data.

---

#### 2. AUTHENTICATION

Create `src/api/supabase.js` — Supabase client initialization.

Create `src/components/Auth.jsx` — Authentication component with:
- Email + Password sign up and login
- Google OAuth sign-in button
- Apple OAuth sign-in button
- Phone/SMS OTP sign-in
- Password reset flow
- Clean, branded UI matching our brand guide (warm neutrals, Cormorant Garamond + DM Sans)

Note: Google, Apple, and Phone auth require configuration in the Supabase dashboard. The code should be ready for it — include setup instructions in a `docs/supabase-setup.md` file.

---

#### 3. FRONTEND STRUCTURE

Create a proper React app (using Vite) with these files:

- `src/index.html` — Entry point
- `src/main.jsx` — React root with Supabase provider
- `src/App.jsx` — Router with auth-protected routes
- `src/components/Auth.jsx` — Login/signup (described above)
- `src/components/Layout.jsx` — App shell with navigation
- `src/components/ProfileSetup.jsx` — Post-signup onboarding (collects gender, basic info)
- `src/styles/main.css` — Global styles per brand guide
- `src/api/supabase.js` — Supabase client
- `src/api/database.js` — Database helper functions (CRUD for all tables)
- `package.json` — Dependencies (react, react-router-dom, @supabase/supabase-js)

---

#### 4. DOCUMENTATION

Create `docs/supabase-setup.md` with step-by-step instructions for:
- Creating a Supabase project
- Running the migration SQL
- Enabling Google, Apple, and Phone auth providers
- Setting environment variables
- Connecting from local development

Create `docs/data-dictionary.md` documenting every table, column, type, and purpose — written for a data scientist who will build ML pipelines on this data.

---

#### CTO INSTRUCTIONS
- Write COMPLETE file contents for every file — no placeholders
- Every file must be output as a task with "file_path" and "code" fields in your JSON
- Use ES modules and modern React (hooks, functional components)
- The app must be a Vite project that runs with `npm run dev`

#### CDO INSTRUCTIONS
- Define the analytics events we should track from day one
- Document the ML-ready data model — explain how recommendation_logs and user_feedback tables will feed a future recommendation model
- Define the first 5 SQL queries a data scientist would run to understand user behavior

---

## 📊 Status Reports

_Status reports from the CEO agent will appear here after each pipeline run._

| Run | Date | Directive Summary | Status |
|-----|------|-------------------|--------|
| 6 | 2026-03-14 | Build a mobile-first React MVP that uses AI to recommend luxury outfits from underdog brands based on personalized style quizzes and color theory matching. | ❌ |
| 6 | 2026-03-14 | Build a production-grade full-stack application using Supabase as the database foundation with proper authentication and frontend integration. | ❌ |

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



### Run 6 — 2026-03-14
**Directive**: Build a production-grade full-stack application using Supabase as the database foundation with proper authentication and frontend integration.
**Status**: ❌

**QA Summary**: ```json
{
  "review_status": "fail",
  "blockers": [
    {
      "severity": "critical",
      "description": "No actual implementation artifacts present - only planning documents. Cannot review code that doesn't exist.",
      "file": "src/",
      "fix_suggestion": "CTO and Frontend agents must actually implement the Supabase setup, authentication components, and database integration before QA review is possible"
    },
    {
      "severity": "critical", 
      "description": "Database schema

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
 
