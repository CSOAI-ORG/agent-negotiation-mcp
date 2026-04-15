# Agent Negotiation MCP Server

> By [MEOK AI Labs](https://meok.ai) — Multi-agent negotiation framework with deal evaluation and auction support

## Installation

```bash
pip install agent-negotiation-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install agent-negotiation-mcp
```

## Tools

### `propose_deal`
Propose a deal between two agents with terms and pricing.

**Parameters:**
- `proposer` (str): Proposing agent
- `receiver` (str): Receiving agent
- `terms` (str): Deal terms
- `price` (float): Proposed price
- `deadline_hours` (int): Deadline in hours (default 24)

### `evaluate_offer`
Evaluate an offer using negotiation theory (BATNA, ZOPA, Nash bargaining solution).

**Parameters:**
- `price` (float): Offered price
- `reservation_price` (float): Your maximum acceptable price
- `best_alternative` (float): Best alternative to negotiated agreement
- `urgency` (float): Urgency factor 0-1

### `counter_offer`
Submit a counter-offer on an existing negotiation. Tracks convergence.

**Parameters:**
- `deal_id` (str): Deal identifier
- `agent` (str): Agent making counter-offer
- `new_price` (float): New proposed price
- `new_terms` (str): Updated terms

### `run_auction`
Run a simulated auction (English, Vickrey, or Dutch).

**Parameters:**
- `item` (str): Item being auctioned
- `starting_price` (float): Starting price
- `bids` (str): JSON array of bid objects
- `auction_type` (str): Auction type — 'english', 'vickrey', 'dutch'

### `negotiation_status`
Get status of a negotiation or list all active negotiations.

**Parameters:**
- `deal_id` (str): Deal identifier (empty for all)

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
