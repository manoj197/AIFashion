# 🧪 Test Cases

## TC-001: Style Quiz Flow
- **Precondition**: User lands on app
- **Steps**: Complete all 5 quiz steps (gender → skin tone → style → occasion → budget)
- **Expected**: Each step allows selection, back/forward navigation works, progress indicator updates
- **Edge Cases**: What if user skips a step? What if they go back and change an answer?

## TC-002: Skin Tone Color Matching
- **Precondition**: User selects a skin tone
- **Steps**: Select each of the 6 skin tones
- **Expected**: "Best colors" preview shows colors appropriate for that undertone
- **Validation**: Cross-reference with `data/color-theory.json`

## TC-003: AI Recommendation Generation
- **Precondition**: User completes quiz
- **Steps**: Submit quiz and wait for recommendations
- **Expected**: 3 complete outfits returned, each with 4 pieces, all from hidden gem brands
- **Edge Cases**: API timeout, malformed response, empty response

## TC-004: Budget Compliance
- **Precondition**: User selects a budget range
- **Steps**: Complete quiz with each budget option
- **Expected**: All recommended item prices fall within the selected range
- **Validation**: Parse prices from response and compare to budget bounds

## TC-005: Mobile Responsiveness
- **Precondition**: Load app on 375px viewport
- **Steps**: Navigate through entire flow
- **Expected**: No horizontal scroll, all buttons tappable, text readable

## TC-006: Brand Exclusion
- **Precondition**: None
- **Steps**: Run recommendations 10 times with varied inputs
- **Expected**: ZERO mainstream brands (Nike, Adidas, Zara, H&M, Gucci, Louis Vuitton, etc.)
- **Validation**: Check against mainstream brand blocklist
