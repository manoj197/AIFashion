# 🖌️ Brand Guide

## Brand Voice Guidelines

### Brand Storytelling
- Every brand story must be exactly 2 sentences
- First sentence: Hook with emotional/sensory detail
- Second sentence: Credibility/craft detail
- Always include origin/founder story when possible
- Focus on the *feeling* of wearing the brand, not just features

### Forbidden Words
- "High-quality" (show, don't tell)
- "Premium" (overused)
- "Luxury" (let the story convey it)
- "Sustainable" (say "deadstock" or "organic cotton" instead)
- "Brand" (say "studio", "atelier", "house")

### Copy Hierarchy
1. **Brand Stories**: Evocative, editorial, 2 sentences max
2. **Outfit Names**: Poetic but specific: "The Sunday Editor", "Off-Duty Creative"
3. **Item Descriptions**: Sensory details: "butter-soft cashmere", "crisp poplin"
4. **Recommendations**: Personal: "This is going to transform your mornings"

## Colors

### Primary Palette
| Name | Hex | Usage |
|------|-----|-------|
| Parchment | `#FAF6F1` | Main background |
| Espresso | `#2C2420` | Primary text |
| Burnished Gold | `#8B6F47` | Accents, CTAs, highlights |
| Warm Stone | `#8B7B6B` | Secondary text |
| Sand | `#E8DDD3` | Cards, dividers |

### Accent Palette
| Name | Hex | Usage |
|------|-----|-------|
| Deep Burgundy | `#6B2D3E` | Error states, bold accents |
| Forest Sage | `#4A6B5A` | Success states, nature vibes |
| Midnight | `#1A1A2E` | Dark mode primary |
| Coral Blush | `#D4856A` | Warm highlights |

## Typography

### Display (Headlines)
- **Font**: Cormorant Garamond
- **Weights**: 300 (Light), 400 (Regular), 500 (Medium)
- **Usage**: H1-H3, hero text, outfit names
- **Style**: Often italic for editorial feel

### Body (UI Text)
- **Font**: DM Sans
- **Weights**: 300, 400, 500, 600
- **Usage**: Body text, buttons, labels, descriptions
- **Style**: Clean, modern, highly readable

## Spacing
- **Base unit**: 8px
- **Component padding**: 16-24px
- **Section spacing**: 48-64px
- **Max content width**: 720px (quiz), 1080px (results)

## Borders & Corners
- **Cards**: 16px border-radius
- **Buttons**: 60px border-radius (pill shape)
- **Tags/pills**: 20px border-radius
- **Input fields**: 12px border-radius

## Shadows
- **Subtle**: `0 2px 8px rgba(0,0,0,0.06)`
- **Medium**: `0 8px 24px rgba(0,0,0,0.08)`
- **Elevated**: `0 8px 32px rgba(139,111,71,0.2)`

## Motion
- **Transitions**: 0.3s ease for interactions, 0.5s cubic-bezier(0.4,0,0.2,1) for layout changes
- **Page transitions**: Fade + slight translateY (12px)
- **Loading states**: Subtle pulse animation, never aggressive spinners

## Hidden Gem Brand Criteria
- Founded within last 15 years OR rediscovered vintage brands
- Production under 10,000 units annually
- Featured in niche publications (Monocle, The Gentlewoman, Fantastic Man)
- NOT sold in major department stores (Nordstrom, Saks, etc.)
- Strong origin story tied to place/craft/founder journey
- Price point $50-800 (accessible luxury)

## Brand Data Requirements
```json
{
  "id": "string",
  "name": "string",
  "story": "2 sentences max, editorial tone",
  "origin": "City/region where founded",
  "founded": "Year",
  "price_range": [min, max],
  "signature_pieces": ["array of hero items"],
  "materials_focus": "What they're known for",
  "fit_notes": "How their clothes fit/feel",
  "categories": ["tops", "bottoms", "outerwear", "dresses", "accessories"],
  "style_vibes": ["minimalist", "maximalist", "classic", "avant-garde", "bohemian", "sophisticated"]
}
```