"""
Agent module
"""

import logging
import os
import re
import traceback

from txtai.app import Application

# Logging configuration
logger = logging.getLogger(__name__)


class Agent:
    """
    Base class for txtchat agents. An agent is joined with a txtai application to form a persona. This persona determines how an agent behaves and
    the type of generated AI-powered responses to user messages.
    """

    def __init__(self, config):
        """
        Create a new agent.

        Args:
            config: configuration
        """

        # Agent configuration
        self.config = config

        # Create a txtai application instance
        self.application = Application(config)

        # Get action, if available
        action = self.config.get("action")

        # Workflow action
        if action in self.application.workflows:
            self.action, self.task = action, "workflow"

        # Agent action
        elif action in self.application.agents:
            self.action, self.task = action, "agent"

        # Default workflow action
        elif self.application.workflows:
            self.action, self.task = list(self.application.workflows.keys())[0], "workflow"

        # Default agent action
        else:
            self.action, self.task = list(self.application.agents.keys())[0], "agent"

    def __call__(self):
        """
        Run this agent.
        """

        logger.info("Starting agent")
        self.start()

    def execute(self, text):
        """
        Executes an Agent task with message text as input.

        Args:
            text: input text

        Returns:
            message response
        """

        # pylint: disable=W0703
        try:
            # Execute action
            if self.task == "workflow":
                # Execute workflow for input message text
                response = list(self.application.workflow(self.action, [text]))[0]
            else:
                # Execute agent for input message text
                response = self.application.agent(self.action, text, self.config.get("maxlength", 8192))

            # Remove thinking tags
            response = re.sub(r"<think>.*?</think>\n?", "", response, flags=re.DOTALL).strip()

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
        config = self.config.get("connection", {})

        # Get parameters from config. If empty check environment variables
        return [config.get(x, os.environ.get(f"AGENT_{x.upper()}")) for x in ["url", "username", "password"]]

    def start(self):
        """
        Method that initiates and registers an agent with a messaging platform.
        """

        raise NotImplementedError
