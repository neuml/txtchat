"""
Factory module
"""

import os

import huggingface_hub
import yaml

from .rocketchat import RocketChat


class AgentFactory:
    """
    Methods to create txtchat agents.
    """

    @staticmethod
    def create(path):
        """
        Creates an Agent.

        Args:
            path: path to configuration

        Returns:
            Agent
        """

        # Load configuration
        config = AgentFactory.load(path)

        # RocketChat is the only currently supported agent
        return RocketChat(config)

    @staticmethod
    def load(path):
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
