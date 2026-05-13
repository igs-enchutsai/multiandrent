# Leader Agent

Team leader responsible for task coordination, user conversation, and delegation.

## Role
- Receive user requests from Telegram (text, photos, files)
- Engage in back-and-forth conversation to clarify requirements
- Break down tasks and assign to worker agents
- Monitor progress and report back to users
- Send photos and documents back to users

## MCP Tools

### Conversation
| Tool | Purpose |
|------|---------|
| `reply(text)` | Reply text to user (Telegram) |
| `reply_photo(photo_path, caption)` | Send photo to user |
| `reply_document(file_path, caption)` | Send file to user |
| `get_conversation_history(limit)` | Get recent conversation |
| `list_media_files()` | List received media files |

### Team Management
| Tool | Purpose |
|------|---------|
| `send_to_instance(instance, message)` | Send to another agent |
| `query_team_status()` | Query all agent status |
| `report_progress(message)` | Report task progress |
| `log_to_leader(text)` | Internal log |
| `record_spend(amount_usd)` | Record API cost |

## Backend
- Uses `kiro-cli` as the backend (interactive chat mode)
- MCP server: `python -m kiro_multi_agent.team_mcp --role leader`
- Conversation history tracked in-memory by the daemon API

## Directory Structure
```
leader-agent/
├── .kiro/
│   ├── settings/mcp.json       # MCP config (team server)
│   └── steering/               # Behavior rules
│       ├── 00-agent-rules.md   # Core rules
│       ├── error-recovery.md   # Error handling
│       ├── language.md         # 繁體中文
│       ├── leader-role.md      # Leader responsibilities
│       ├── media-handling.md   # Photo/file handling
│       └── tech-stack.md       # Technology guidelines
├── logs/
└── README.md
```
