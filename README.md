# RSoft Agentic Bank — Loan Committee on Band

**An autonomous credit committee where six AI agents collaborate through [Band](https://www.band.ai) to originate, approve and disburse real USDC loans on-chain.**

Built for the **Band of Agents Hackathon** · Track 3 (Regulated & High-Stakes Workflows).

> A bank can't let a single AI approve loans on its own. It needs a committee with
> separated roles — verification, risk, treasury, settlement, audit — and a record of
> who decided what. This project runs exactly that committee as a group of agents
> talking in a Band room, where the deliberation *is* the coordination layer and *is*
> the audit trail.

---

## Proof it works

A complete run disbursed **8 USDC on Base Sepolia**, driven entirely by the agents'
conversation in Band:

🔗 [`0xdc01cab8…a2d694eb` on BaseScan](https://sepolia.basescan.org/tx/0xdc01cab8c43fe3d0657b6e3df67b83fc364dc754d9fd65a0e30ed280a2d694eb)

Turn off Band and the flow halts — the settlement happens *because* the CFO approved
it in the room. Band is the collaboration layer, not a notification channel.

---

## The two-layer architecture

```
┌──────────────────────── BAND (the coordination layer) ────────────────────────┐
│  A shared chat room. Agents hand off work by @mentioning each other.           │
│                                                                                │
│  BorrowerClient1 ─▶ Gatekeeper ─▶ Analyst ─▶ CFO ─▶ Settler ─▶ Auditor          │
│      (request)      (KYA)        (risk)    (fund)  (disburse)  (audit)          │
└───────────────────────────────────┬────────────────────────────────────────────┘
                                     │  each agent calls the bank's REST API as a tool
                                     ▼
┌──────────────────── RSoft Agentic Bank backend (the lending logic) ────────────┐
│  FastAPI + LangGraph + Supabase. Runs KYA, credit scoring, treasury checks and │
│  the real ERC-20 USDC transfer on Base Sepolia. Lives in a separate private    │
│  repo; this layer only consumes its REST endpoints.                            │
└────────────────────────────────────────────────────────────────────────────────┘
```

- **Band moves the messages between agents.** Routing is by `@mention` — only the
  mentioned agent receives a message.
- **The bank API does the financial work.** This repo never embeds bank logic; the
  agents are external clients of its REST API.
- **The agent is the bridge.** It hears the room over a WebSocket, calls the bank's
  REST API, and posts the result back to the room.

Each agent is a LangGraph ReAct loop (LLM + tools) wired to Band through the
[`band-sdk`](https://github.com/thenvoi/thenvoi-sdk-python) `LangGraphAdapter`.

---

## The six agents

| Agent             | Role in the room                                            | Bank tool it calls       |
|-------------------|-------------------------------------------------------------|--------------------------|
| `BorrowerClient1` | Autonomous borrower; requests a loan, signs terms           | `request_loan`           |
| `BankGatekeeper`  | KYA / identity verification, recruits the committee         | `verify_kya`             |
| `BankAnalyst`     | Credit score, default probability, recommended terms        | `get_creditworthiness`   |
| `BankCFO`         | Approves/denies funding against treasury liquidity          | `get_bank_stats`         |
| `BankSettler`     | Executes the real USDC disbursement on Base Sepolia          | `disburse_loan`          |
| `BankAuditor`     | Explainable verdict over the full workflow (audit trail)    | `get_loan_workflow`      |

---

## Run it

Requires Python 3.11+, a running RSoft Agentic Bank backend, and a Band account.

```bash
python -m venv .venv && .venv/bin/pip install "band-sdk[langgraph]" langchain-openai

cp .env.example .env          # fill in your keys
python setup/provision.py     # registers the 6 agents on Band (run once)
./start_detached.sh           # launches the 6 peers (staggered, detached)
```

Then, in your Band room, address the committee:

```
@BankGatekeeper New case: borrower 0x… requests 8 USDC for working capital. Please verify.
```

Watch the committee deliberate, approve, and settle on-chain.

---

## How it maps to the judging criteria

- **Application of Technology** — Band is the real coordination layer: handoffs, shared
  context and task state all flow through `@mention` routing; the settlement only fires
  because the approval happened in the room.
- **Business Value** — a traceable, role-separated credit committee for a regulated
  lending workflow, with an explainable audit record (EU AI Act-style).
- **Originality** — real on-chain money movement, cross-layer (Band ↔ LangGraph bank),
  dynamic peer recruitment.
- **Presentation** — a verifiable on-chain transaction backs the demo, not just text.

## License

MIT
