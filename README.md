<div align="center">

# Agent Negotiation MCP

**MCP server for agent negotiation mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-agent-negotiation-mcp)](https://pypi.org/project/meok-agent-negotiation-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Agent Negotiation MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `propose_deal` | Propose a deal between two agents with terms and pricing. |
| `evaluate_offer` | Evaluate an offer using negotiation theory (BATNA, ZOPA, Nash). |
| `counter_offer` | Submit a counter-offer on an existing negotiation. |
| `run_auction` | Run a simulated auction. Bids as JSON: [{"bidder": "A", "amount": 100}, ...] |
| `negotiation_status` | Get status of a negotiation or list all active negotiations. |

## Installation

```bash
pip install meok-agent-negotiation-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agent-negotiation": {
      "command": "python",
      "args": ["-m", "meok_agent_negotiation_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 5 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
