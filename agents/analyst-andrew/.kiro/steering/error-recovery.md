---
inclusion: always
---

# Error Recovery

| Level | Definition | Action |
|-------|-----------|--------|
| L1 Minor | Single operation failed | Auto-retry (max 3) |
| L2 Medium | Dependency temporarily unavailable | Wait 30s, notify leader |
| L3 Severe | Core function broken | Notify leader + user, stop |

## Retry Strategy
- Attempt 1: wait 3s
- Attempt 2: wait 10s
- Attempt 3: wait 30s
- All failed: escalate to L2
