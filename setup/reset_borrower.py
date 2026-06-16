"""Demo helper: close any stuck active loans for the borrower wallet so a
fresh committee run isn't blocked by the one-active-loan rule. Marks them
'repaid'. Run from the bank repo's venv:

  cd ../rsoft-latam-agentic-bank && .venv/bin/python ../rsoft-band-loan-committee/setup/reset_borrower.py
"""

import asyncio

WALLET = "0xd4582736738b47233f675c99d7Bb79281f8f1B2f"


async def main():
    from app.database import db

    agent = await db.agents.get_by_wallet(WALLET) or await db.agents.get_by_wallet(WALLET.lower())
    if not agent:
        print("borrower agent no encontrado en BD")
        return
    active = await db.loans.get_active_by_agent(agent.id)
    print(f"activos: {len(active)}")
    for loan in active:
        await db.loans.update_status(loan.request_id, "repaid", current_step="completed", progress=1.0)
        print(f"  cerrado {loan.request_id} ({loan.status} -> repaid)")
    print("listo")


if __name__ == "__main__":
    asyncio.run(main())
