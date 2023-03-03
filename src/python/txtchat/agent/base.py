"""
Agent module
"""

import logging
import os
import traceback

from txtai.app import Application

# Logging configuration
logger = logging.getLogger(__name__)


class Agent:
    """
    Base class for intelligent agents. An agent is joined with a txtai workflow to form a persona. This persona determines how an agent behaves and
    the type of generated AI-powered responses to user messages.
    """

    def __init__(self, config):
        """
        Create a new agent.

        Args:
            config: configuration
        """

        self.config = config

        # Workflow application
        self.application = Application(config)

        # Workflow to execute, default to first workflow found if not provided
        self.action = config.get("action", list(self.application.workflows.keys())[0])

    def __call__(self):
        """
        Run this agent.
        """

        logger.info("Starting agent")
        self.start()

    def process(self, text):
        """
        Runs a workflow with message text as input.

        Args:
            text: input text

        Returns:
            message response
        """

        # pylint: disable=W0703
        try:
            # Execute workflow for input message text
            response = list(self.application.workflow(self.action, [text]))[0]
        except Exception:
            response = "I had an error processing this request"
            logger.error(traceback.format_exc())

        return response

    def connection(self):
        """
        Reads agent connection parameters. This method also supports parameters as environment variables.

        Returns:
            (url, username, password)
        """

        # Get agent connection parameters
        config = self.config.get("agent", {})

        # Get parameters from config. If empty check environment variables
        return [config.get(x, os.environ.get(f"AGENT_{x.upper()}")) for x in ["url", "username", "password"]]

    def start(self):
        """
        Method that initiates and registers an agent with a messaging platform.
        """

        raise NotImplementedError
