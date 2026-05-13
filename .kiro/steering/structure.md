---
inclusion: always
---

# Project Structure

```
kiro-multi-agent/
+-- src/kiro_multi_agent/      # Main package (src layout)
+-- scripts/                   # Startup & management scripts
+-- templates/agent-template/  # New agent template
+-- cmd/watchdog/              # Go watchdog binary
+-- .kiro/steering/            # Global steering rules
+-- examples/                  # Example configs
+-- tests/                     # Tests (pytest)
+-- pyproject.toml             # Build config
+-- team.yaml                  # Local team config (not in VCS)
```

## Conventions
- src layout: all source in src/kiro_multi_agent/
- One module, one responsibility (no utils.py)
- Each agent has independent .kiro/ config
