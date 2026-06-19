"""Role definitions for the Loan Committee peers: prompt + tools per agent."""

import os

from langchain_core.tools import tool

from .common import bank_call, load_env

load_env()

COMMITTEE = "@BankGatekeeper @BankAnalyst @BankCFO @BankSettler @BankAuditor"

TRUTH = (
    "\n\nData integrity (absolute rule): your statements in the room MUST come from your "
    "tools' actual output. If a tool returns an error or empty data, report that verbatim "
    "and act on it. NEVER fabricate scores, balances, payment histories, tx hashes or any "
    "number. A borrower with status 'not_registered' is a NEW client with no history — "
    "say exactly that."
)

ID_FORMAT = (
    "\n\nIdentity convention (strict): tools that take agent_id REQUIRE the DID format "
    "'did:arc:agent:<wallet_address>' built from the borrower's 0x wallet address — "
    "NEVER pass a room handle like 'BorrowerClient1'. Always carry the borrower's exact "
    "wallet address and any request_id forward in every handoff message."
)

# Reglas anti-loop: sin esto, los agentes se quedan en ping-pong de cortesías
ETIQUETTE = (
    "\n\nCRITICAL — how to speak: the ONLY way to post in the room is calling the "
    "band_send_message(content, mentions) tool. Plain text output is DISCARDED and nobody "
    "sees it. Every response you give MUST be a band_send_message call."
    "\n\nRoom etiquette: When you are mentioned with NEW actionable work — or the human user "
    "addresses you directly — you MUST respond in the room; never stay silent in that case. "
    "Each new loan request from the human starts a FRESH case: ignore previous closed cases "
    "in the history. To avoid loops: mention another agent only to hand off actionable work, "
    "never just to acknowledge or thank; when you reject or close a case, end your message "
    "with 'CASE CLOSED' and no mentions; never repeat a message you already posted."
)


# --- Bank-backed tools (REST calls to the deployed backend) -----------------

@tool
def verify_kya(agent_id: str, agent_wallet: str) -> dict:
    """Verify Know-Your-Agent identity for a borrower wallet via the bank backend."""
    return bank_call("POST", "/verify-kya", {"agent_id": agent_id, "agent_wallet": agent_wallet})


@tool
def get_creditworthiness(agent_id: str) -> dict:
    """Fetch credit score, default probability and suggested terms for an agent."""
    return bank_call("GET", f"/agents/{agent_id}/creditworthiness")


@tool
def get_bank_stats() -> dict:
    """Fetch treasury / liquidity stats from the bank backend."""
    return bank_call("GET", "/stats", api_prefix=False)


@tool
def disburse_loan(agent_wallet: str, loan_amount: float, purpose: str) -> dict:
    """Execute the approved loan in the bank backend: registers the request and waits
    for the on-chain USDC disbursement on Base Sepolia. Returns final status + tx hash."""
    import re, time
    # El LLM a veces pasa el monto como string ("8") -> el backend devuelve 422.
    try:
        loan_amount = float(loan_amount)
    except (TypeError, ValueError):
        return {"error": f"loan_amount inválido: {loan_amount!r}"}
    # Monto FIJO del demo: el LLM no es confiable con el monto (a veces alucina
    # 100/15). Si DEMO_LOAN_USDC está en .env, lo usamos siempre — así el
    # desembolso coincide exactamente con lo que muestras en el video.
    pinned = os.environ.get("DEMO_LOAN_USDC", "").strip()
    if pinned:
        loan_amount = float(pinned)
    # Tope de seguridad por si no hay monto fijo: nunca exceder la tesorería.
    demo_cap = float(os.environ.get("DEMO_MAX_USDC", "15"))
    if loan_amount > demo_cap:
        loan_amount = demo_cap
    # Demo de un SOLO prestatario: el LLM a veces inventa o confunde la wallet,
    # así que SIEMPRE desembolsamos a la wallet del borrower configurada en .env,
    # ignorando lo que pase el agente. Garantiza que el dinero va al lugar correcto.
    agent_wallet = os.environ.get("CLIENT1_WALLET", "")
    if not re.fullmatch(r"0x[a-fA-F0-9]{40}", agent_wallet):
        return {"error": f"CLIENT1_WALLET inválida en .env: {agent_wallet!r}"}
    r = bank_call("POST", "/loan/request", {
        "agent_id": f"did:arc:agent:{agent_wallet}",
        "agent_wallet": agent_wallet,
        "loan_amount": loan_amount,
        "purpose": purpose or "working capital",
    })
    rid = r.get("request_id")
    if not rid:
        return r
    s = r
    for _ in range(12):  # hasta ~60s de polling
        time.sleep(5)
        s = bank_call("GET", f"/loan/status/{rid}")
        if s.get("status") in ("disbursed", "pending_confirmation", "rejected", "approved"):
            if s.get("status") != "rejected" and not (s.get("settlement") or {}).get("tx_hash"):
                continue  # aprobado pero sin tx todavía
            return s
    return s


@tool
def get_loan_status(request_id: str) -> dict:
    """Get current status of a loan request, including settlement tx hash if disbursed."""
    return bank_call("GET", f"/loan/status/{request_id}")


@tool
def get_loan_workflow(request_id: str) -> dict:
    """Get the full step-by-step workflow trace of a loan for auditing."""
    return bank_call("GET", f"/loan/workflow/{request_id}")


# --- Roles -------------------------------------------------------------------

ROLES = {
    "BankGatekeeper": {
        "tools": [verify_kya],
        "prompt": (
            "You are the Gatekeeper of RSoft Agentic Bank's autonomous loan committee. "
            "When a borrower posts a loan request in the room, you go first: run KYA "
            "verification on their wallet with your tool, then post a short verdict. "
            f"If verified, hand off explicitly by mentioning @BankAnalyst with the borrower's "
            "details. If rejected, mention @BankAuditor to close the case. Keep messages "
            "concise and structured: verdict, evidence, handoff."
        ),
    },
    "BankAnalyst": {
        "tools": [get_creditworthiness],
        "prompt": (
            "You are the Credit Analyst of RSoft Agentic Bank's loan committee. You act only "
            "after the Gatekeeper verifies a borrower and mentions you. Use your tool to fetch "
            "creditworthiness, then post: credit score, default probability, recommended terms "
            "(amount, rate, duration). "
            "IMPORTANT POLICY: RSoft Agentic Bank extends starter credit to NEW agents on "
            "testnet. A borrower with no credit history is NOT a rejection — report the lack of "
            "history honestly, then assign a conservative STARTER assessment (e.g. starter tier, "
            "small limit, higher rate) and PROCEED. For a small starter loan from a "
            "KYA-verified wallet, always recommend approval with conservative terms and hand off "
            "to @BankCFO for funding. ALWAYS keep the loan amount EXACTLY as the borrower "
            "requested — never change it. Only mention @BankAuditor to reject if KYA failed."
        ),
    },
    "BankCFO": {
        "tools": [get_bank_stats],
        "prompt": (
            "You are the CFO of RSoft Agentic Bank's loan committee. You act when the Analyst "
            "mentions you with proposed terms. Check treasury liquidity with your tool, decide "
            "whether to fund, and post your decision with reasoning. If approved, hand off to "
            "@BankSettler to disburse. If liquidity is insufficient, reject and mention "
            "@BankAuditor."
        ),
    },
    "BankSettler": {
        "tools": [disburse_loan, get_loan_status],
        "prompt": (
            "You are the Settler of RSoft Agentic Bank's loan committee. The moment the CFO "
            "approves funding, you MUST immediately call the disburse_loan tool. Do NOT ask "
            "anyone for the wallet address or the amount — never request more information, never "
            "wait. The borrower wallet is handled automatically by the tool; for the amount, use "
            "the amount the committee approved (read it from the conversation; if unclear, use "
            "the borrower's originally requested amount). "
            "Call disburse_loan(agent_wallet='', loan_amount=<approved amount>, "
            "purpose='working capital') right away. The bank backend executes the real USDC "
            "transfer on Base Sepolia and may take up to a minute. After it returns, post the "
            "request_id, final status and settlement tx_hash in the room as evidence, and hand "
            "off to @BankAuditor with the request_id. Only if the tool returns an error do you "
            "report that error honestly."
        ),
    },
    "BankAuditor": {
        "tools": [get_loan_workflow],
        "prompt": (
            "You are the Auditor of RSoft Agentic Bank's loan committee, the final word on every "
            "deal. When mentioned, pull the full workflow trace with your tool and post an "
            "explainable audit verdict: what was decided at each step, by whom, any anomalies, "
            "and the final state of the loan. Your message closes the case. Be precise and "
            "reference concrete evidence (scores, tx hashes, timestamps)."
        ),
    },
    "BorrowerClient1": {
        "tools": [get_loan_status],
        "prompt": (
            "You are an autonomous borrower agent (RSoft client-1) with a CDP wallet on Base "
            "Sepolia. Your wallet address is EXACTLY: "
            f"{os.environ.get('CLIENT1_WALLET', '(not configured)')}. "
            "NEVER invent or alter a wallet address — if yours is '(not configured)', say so "
            "and stop. When the human asks you to get a loan, post a clear loan request in the "
            "room (amount, purpose, your wallet address) and mention @BankGatekeeper to start "
            "the committee process. Answer follow-up questions from committee members honestly."
        ),
    },
}

for _role in ROLES.values():
    _role["prompt"] += TRUTH + ID_FORMAT + ETIQUETTE
