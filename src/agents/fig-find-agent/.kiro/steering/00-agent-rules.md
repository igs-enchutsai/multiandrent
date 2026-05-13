---
inclusion: always
---

# Agent Core Rules

## 1. Progress Reporting (Mandatory)

Report progress every 5 minutes during task execution.

### When to Report
1. Task start: "Starting XXX"
2. Every 5 minutes: current progress
3. On error: immediately
4. On completion: result summary

## 2. Coding Principles

- Think before coding. State assumptions explicitly.
- Simplicity first. Minimum code to solve the problem.
- Surgical edits. Only change what is necessary.
- Goal-driven. Define success criteria, iterate until verified.

## 3. Error Handling

- Retry up to 3 times with exponential backoff
- Use `log_to_leader()` for internal errors (not visible to user)
- Never show raw stack traces to users
- Always provide alternative approaches when blocked

## 4. Telegram Reply Style

- Concise: max 300 chars per message
- Result-oriented: conclusion first, then reasoning
- Use emoji prefixes: success, warning, progress, info
- Never paste raw stdout, diffs, or JSON to users
