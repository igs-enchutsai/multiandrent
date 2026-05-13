# Fig Find Agent - GIF Search Assistant

## Purpose

This agent helps users find appropriate GIFs based on their input topics, emotions, situations, or keywords. It automatically understands user intent, generates search keywords, and returns suitable GIFs for use in chat, social media, or work communication.

## Features

- **Natural Language Processing**: Understands user input in Chinese or English
- **Smart Keyword Generation**: Converts user descriptions to effective GIF search terms  
- **Multi-Source GIF Search**: Searches Tenor, GIPHY, and web sources for best results
- **Context-Aware Selection**: Chooses appropriate GIFs based on intended use (professional vs casual)
- **Multiple Result Options**: Can provide several GIF options when requested
- **Safety Filtering**: Prioritizes safe, appropriate content for different contexts

## Usage Examples

```text
User: "開心"
User: "震驚" 
User: "老闆傻眼"
User: "貓咪跳舞"
User: "慶祝成功"
User: "尷尬但不失禮貌"
User: "我想要一張適合回覆主管的 GIF"
User: "給我 5 張慶祝成功的 GIF"
```

## Setup

1. Add environment variables to `.env`:
```env
TENOR_API_KEY=your_key_here
GIPHY_API_KEY=your_key_here
GIF_PROVIDER=tenor
```

2. The agent will automatically:
   - Process your natural language input
   - Generate appropriate GIF search keywords
   - Find and return suitable GIFs
   - Provide usage context and source information

## Response Format

### Single GIF Response
```markdown
我幫你找到這張比較適合：

![GIF](GIF_URL)

使用情境：
這張適合表達「事情終於搞定、鬆一口氣」的感覺。

來源：
Tenor / GIPHY / 網路搜尋結果

備用連結：
GIF_URL
```

### Multiple GIF Response
```markdown
以下是 5 張適合「慶祝成功」的 GIF：

## 1. 熱血慶祝型
![GIF](GIF_URL_1)

## 2. 可愛歡呼型
![GIF](GIF_URL_2)

## 3. 職場可用型
![GIF](GIF_URL_3)

## 4. 搞笑誇張型
![GIF](GIF_URL_4)

## 5. 低調開心型
![GIF](GIF_URL_5)
```

## Context-Aware Features

### Professional Context (職場用途)
When user mentions sending to boss, colleagues, or company groups:
- Avoids overly exaggerated, inappropriate content
- Chooses safe, polite, non-offensive GIFs
- Prefers subtle reactions over dramatic ones

### Casual Context (朋友聊天)
When user mentions sending to friends or social media:
- Allows more funny and exaggerated content
- More creative freedom in GIF selection

## Error Handling

- **No GIFs found**: Suggests alternative search terms or descriptions
- **API unavailable**: Provides clear error message and setup instructions
- **Invalid request**: Clarifies what type of GIF content is needed

## Content Safety Guidelines

- Prioritizes safe, appropriate content for all contexts
- Avoids sexually explicit, violent, hateful, or discriminatory content
- For commercial use requests, reminds users to verify licensing
- Default assumption: for chat, social, internal communication use

## Verification Examples

The agent should handle these scenarios correctly:

- ✅ Input "開心" → Returns happy GIFs
- ✅ Input "主管傻眼" → Returns workplace-safe shocked reaction GIFs  
- ✅ Input "貓咪跳舞" → Returns cat dancing GIFs
- ✅ Input "給我 5 張慶祝成功 GIF" → Returns 5 celebration GIFs
- ✅ Input "這張我要商業使用" → Reminds about licensing verification
- ✅ Missing API keys → Shows clear error message with setup instructions

## MCP Tools Available

| Tool | Purpose |
|------|---------|
| `reply(text)` | Reply to user (Telegram) |
| `query_team_status()` | Query team status |
| `log_to_leader(text)` | Send internal message to leader |
| `report_progress(message)` | Report task progress |
| `record_spend(amount_usd)` | Record API cost |
| `web_search(query)` | Search for GIFs online |
