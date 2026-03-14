# 🤖 Recommendation Engine

## Current Model: v1.0 — Prompt-Based

### Architecture
We use Claude API as our recommendation engine. The "model" is the prompt we send.

### Prompt Strategy
The recommendation prompt is assembled from user quiz answers and includes:
1. **User Profile**: gender, skin tone, undertone, style vibes, occasion, budget
2. **Color Theory**: skin-tone-specific color recommendations from `data/color-theory.json`
3. **Brand Database**: curated hidden gem brands from `data/brands.json`
4. **Trend Context**: current season trends from `data/trends.json`
5. **Output Format**: structured JSON for consistent parsing

### Personalization Signals (ranked by importance)
1. Skin tone + undertone → drives color palette (highest weight)
2. Style vibe → drives brand selection and item types
3. Occasion → drives formality level and piece types
4. Budget → constrains brand selection
5. Gender → drives cut/fit recommendations

### Prompt Version History
| Version | Date | Change | Impact |
|---------|------|--------|--------|
| v1.0 | Initial | Base prompt | Baseline |

### Known Limitations
- No user history (can't learn from past preferences)
- No real-time trend data (trends are manually updated)
- Brand database requires manual curation
- No feedback loop (user ratings don't improve future recommendations)

### Improvement Roadmap
1. Add user feedback collection → train on preferred vs rejected outfits
2. Add seasonal/regional trend weighting
3. Add brand availability checking (are items actually in stock?)
4. Build collaborative filtering (users like you also liked…)
