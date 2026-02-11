"""
Chat module
"""

import asyncio


class Chat:
    """
    Base chat provider class.
    """

    def __init__(self, config, action):
        """
        Creates a new chat provider.

        Args:
            config: chat configuration
            action: chat action to execute for each message
        """

        # Chat configuration
        self.config = config

        # Action to execute
        self.action = action

    def run(self):
        """
        Starts the chat session and main processing loop.
        """

        # Start main loop
        asyncio.run(self.loop())

    async def loop(self):
        """
        Main processing loop.
        """

        try:
            await self.start()
        finally:
            await self.finish()

    async def start(self):
        """
        Starts a new chat session.
        """

        raise NotImplementedError

    async def finish(self):
        """
        Closes and cleans up this chat session.
        """

        raise NotImplementedError
