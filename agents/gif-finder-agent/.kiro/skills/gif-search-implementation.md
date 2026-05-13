---
inclusion: always
---

# GIF Search Implementation Guide

## Search Strategy

### 1. Keyword Generation
Transform user input into effective search terms:

```python
def generate_gif_keywords(user_input: str, context: str = "general") -> list[str]:
    """
    Generate multiple search keyword variations for GIF search.
    
    Args:
        user_input: User's natural language input
        context: Usage context (workplace, friends, social, etc.)
    
    Returns:
        List of search keyword combinations
    """
    # Base emotion/action mapping
    emotion_map = {
        "開心": ["happy", "celebration", "joy", "excited"],
        "震驚": ["shocked", "surprised", "speechless", "wow"],
        "傻眼": ["confused", "speechless", "what", "stunned"],
        "尷尬": ["awkward", "embarrassed", "nervous", "uncomfortable"],
        "完成": ["done", "finished", "complete", "success", "relief"]
    }
    
    # Context-specific modifiers
    context_modifiers = {
        "workplace": ["office", "professional", "work", "business"],
        "friends": ["funny", "cute", "hilarious", "awesome"],
        "social": ["viral", "trending", "popular", "meme"]
    }
    
    # Generate combinations
    keywords = []
    # Add base keywords + "gif"
    # Add context modifiers
    # Add character/theme specific terms
    
    return keywords
```

### 2. Search Sources Priority

1. **Tenor API** (Primary - chat optimized)
2. **GIPHY API** (Secondary - broader selection)  
3. **Web Search** (Fallback - general image search)

### 3. Content Filtering

```python
def filter_safe_gifs(gifs: list, context: str) -> list:
    """
    Filter GIFs based on safety and context appropriateness.
    
    Workplace context: Extra strict filtering
    General context: Standard safety filtering
    """
    # Check for inappropriate keywords in titles/tags
    unsafe_keywords = ["nsfw", "adult", "sexual", "violence", "hate"]
    workplace_avoid = ["party", "drunk", "crazy", "wild", "sexy"]
    
    # Apply filtering logic
    return filtered_gifs
```

## API Integration Examples

### Tenor API Search
```python
import requests
import os

def search_tenor_gifs(query: str, limit: int = 8) -> list:
    """Search Tenor for GIFs matching query."""
    api_key = os.getenv("TENOR_API_KEY")
    if not api_key:
        return []
    
    url = "https://tenor.googleapis.com/v2/search"
    params = {
        "q": query,
        "key": api_key,
        "limit": limit,
        "media_filter": "gif",
        "contentfilter": "medium"  # Safe for most contexts
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        gifs = []
        for result in data.get("results", []):
            gif_data = {
                "url": result["media_formats"]["gif"]["url"],
                "preview": result["media_formats"]["tinygif"]["url"],
                "title": result.get("content_description", ""),
                "source": "Tenor"
            }
            gifs.append(gif_data)
        
        return gifs
    except Exception as e:
        return []
```

### GIPHY API Search
```python
def search_giphy_gifs(query: str, limit: int = 8) -> list:
    """Search GIPHY for GIFs matching query."""
    api_key = os.getenv("GIPHY_API_KEY")
    if not api_key:
        return []
    
    url = "https://api.giphy.com/v1/gifs/search"
    params = {
        "api_key": api_key,
        "q": query,
        "limit": limit,
        "rating": "pg-13"  # Family-friendly content
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        gifs = []
        for result in data.get("data", []):
            gif_data = {
                "url": result["images"]["original"]["url"],
                "preview": result["images"]["preview_gif"]["url"],
                "title": result.get("title", ""),
                "source": "GIPHY"
            }
            gifs.append(gif_data)
        
        return gifs
    except Exception as e:
        return []
```

## Response Formatting

### Single GIF Response
```markdown
I found this GIF that fits well:

![GIF]({gif_url})

Usage context:
{context_explanation}

Source:
{source_platform}

Direct link:
{gif_url}
```

### Multiple GIF Response
```markdown
Here are {count} GIFs for "{user_query}":

## 1. {category_1}
![GIF]({gif_url_1})

## 2. {category_2}  
![GIF]({gif_url_2})

## 3. {category_3}
![GIF]({gif_url_3})

[Continue for all requested GIFs...]
```

## Error Handling

### No API Keys
```markdown
GIF search requires API setup. Please add to your .env file:

```env
TENOR_API_KEY=your_tenor_key
# or
GIPHY_API_KEY=your_giphy_key
```

Get API keys from:
- Tenor: https://developers.google.com/tenor
- GIPHY: https://developers.giphy.com/
```

### No Results Found
```markdown
I couldn't find suitable GIFs for "{user_query}". 

Try rephrasing with:
- More specific emotions (happy → excited, celebrating)
- Different style (cute, funny, professional)
- Alternative keywords (boss → manager, done → finished)
```

### API Rate Limits
```markdown
GIF search is temporarily limited. Please try again in a few minutes or use different keywords.
```

## Usage Context Detection

```python
def detect_usage_context(user_input: str) -> str:
    """Detect intended usage context from user input."""
    workplace_indicators = ["主管", "老闆", "同事", "工作", "boss", "manager", "colleague", "work", "office"]
    friend_indicators = ["朋友", "好友", "群組", "friend", "buddy", "group chat"]
    social_indicators = ["社群", "貼文", "分享", "social", "post", "share"]
    
    input_lower = user_input.lower()
    
    if any(word in input_lower for word in workplace_indicators):
        return "workplace"
    elif any(word in input_lower for word in friend_indicators):
        return "friends"
    elif any(word in input_lower for word in social_indicators):
        return "social"
    else:
        return "general"
```
