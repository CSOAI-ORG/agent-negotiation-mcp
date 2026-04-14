#!/usr/bin/env python3
"""Agent Negotiation MCP — MEOK AI Labs. Multi-agent negotiation protocols, deal evaluation, and strategy."""

import sys, os
sys.path.insert(0, os.path.expanduser('~/clawd/meok-labs-engine/shared'))
from auth_middleware import check_access

import json, hashlib, time, math
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP

FREE_DAILY_LIMIT = 15
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("agent-negotiation", instructions="Multi-agent negotiation framework. Propose deals, evaluate offers, run auctions, and optimize outcomes. By MEOK AI Labs.")

_NEGOTIATIONS: dict[str, dict] = {}
_OFFERS: list[dict] = []


@mcp.tool()
def propose_deal(proposer: str, receiver: str, terms: str, price: float = 0, deadline_hours: int = 24, api_key: str = "") -> str:
    """Propose a deal between two agents with terms and pricing."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    deal_id = f"deal-{hashlib.sha256(f'{proposer}{receiver}{time.time_ns()}'.encode()).hexdigest()[:12]}"
    now = datetime.now(timezone.utc)

    deal = {
        "deal_id": deal_id,
        "proposer": proposer,
        "receiver": receiver,
        "terms": terms,
        "price": price,
        "status": "proposed",
        "created_at": now.isoformat(),
        "deadline": (now.replace(hour=now.hour + deadline_hours) if deadline_hours < 24 else now).isoformat(),
        "rounds": 1,
        "history": [{"round": 1, "action": "propose", "agent": proposer, "price": price, "terms": terms}],
    }
    _NEGOTIATIONS[deal_id] = deal

    return {
        "deal_id": deal_id,
        "status": "proposed",
        "from": proposer,
        "to": receiver,
        "price": price,
        "suggested_counter": round(price * 0.85, 2),
        "fair_range": {"low": round(price * 0.75, 2), "high": round(price * 1.1, 2)},
    }


@mcp.tool()
def evaluate_offer(price: float, reservation_price: float, best_alternative: float = 0, urgency: float = 0.5, api_key: str = "") -> str:
    """Evaluate an offer using negotiation theory (BATNA, ZOPA, Nash)."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    batna = best_alternative if best_alternative > 0 else reservation_price * 0.7
    zopa_exists = price <= reservation_price
    surplus = reservation_price - price if zopa_exists else 0

    # Nash bargaining solution
    nash_price = (price + reservation_price) / 2

    # Urgency-adjusted recommendation
    urgency = max(0, min(1, urgency))
    accept_threshold = reservation_price * (1 - 0.15 * (1 - urgency))

    if price <= accept_threshold:
        recommendation = "ACCEPT"
        confidence = min(100, round((1 - price / reservation_price) * 200))
    elif price <= reservation_price:
        recommendation = "COUNTER"
        counter_price = round(nash_price * (1 - 0.05 * urgency), 2)
        confidence = 60
    else:
        recommendation = "REJECT"
        confidence = min(100, round((price / reservation_price - 1) * 200))

    return {
        "offer_price": price,
        "reservation_price": reservation_price,
        "batna": round(batna, 2),
        "zopa_exists": zopa_exists,
        "surplus": round(surplus, 2),
        "nash_solution": round(nash_price, 2),
        "recommendation": recommendation,
        "confidence": confidence,
        "suggested_counter": round(nash_price, 2) if recommendation == "COUNTER" else None,
        "urgency_factor": urgency,
    }


@mcp.tool()
def counter_offer(deal_id: str, agent: str, new_price: float, new_terms: str = "", api_key: str = "") -> str:
    """Submit a counter-offer on an existing negotiation."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    if deal_id not in _NEGOTIATIONS:
        return {"error": "Deal not found"}

    deal = _NEGOTIATIONS[deal_id]
    deal["rounds"] += 1
    deal["price"] = new_price
    if new_terms:
        deal["terms"] = new_terms
    deal["status"] = "counter-offered"
    deal["history"].append({
        "round": deal["rounds"],
        "action": "counter",
        "agent": agent,
        "price": new_price,
        "terms": new_terms or deal["terms"],
    })

    # Calculate convergence
    prices = [h["price"] for h in deal["history"]]
    if len(prices) >= 2:
        convergence = round(abs(prices[-1] - prices[-2]) / max(prices) * 100, 1)
    else:
        convergence = 100

    return {
        "deal_id": deal_id,
        "round": deal["rounds"],
        "new_price": new_price,
        "convergence_pct": convergence,
        "likely_settlement": round(sum(prices[-2:]) / 2, 2) if len(prices) >= 2 else new_price,
        "status": "counter-offered",
    }


@mcp.tool()
def run_auction(item: str, starting_price: float, bids: str, auction_type: str = "english", api_key: str = "") -> str:
    """Run a simulated auction. Bids as JSON: [{"bidder": "A", "amount": 100}, ...]"""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    try:
        bid_list = json.loads(bids)
    except json.JSONDecodeError:
        return {"error": "Invalid bids JSON. Format: [{\"bidder\": \"A\", \"amount\": 100}]"}

    if not bid_list:
        return {"error": "No bids provided"}

    auction_type = auction_type.lower()

    if auction_type == "english":
        # Highest bid wins
        sorted_bids = sorted(bid_list, key=lambda b: b["amount"], reverse=True)
        winner = sorted_bids[0]
        price = winner["amount"]
    elif auction_type == "vickrey":
        # Highest bid wins, pays second-highest price
        sorted_bids = sorted(bid_list, key=lambda b: b["amount"], reverse=True)
        winner = sorted_bids[0]
        price = sorted_bids[1]["amount"] if len(sorted_bids) > 1 else winner["amount"]
    elif auction_type == "dutch":
        # First bid at or above starting price wins
        winner = None
        price = starting_price
        for bid in bid_list:
            if bid["amount"] >= starting_price:
                winner = bid
                price = bid["amount"]
                break
        if not winner:
            return {"item": item, "status": "no_sale", "reason": "No bid met the starting price"}
    else:
        return {"error": f"Unknown auction type. Supported: english, vickrey, dutch"}

    return {
        "item": item,
        "auction_type": auction_type,
        "winner": winner["bidder"],
        "winning_bid": winner["amount"],
        "price_paid": price,
        "starting_price": starting_price,
        "total_bids": len(bid_list),
        "bid_spread": round(max(b["amount"] for b in bid_list) - min(b["amount"] for b in bid_list), 2),
    }


@mcp.tool()
def negotiation_status(deal_id: str = "", api_key: str = "") -> str:
    """Get status of a negotiation or list all active negotiations."""
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err

    if deal_id:
        if deal_id not in _NEGOTIATIONS:
            return {"error": "Deal not found"}
        return _NEGOTIATIONS[deal_id]

    active = [{"deal_id": did, "parties": f"{d['proposer']} ↔ {d['receiver']}", "price": d["price"], "rounds": d["rounds"], "status": d["status"]} for did, d in _NEGOTIATIONS.items()]
    return {"active_negotiations": active, "total": len(active)}


if __name__ == "__main__":
    mcp.run()
