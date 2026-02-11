"""
Agent module
"""

import logging
import os
import traceback

import huggingface_hub
import yaml

from txtai import Application

from ..chat import ChatFactory

# Logging configuration
logger = logging.getLogger(__name__)


class Agent:
    """
    Base class for txtchat agents. An agent is joined with a txtai application to form a persona. This persona determines how an agent behaves and
    the type of generated AI-powered responses to user messages.
    """

    def __init__(self, path):
        """
        Create a new agent.

        Args:
            path: path to configuration file
        """

        # Load configuration
        self.config = self.load(path)

        # Create a txtai application instance
        self.application = Application(self.config)

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

        # Load chat provider
        self.chat = ChatFactory.create(self.connection(), self.execute)

    def __call__(self):
        """
        Run this agent.
        """

        logger.info("Starting agent")

        # Run chat loop
        self.chat.run()

    def execute(self, text, **kwargs):
        """
        Executes an Agent task with message text as input.

        Args:
            text: input text
            kwargs: additional keyword arguments

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
                response = self.application.agent(self.action, text, self.config.get("maxlength", 8192), **kwargs)

        except Exception:
            response = "I had an error processing this request"
            logger.error(traceback.format_exc())

        return response

    def connection(self):
        """
        Reads agent connection parameters. This method also supports parameters as environment variables.

        Returns:
            connection parameters
        """

        # Get agent connection parameters
        config = self.config.get("connection", {})

        # Get parameters from config. If empty check environment variables
        return {x: config.get(x, os.environ.get(f"AGENT_{x.upper()}")) for x in ["url", "username", "password", "token", "provider"]}

    def load(self, path):
        """
        Loads configuration from path. If path doesn't exist, check with project on HF Hub.

        Args:
            path: path to configuration

        Returns:
            configuration
        """

        # Check Hugging Face Hub for configuration
        if not os.path.exists(path):
            path = huggingface_hub.hf_hub_download(
                repo_id="neuml/txtchat-personas",
                filename=os.path.basename(path),
            )

        # Read yaml from file
        with open(path, "r", encoding="utf-8") as f:
            # Read configuration
            config = yaml.safe_load(f)

        return config
