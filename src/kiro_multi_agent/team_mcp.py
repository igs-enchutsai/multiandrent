"""Team MCP Server - cross-agent communication tools via stdio JSON-RPC."""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


_port = 8470
_instance = "unknown"
_role = "worker"
_allowed_targets: list[str] = []


def _api(method: str, path: str, data: dict | None = None, max_retries: int = 3) -> dict:
    """Call Daemon API with retry + exponential backoff."""
    url = f"http://127.0.0.1:{_port}{path}"
    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"} if body else {}

    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, data=body, method=method, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                return {"ok": False, "error": f"HTTP {e.code}"}
        except Exception:
            pass
        if attempt < max_retries:
            time.sleep(0.5 * (2 ** attempt))

    return {"ok": False, "error": "API unreachable"}


def _respond(msg_id, result, error=None) -> None:
    resp = {"jsonrpc": "2.0", "id": msg_id}
    if error:
        resp["error"] = error
    else:
        resp["result"] = result
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()


def _handle_tool(name: str, args: dict) -> str:
    if name == "reply":
        r = _api("POST", "/api/reply", {"instance": _instance, "text": args["text"], "kind": args.get("kind", "primary")})
        return "sent" if r.get("ok") else f"failed: {r}"
    elif name == "reply_photo":
        r = _api("POST", "/api/reply/photo", {
            "instance": _instance,
            "photo_path": args["photo_path"],
            "caption": args.get("caption", ""),
        })
        return "photo sent" if r.get("ok") else f"failed: {r}"
    elif name == "reply_document":
        r = _api("POST", "/api/reply/document", {
            "instance": _instance,
            "file_path": args["file_path"],
            "caption": args.get("caption", ""),
        })
        return "document sent" if r.get("ok") else f"failed: {r}"
    elif name == "query_team_status":
        r = _api("GET", "/api/status")
        lines = []
        for s in r.get("instances", []):
            icon = {"running": "G", "stopped": "W", "crashed": "R"}.get(s["status"], "?")
            lines.append(f"[{icon}] {s['name']} - {s['status']}")
        return "\n".join(lines) or "no instances"
    elif name == "log_to_leader":
        _api("POST", "/api/log", {"instance": _instance, "text": args["text"]})
        return "logged"
    elif name == "send_to_instance":
        if _role != "leader":
            return "permission denied: only leader can send"
        r = _api("POST", "/api/send", {"instance": args["instance"], "message": args["message"], "source": _instance})
        return "sent" if r.get("ok") else f"failed: {r}"
    elif name == "report_progress":
        _api("POST", "/api/progress", {"instance": _instance, "message": args["message"]})
        return "progress updated"
    elif name == "record_spend":
        r = _api("POST", "/api/costs/spend", {"instance": _instance, "amount_usd": float(args.get("amount_usd", 0))})
        return "recorded" if r.get("ok") else f"failed: {r}"
    elif name == "get_conversation_history":
        r = _api("GET", f"/api/conversation/{_instance}?limit={args.get('limit', 20)}")
        if r.get("ok"):
            messages = r.get("messages", [])
            if not messages:
                return "no conversation history"
            lines = []
            for m in messages:
                ts = m.get("timestamp", "")
                role = m.get("role", "?")
                text = m.get("text", "")[:200]
                lines.append(f"[{ts}] {role}: {text}")
            return "\n".join(lines)
        return "no conversation history"
    elif name == "list_media_files":
        r = _api("GET", f"/api/media/{_instance}")
        if r.get("ok"):
            files = r.get("files", [])
            if not files:
                return "no media files"
            return "\n".join(files)
        return "no media files"
    elif name == "create_forum_topic":
        topic_name = args.get("name", "")
        instance = args.get("instance", "")
        if not topic_name:
            return "error: name is required"
        r = _api("POST", "/api/topic/create", {
            "name": topic_name,
            "instance": instance,
        })
        if r.get("ok"):
            topic_id = r.get("topic_id")
            return f"topic created: name={topic_name}, topic_id={topic_id}"
        return f"failed: {r.get('error', 'unknown error')}"
    elif name == "restart_team":
        # Use full restart (reloads Python code) for safety
        r = _api("POST", "/api/team/full-restart")
        if r.get("ok"):
            return "✅ 完整重啟已啟動，daemon 將重新載入所有程式碼和配置。"
        # Fallback to soft restart
        r = _api("POST", "/api/team/restart")
        if r.get("ok"):
            total = r.get("total", 0)
            running = r.get("running", 0)
            instances = r.get("instances", {})
            lines = [f"重啟完成: {running}/{total} running"]
            for inst, status in instances.items():
                icon = "✅" if status == "running" else "❌"
                lines.append(f"  {icon} {inst}: {status}")
            return "\n".join(lines)
        return f"restart failed: {r.get('error', 'unknown')}"
    return f"unknown tool: {name}"


_TOOLS = [
    {
        "name": "reply",
        "description": "Reply to user via Telegram (text message).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Message text to send"},
                "kind": {"type": "string", "enum": ["primary", "followup"], "default": "primary"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "reply_photo",
        "description": "Send a photo/image to user via Telegram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "photo_path": {"type": "string", "description": "Absolute or relative path to the image file"},
                "caption": {"type": "string", "description": "Optional caption for the photo"},
            },
            "required": ["photo_path"],
        },
    },
    {
        "name": "reply_document",
        "description": "Send a file/document to user via Telegram.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Absolute or relative path to the file"},
                "caption": {"type": "string", "description": "Optional caption for the document"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "query_team_status",
        "description": "Query team agent status.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "log_to_leader",
        "description": "Send internal message to leader (not visible to user).",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "report_progress",
        "description": "Report task progress.",
        "inputSchema": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
    },
    {
        "name": "record_spend",
        "description": "Record API spend for cost tracking.",
        "inputSchema": {
            "type": "object",
            "properties": {"amount_usd": {"type": "number"}},
            "required": ["amount_usd"],
        },
    },
    {
        "name": "send_to_instance",
        "description": "Send message to another agent (leader only).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "instance": {"type": "string", "description": "Target agent instance name"},
                "message": {"type": "string", "description": "Message to send"},
            },
            "required": ["instance", "message"],
        },
    },
    {
        "name": "get_conversation_history",
        "description": "Get recent conversation history for this instance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Max messages to retrieve (default 20)", "default": 20},
            },
        },
    },
    {
        "name": "list_media_files",
        "description": "List media files (photos/documents) received from user.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "create_forum_topic",
        "description": "Create a new Telegram Forum Topic and optionally map it to an agent instance (leader only).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the new Forum Topic"},
                "instance": {"type": "string", "description": "Agent instance name to map this topic to (optional)"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "restart_team",
        "description": "Full restart: stop all agents, reload Python code and team.yaml, restart everything (leader only). Use after modifying any code or config.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]

# Leader-only tools
_LEADER_ONLY_TOOLS = {"send_to_instance", "create_forum_topic", "restart_team"}


def main() -> None:
    global _port, _instance, _role, _allowed_targets
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8470)
    parser.add_argument("--instance", default="unknown")
    parser.add_argument("--role", default="worker")
    parser.add_argument("--allowed-targets", default="")
    args = parser.parse_args()
    _port, _instance, _role = args.port, args.instance, args.role
    _allowed_targets = [t for t in args.allowed_targets.split(",") if t]

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = msg.get("method", "")
        params = msg.get("params", {})
        msg_id = msg.get("id")

        if method == "initialize":
            _respond(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "team-mcp", "version": "0.2.0"},
            })
        elif method == "tools/list":
            if _role == "leader":
                tools = _TOOLS
            else:
                tools = [t for t in _TOOLS if t["name"] not in _LEADER_ONLY_TOOLS]
            _respond(msg_id, {"tools": tools})
        elif method == "tools/call":
            result = _handle_tool(params.get("name", ""), params.get("arguments", {}))
            _respond(msg_id, {"content": [{"type": "text", "text": result}]})
        elif method == "notifications/initialized":
            pass
        else:
            _respond(msg_id, None, error={"code": -32601, "message": f"Unknown: {method}"})


if __name__ == "__main__":
    main()
