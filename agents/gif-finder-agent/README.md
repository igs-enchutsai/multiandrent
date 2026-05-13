# GIF Finder Agent

A specialized agent that helps users find appropriate GIFs for chat, social media, or workplace communication.

## Features

- **Natural Language Input**: Understands emotions, situations, and contexts in multiple languages
- **Smart Search**: Converts user input into effective GIF search keywords
- **Context Awareness**: Adjusts GIF selection based on usage scenario (workplace, friends, social media)
- **Multiple Results**: Can provide categorized multiple GIF options
- **Safety First**: Filters out inappropriate content for different contexts

## Usage Examples

```
User: 開心
Agent: [Returns happy/celebration GIFs]

User: 老闆傻眼
Agent: [Returns workplace-appropriate shocked reaction GIFs]

User: 給我5張貓咪跳舞的GIF
Agent: [Returns 5 categorized cat dancing GIFs]

User: 我要回覆主管但不要太白目
Agent: [Returns professional, polite reaction GIFs]
```

## Environment Setup

Add to your `.env` file:

```env
# GIF API Keys (at least one required)
TENOR_API_KEY=your_tenor_api_key
GIPHY_API_KEY=your_giphy_api_key

# Default provider (optional)
GIF_PROVIDER=tenor
```

## API Keys Setup

### Tenor API (Recommended)
1. Visit [Tenor Developer Portal](https://developers.google.com/tenor)
2. Create an account and get API key
3. Add `TENOR_API_KEY` to `.env`

### GIPHY API (Alternative)
1. Visit [GIPHY Developers](https://developers.giphy.com/)
2. Create an account and get API key  
3. Add `GIPHY_API_KEY` to `.env`

## Response Format

The agent returns GIFs in this format:

```markdown
I found this GIF that fits well:

![GIF](https://media.tenor.com/example.gif)

Usage context:
Perfect for expressing "finally done, what a relief" feeling.

Source:
Tenor

Direct link:
https://media.tenor.com/example.gif
```

## Safety & Licensing

- **Personal Use**: Default assumption for chat/social communication
- **Commercial Use**: Agent will remind users to verify licensing
- **Content Filtering**: Automatically avoids inappropriate content based on context
- **Workplace Safe**: Special filtering for professional environments

## Error Handling

- **No API Key**: Clear setup instructions
- **No Results**: Suggests alternative keywords
- **API Failure**: Graceful fallback with retry suggestions

## Team Integration

Add to `team.yaml`:

```yaml
instances:
  gif-finder-agent:
    working_directory: ./agents/gif-finder-agent
    description: "GIF search and recommendation agent"
    topic_id: [your_topic_id]
    role: worker
```
