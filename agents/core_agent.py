"""Lightweight runner for the NewsNexus core AI agent workflow.

This module is intentionally simple so support/maintenance teams can run a
single orchestration cycle locally without external infrastructure.
"""

import asyncio
import logging

from agents.orchestrator import AgentOrchestrator
from database.connection import init_database


async def run_once() -> dict:
    """Run one orchestrator cycle and return status."""
    init_database()
    orchestrator = AgentOrchestrator()
    await orchestrator.run_single_cycle()
    return orchestrator.get_orchestration_status()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    status = asyncio.run(run_once())
    logging.info("Core agent cycle completed. running=%s", status.get("running"))
    logging.info("Agents: %s", ", ".join(status.get("agents", {}).keys()))


if __name__ == "__main__":
    main()
