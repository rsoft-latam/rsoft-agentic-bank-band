"""Launch one Loan Committee peer connected to Band.

Usage: python -m committee.peer BankGatekeeper
"""

import asyncio
import logging
import os
import sys

from .common import load_credentials, load_env
from .roles import ROLES


async def main(agent_name: str) -> None:
    load_env()
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [{agent_name}] %(name)s %(levelname)s %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)

    from band import Agent
    from band.adapters import LangGraphAdapter
    from langchain_openai import ChatOpenAI

    role = ROLES[agent_name]
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(model=os.environ.get("COMMITTEE_LLM_MODEL", "gpt-4o-mini")),
        custom_section=role["prompt"],
        additional_tools=role["tools"],
    )

    agent_id, api_key = load_credentials(agent_name)
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    print(f"[{agent_name}] conectando a Band…", flush=True)
    await agent.run()


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ROLES:
        raise SystemExit(f"uso: python -m committee.peer <{'|'.join(ROLES)}>")
    asyncio.run(main(sys.argv[1]))
