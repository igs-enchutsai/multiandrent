"""HoYeah API MCP Server - provides query_hoyeah tool for natural language data queries."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


# Load .env from agent directory or project root
for env_path in [Path(".env"), Path("../../.env"), Path("../../../.env")]:
    if env_path.exists():
        load_dotenv(env_path)
        break

HOYEAH_API_BASE = os.getenv("HOYEAH_API_BASE", "")
HOYEAH_API_KEY = os.getenv("HOYEAH_API_KEY", "")


def query_hoyeah(question: str) -> str:
    """Send a natural language query to HoYeah API and return the response."""
    url = HOYEAH_API_BASE.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {HOYEAH_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "hermes-agent",
        "messages": [{"role": "user", "content": question}],
    }

    try:
        r = requests.post(url, json=data, headers=headers, timeout=600)
        r.raise_for_status()
        result = r.json()
        choices = result.get("choices", [])
        if choices:
            return choices[0]["message"]["content"]
        return "API 回覆為空"
    except requests.Timeout:
        return "錯誤：API 請求超時（600秒）"
    except requests.ConnectionError:
        return "錯誤：無法連線到 HoYeah API"
    except Exception as e:
        return f"錯誤：{e}"


# ─── JSON-RPC stdio MCP Server ───────────────────────────────────

TOOLS = [
    {
        "name": "query_hoyeah",
        "description": "查詢營運數據。直接用自然語言提問，例如：'CN今天營收多少'、'昨天全服DAU'、'本週付費率趨勢'",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "自然語言查詢問題",
                }
            },
            "required": ["question"],
        },
    }
]


def handle_request(req: dict) -> dict:
    """Handle a JSON-RPC request."""
    method = req.get("method", "")
    req_id = req.get("id")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "hoyeah-api",
                    "version": "1.0.0",
                },
            },
        }

    if method == "notifications/initialized":
        return None  # No response for notifications

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS},
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name == "query_hoyeah":
            question = arguments.get("question", "")
            if not question:
                content = "錯誤：請提供查詢問題"
            else:
                content = query_hoyeah(question)

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": content}],
                    "isError": False,
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
        }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def main() -> None:
    """Run the MCP server on stdio."""
    sys.stderr.write("HoYeah MCP Server started\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        response = handle_request(req)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
