"""
Factory module
"""

from .mattermost import Mattermost
from .rocketchat import RocketChat


class ChatFactory:
    """
    Methods to create chat providers.
    """

    @staticmethod
    def create(config, action):
        """
        Create a Chat provider.

        Args:
            config: chat configuration
            action: chat action to execute for each message

        Returns:
            Chat
        """

        # Chat instance
        chat = None
        provider = config.get("provider")

        # Create chat instance
        if provider == "mattermost":
            chat = Mattermost(config, action)
        else:
            chat = RocketChat(config, action)

        return chat
