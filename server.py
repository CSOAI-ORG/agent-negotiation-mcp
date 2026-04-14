#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("agent-negotiation-mcp")
@mcp.tool(name="propose_deal")
async def propose_deal(agent_a: str, agent_b: str, offer: dict, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    return {"from": agent_a, "to": agent_b, "offer": offer, "status": "proposed", "counter_offer_suggested": {"price": offer.get("price", 0) * 0.9}}
    return {"from": agent_a, "to": agent_b, "offer": offer, "status": "proposed", "counter_offer_suggested": {"price": offer.get("price", 0) * 0.9}}
@mcp.tool(name="evaluate_offer")
async def evaluate_offer(offer: dict, reservation_price: float, api_key: str = "") -> str:
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}

    price = offer.get("price", 0)
    accepted = price <= reservation_price
    return {"acceptable": accepted, "price": price, "reservation": reservation_price, "recommendation": "Accept" if accepted else "Counter"}
if __name__ == "__main__":
    mcp.run()
