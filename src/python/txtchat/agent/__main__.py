"""
Main agent execution method
"""

import logging
import sys

from .base import Agent


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: agent <path to config yml>")
        sys.exit()

    # Configure logging
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s")
    logging.getLogger().setLevel(logging.INFO)

    # Load agent
    agent = Agent(sys.argv[1])

    # Run agent
    agent()
