# 🧪 Test Cases

## ⚠️ IMPLEMENTATION PENDING
**Status**: These test cases are ready but cannot be executed until code is implemented.

## TC-001: Style Quiz Flow
- **Precondition**: User lands on app
- **Steps**: Complete all 5 quiz steps (gender → skin tone → style → occasion → budget)
- **Expected**: Each step allows selection, back/forward navigation works, progress indicator updates
- **Edge Cases**: What if user skips a step? What if they go back and change an answer?
- **Status**: 🔴 BLOCKED - No quiz components built

## TC-002: Skin Tone Color Matching
- **Precondition**: User selects a skin tone
- **Steps**: Select each of the 6 skin tones
- **Expected**: "Best colors" preview shows colors appropriate for that undertone
- **Validation**: Cross-reference with `data/color-theory.json`
- **Status**: 🔴 BLOCKED - No color-theory.json file exists

## TC-003: AI Recommendation Generation
- **Precondition**: User completes quiz
- **Steps**: Submit quiz and wait for recommendations
- **Expected**: 3 complete outfits returned, each with 4 pieces, all from hidden gem brands
- **Edge Cases**: API timeout, malformed response, empty response
- **Status**: 🔴 BLOCKED - No Claude API integration

## TC-004: Budget Compliance
- **Precondition**: User selects a budget range
- **Steps**: Complete quiz with each budget option
- **Expected**: All recommended item prices fall within the selected range
- **Validation**: Parse prices from response and compare to budget bounds
- **Status**: 🔴 BLOCKED - No recommendation system built

## TC-005: Mobile Responsiveness
- **Precondition**: Load app on 375px viewport
- **Steps**: Navigate through entire flow
- **Expected**: No horizontal scroll, all buttons tappable, text readable
- **Status**: 🔴 BLOCKED - No UI components built

## TC-006: Brand Exclusion
- **Precondition**: None
- **Steps**: Run recommendations 10 times with varied inputs
- **Expected**: ZERO mainstream brands (Nike, Adidas, Zara, H&M, Gucci, Louis Vuitton, etc.)
- **Validation**: Check against mainstream brand blocklist
- **Status**: 🔴 BLOCKED - No brand database exists

## TC-007: Error Handling (NEW)
- **Precondition**: App is running
- **Steps**: Disconnect internet, try to submit quiz
- **Expected**: Graceful error message, retry option
- **Status**: 🔴 BLOCKED - No error handling implemented

## TC-008: Loading States (NEW)
- **Precondition**: App is running
- **Steps**: Submit quiz and observe loading behavior
- **Expected**: Elegant loading animation, no blank screens
- **Status**: 🔴 BLOCKED - No loading states implemented

---

## 🔄 Post-Implementation Checklist
Once code is built, verify:
- [ ] All components render without crashing
- [ ] Quiz state management works correctly
- [ ] API calls handle success/error/loading states
- [ ] Brand database is populated with underdog brands only
- [ ] Color theory mappings are scientifically accurate
- [ ] Mobile responsiveness across device sizes
- [ ] Design matches brand guide specifications