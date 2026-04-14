#!/usr/bin/env python3
import json
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("agent-negotiation-mcp")
@mcp.tool(name="propose_deal")
async def propose_deal(agent_a: str, agent_b: str, offer: dict) -> str:
    return json.dumps({"from": agent_a, "to": agent_b, "offer": offer, "status": "proposed", "counter_offer_suggested": {"price": offer.get("price", 0) * 0.9}})
@mcp.tool(name="evaluate_offer")
async def evaluate_offer(offer: dict, reservation_price: float) -> str:
    price = offer.get("price", 0)
    accepted = price <= reservation_price
    return json.dumps({"acceptable": accepted, "price": price, "reservation": reservation_price, "recommendation": "Accept" if accepted else "Counter"})
if __name__ == "__main__":
    mcp.run()
