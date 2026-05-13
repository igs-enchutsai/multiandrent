---
inclusion: always
---

# GIF Finder Usage Examples & Test Cases

## Test Scenarios

### 1. Basic Emotion Queries
```
User: 開心
Expected: Happy/celebration GIFs with cheerful, positive vibes

User: 震驚  
Expected: Surprised/shocked reaction GIFs, wide eyes, jaw drop

User: 尷尬
Expected: Awkward/embarrassed GIFs, nervous smiles, face palm
```

### 2. Workplace Context
```
User: 老闆傻眼
Expected: Professional-appropriate confused/speechless reactions
Avoid: Overly dramatic, disrespectful, or mocking GIFs

User: 我要回覆主管但不要太白目
Expected: Polite, safe acknowledgment GIFs
Avoid: Eye-rolling, sarcastic, or dismissive reactions
```

### 3. Specific Scenarios
```
User: 終於完成任務
Expected: Relief, celebration, "finally done" themed GIFs
Keywords: "finally finished", "task complete", "relief", "success"

User: 貓咪跳舞
Expected: Cat dancing GIFs, cute animal content
Keywords: "cat dancing", "dancing cat", "cute cat moves"
```

### 4. Multiple Results
```
User: 給我5張慶祝成功的GIF
Expected: 5 different celebration GIFs categorized by style:
- Professional celebration
- Cute/adorable celebration  
- Funny/humorous celebration
- Epic/dramatic celebration
- Subtle/modest celebration
```

### 5. Context-Aware Responses
```
User: 傳給同事的開心GIF
Context: Workplace-friendly
Expected: Professional but positive GIFs

User: 傳給朋友群組的搞笑GIF  
Context: Casual/humorous
Expected: Funny, expressive, entertaining GIFs
```

## Response Quality Checklist

### ✅ Good Response Includes:
- Direct GIF image display using ![GIF](url)
- Clear usage context explanation
- Source attribution (Tenor/GIPHY/etc.)
- Direct link for easy copying
- Appropriate content for stated context

### ❌ Avoid:
- Broken or invalid GIF links
- Inappropriate content for context
- Missing source attribution
- Overly long explanations
- Generic/irrelevant GIFs

## Error Handling Test Cases

### 1. Missing API Keys
```
User: 開心
Expected Response:
"GIF search requires API setup. Please add to your .env file:
[API setup instructions]"
```

### 2. No Results Found
```
User: [Very specific/unusual request]
Expected Response:
"I couldn't find suitable GIFs for '[query]'. Try rephrasing with:
- [Alternative suggestions]"
```

### 3. API Failure
```
User: [Any request when API is down]
Expected Response:
"GIF search is temporarily unavailable. Please try again later or with different keywords."
```

## Commercial Use Reminders

### Trigger Phrases:
- "商業使用"
- "commercial use"  
- "for business"
- "公司用途"
- "營利用途"

### Expected Response Addition:
```
⚠️ For commercial use, please verify the GIF's licensing terms on the source platform. 
This recommendation is for personal/internal communication use.
```

## Keyword Transformation Examples

### Chinese to English
- 開心 → "happy", "joy", "celebration", "excited"
- 震驚 → "shocked", "surprised", "speechless", "wow"  
- 傻眼 → "confused", "speechless", "what", "stunned"
- 完成 → "done", "finished", "complete", "success"

### Context Modifiers
- 職場 → add "office", "professional", "work"
- 可愛 → add "cute", "adorable", "sweet"
- 搞笑 → add "funny", "hilarious", "comedy"
- 誇張 → add "dramatic", "over the top", "epic"

### Character/Theme Specific
- 貓咪 → "cat", "kitten", "feline"
- 動漫 → "anime", "manga", "animated"
- 卡通 → "cartoon", "animated", "character"
