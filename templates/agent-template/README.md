# Agent Template

## Usage

Copy this directory when creating a new agent:

```bash
cp -r templates/agent-template agents/<new-agent-name>
```

Then:
1. Edit `.kiro/settings/mcp.json` - replace `__AGENT_NAME__`
2. Add `language.md` steering (mandatory - 繁體中文)
3. Add steering files for your agent's domain
4. Use `create_forum_topic()` to create a Telegram Forum Topic
5. Add the instance to `team.yaml` with the topic_id
6. Use `restart_team()` to reload config

## Directory Structure

```
<agent-name>/
+-- .kiro/
|   +-- settings/mcp.json       # MCP tools (replace __AGENT_NAME__)
|   +-- steering/                # Behavior rules
|   |   +-- 00-agent-rules.md   # Core rules (do not modify)
|   |   +-- error-recovery.md   # Error handling SOP
|   |   +-- local-llm.md        # kiro-cli & MCP communication
|   |   +-- media-handling.md   # Image/file handling
|   |   +-- tech-stack.md       # Technology guidelines
|   |   +-- test-policy.md      # Testing requirements
|   |   +-- language.md         # <- ADD: 繁體中文 (mandatory)
|   |   +-- project.md          # <- ADD: project-specific rules
|   +-- skills/                  # Custom skills
+-- logs/                        # Auto-generated logs
+-- README.md
```

## MCP Tools Available

| Tool | Purpose |
|------|---------|
| `reply(text)` | Reply to user (Telegram) |
| `reply_photo(photo_path, caption)` | Send photo to user |
| `reply_document(file_path, caption)` | Send file to user |
| `get_conversation_history(limit)` | Get recent conversation |
| `list_media_files()` | List received media files |
| `query_team_status()` | Query team status |
| `log_to_leader(text)` | Send internal message to leader |
| `report_progress(message)` | Report task progress |
| `record_spend(amount_usd)` | Record API cost |
| `send_to_instance(instance, message)` | Send to another agent (leader only) |
| `create_forum_topic(name, instance)` | Create Forum Topic (leader only) |
| `restart_team()` | Restart all agents (leader only) |

## 強制規範

1. 一律使用繁體中文回覆
2. 每個 Agent 必須有獨立的 Telegram Forum Topic
3. 檔案路徑一律使用絕對路徑
4. 每次回覆都必須使用 `reply()` MCP 工具
