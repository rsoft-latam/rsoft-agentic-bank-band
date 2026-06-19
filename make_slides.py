"""Generate the submission slide deck as a PDF (run with anaconda python)."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch

NAVY = "#0B1F3A"
BLUE = "#2D7FF9"
TEAL = "#15B8A6"
GOLD = "#F2B705"
WHITE = "#FFFFFF"
GREY = "#8A99AD"
LIGHT = "#E8EEF6"

W, H = 13.333, 7.5  # 16:9


def slide(pdf, bg=NAVY):
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=bg, zorder=0))
    return fig, ax


def text(ax, x, y, s, size, color=WHITE, weight="normal", ha="left", va="center", family="DejaVu Sans", style="normal"):
    ax.text(x, y, s, fontsize=size, color=color, weight=weight, ha=ha, va=va,
            transform=ax.transAxes, family=family, style=style, zorder=5)


def chip(ax, x, y, s, color=BLUE, tcolor=WHITE, size=13):
    ax.text(x, y, s, fontsize=size, color=tcolor, weight="bold", ha="left", va="center",
            transform=ax.transAxes, zorder=6,
            bbox=dict(boxstyle="round,pad=0.5", fc=color, ec="none"))


pdf = PdfPages("RSoft_Band_Slides.pdf")

# ---- Slide 1: Title ----
fig, ax = slide(pdf)
ax.add_patch(plt.Rectangle((0, 0.0), 1, 0.06, color=TEAL))
ax.add_patch(plt.Rectangle((0, 0.94), 1, 0.06, color=BLUE))
chip(ax, 0.07, 0.80, "  BAND OF AGENTS HACKATHON  ", color=BLUE)
text(ax, 0.07, 0.62, "RSoft Agentic Bank", 60, WHITE, "bold")
text(ax, 0.07, 0.50, "A bank run by AI agents — on Band", 30, TEAL, "bold")
text(ax, 0.07, 0.36, "Six AI agents collaborate in a shared chat room to verify, approve,", 19, LIGHT)
text(ax, 0.07, 0.31, "and disburse real USDC loans on-chain — every decision recorded.", 19, LIGHT)
text(ax, 0.07, 0.16, "Track 3  ·  Regulated & High-Stakes Workflows", 17, GOLD, "bold")
pdf.savefig(fig); plt.close(fig)

# ---- Slide 2: The Problem ----
fig, ax = slide(pdf)
chip(ax, 0.07, 0.88, "  THE PROBLEM  ", color=GOLD, tcolor=NAVY)
text(ax, 0.07, 0.72, "One AI can't run a bank", 44, WHITE, "bold")
text(ax, 0.07, 0.57, "A bank cannot let a single AI approve loans on its own.", 22, LIGHT)
text(ax, 0.07, 0.50, "It needs a committee — separated roles, checks and balances,", 22, LIGHT)
text(ax, 0.07, 0.43, "and a clear record of who decided what.", 22, LIGHT)
text(ax, 0.07, 0.28, "But today, most AI agents work alone — locked in one app,", 20, GREY)
text(ax, 0.07, 0.22, "one framework, unable to talk to each other or to humans.", 20, GREY)
pdf.savefig(fig); plt.close(fig)

# ---- Slide 3: The Solution ----
fig, ax = slide(pdf)
chip(ax, 0.07, 0.88, "  THE SOLUTION  ", color=TEAL, tcolor=NAVY)
text(ax, 0.07, 0.74, "An autonomous credit committee", 40, WHITE, "bold")
text(ax, 0.07, 0.62, "Six specialized AI agents collaborate through Band — a shared", 21, LIGHT)
text(ax, 0.07, 0.555, "chat room for AI. They hand off work by @mentioning each other.", 21, LIGHT)
flow = ["Borrower", "Gatekeeper", "Analyst", "CFO", "Settler", "Auditor"]
x = 0.07
for i, name in enumerate(flow):
    ax.text(x, 0.36, name, fontsize=15, color=WHITE, weight="bold", ha="left", va="center",
            transform=ax.transAxes, zorder=6,
            bbox=dict(boxstyle="round,pad=0.45", fc=BLUE if i % 2 == 0 else TEAL, ec="none"))
    x += 0.135 + 0.012
    if i < len(flow) - 1:
        ax.text(x - 0.018, 0.36, "→", fontsize=18, color=GOLD, ha="center", va="center", transform=ax.transAxes, zorder=6)
text(ax, 0.07, 0.20, "Turn Band off and the flow stops — the disbursement happens", 18, GREY)
text(ax, 0.07, 0.15, "because the CFO approved it in the room. Band is the coordination, not a wrapper.", 18, GREY)
pdf.savefig(fig); plt.close(fig)

# ---- Slide 4: Architecture ----
fig, ax = slide(pdf)
chip(ax, 0.07, 0.90, "  ARCHITECTURE — TWO LAYERS  ", color=BLUE)
# Layer 1 box
ax.add_patch(FancyBboxPatch((0.07, 0.58), 0.86, 0.22, boxstyle="round,pad=0.01",
             fc="#13294B", ec=TEAL, lw=2, transform=ax.transAxes, zorder=3))
text(ax, 0.10, 0.74, "BAND  —  the coordination layer", 22, TEAL, "bold")
text(ax, 0.10, 0.665, "A shared chat room. Agents discover each other and hand off work via @mention.", 17, LIGHT)
text(ax, 0.10, 0.615, "Each agent = a LangGraph ReAct loop (GPT-4o + tools), connected via band-sdk.", 16, GREY)
# arrow
ax.text(0.5, 0.52, "↓  agents call the bank over REST", fontsize=15, color=GOLD, ha="center", va="center", transform=ax.transAxes, weight="bold")
# Layer 2 box
ax.add_patch(FancyBboxPatch((0.07, 0.22), 0.86, 0.22, boxstyle="round,pad=0.01",
             fc="#13294B", ec=BLUE, lw=2, transform=ax.transAxes, zorder=3))
text(ax, 0.10, 0.38, "RSoft Agentic Bank backend  —  the lending logic", 22, BLUE, "bold")
text(ax, 0.10, 0.305, "FastAPI + LangGraph + Supabase. Runs KYA, credit scoring, treasury checks,", 17, LIGHT)
text(ax, 0.10, 0.255, "and the real ERC-20 USDC transfer on Base Sepolia.", 16, GREY)
text(ax, 0.07, 0.12, "Band moves the messages between agents · the bank API does the work · the agent is the bridge.", 16, WHITE, "bold")
pdf.savefig(fig); plt.close(fig)

# ---- Slide 5: The six agents ----
fig, ax = slide(pdf)
chip(ax, 0.07, 0.90, "  THE SIX AGENTS  ", color=TEAL, tcolor=NAVY)
rows = [
    ("Borrower", "Requests a loan and signs terms"),
    ("Gatekeeper", "KYA / identity verification, recruits the committee"),
    ("Analyst", "Credit score, default probability, recommended terms"),
    ("CFO", "Approves or denies funding against treasury liquidity"),
    ("Settler", "Executes the real USDC disbursement on Base Sepolia"),
    ("Auditor", "Explainable verdict over the full workflow (audit trail)"),
]
y = 0.78
for name, desc in rows:
    ax.text(0.09, y, name, fontsize=18, color=NAVY, weight="bold", ha="left", va="center",
            transform=ax.transAxes, zorder=6,
            bbox=dict(boxstyle="round,pad=0.35", fc=GOLD, ec="none"))
    text(ax, 0.30, y, desc, 18, LIGHT)
    y -= 0.115
pdf.savefig(fig); plt.close(fig)

# ---- Slide 6: Proof ----
fig, ax = slide(pdf)
chip(ax, 0.07, 0.90, "  PROOF — REAL MONEY ON-CHAIN  ", color=GOLD, tcolor=NAVY)
text(ax, 0.07, 0.74, "Not simulated. Verifiable.", 40, WHITE, "bold")
text(ax, 0.07, 0.60, "A full committee run disburses real USDC on Base Sepolia,", 21, LIGHT)
text(ax, 0.07, 0.535, "and the Auditor closes each case with the score, the approval,", 21, LIGHT)
text(ax, 0.07, 0.47, "the settlement tx hash and the block number.", 21, LIGHT)
ax.add_patch(FancyBboxPatch((0.07, 0.20), 0.86, 0.16, boxstyle="round,pad=0.01",
             fc="#13294B", ec=TEAL, lw=2, transform=ax.transAxes, zorder=3))
text(ax, 0.10, 0.31, "Example disbursement — BaseScan (Base Sepolia)", 17, TEAL, "bold")
text(ax, 0.10, 0.255, "0xabc25ce0bae88d2b2735b0e59b51bd71334fa3bb3089e7f14da0466556c3a24e", 14, WHITE, family="DejaVu Sans Mono")
text(ax, 0.10, 0.215, "5 USDC  ·  treasury -> borrower  ·  status: SUCCESS", 15, GOLD, "bold")
pdf.savefig(fig); plt.close(fig)

# ---- Slide 7: Why it matters ----
fig, ax = slide(pdf)
chip(ax, 0.07, 0.90, "  WHY IT MATTERS  ", color=BLUE)
text(ax, 0.07, 0.76, "The future is a team of agents", 40, WHITE, "bold")
bullets = [
    ("Application of tech", "Band is the real coordination layer for handoffs."),
    ("Business value", "Traceable, role-separated credit for regulated lending."),
    ("Originality", "Real on-chain money, cross-layer Band <-> LangGraph."),
    ("Presentation", "A verifiable on-chain transaction backs the demo."),
]
y = 0.62
for head, body in bullets:
    ax.text(0.09, y, head, fontsize=16, color=NAVY, weight="bold", ha="left", va="center",
            transform=ax.transAxes, zorder=6, bbox=dict(boxstyle="round,pad=0.3", fc=TEAL, ec="none"))
    text(ax, 0.37, y, body, 16, LIGHT)
    y -= 0.11
text(ax, 0.07, 0.13, "Not one AI doing everything — a team of specialized agents running a bank.", 19, GOLD, "bold")
text(ax, 0.07, 0.07, "Band (band-sdk) · LangGraph · GPT-4o · FastAPI · Supabase · Base Sepolia · USDC (Circle)", 13, GREY)
pdf.savefig(fig); plt.close(fig)

pdf.close()
print("OK -> RSoft_Band_Slides.pdf")
