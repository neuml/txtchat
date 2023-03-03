"""
RocketChat module
"""

import asyncio
import logging

from rocketchat_async import RocketChat as RocketChatClient

from .base import Agent

# Logging configuration
logger = logging.getLogger(__name__)


class RocketChat(Agent):
    """
    Intelligent agent for RocketChat, an open-source communications platform.
    """

    def __init__(self, config):
        """
        Creates a RocketChat agent.

        Args:
            config: configuration
        """

        # Call parent constructor
        super().__init__(config)

        # Chat instance
        self.chat = None

        # Direct messages this instance is subscribed to
        self.subscriptions = set()

        # Message ids this instance has responded to
        self.messages = set()

    def start(self):
        """
        Run the agent as an async io function.
        """

        asyncio.run(self.run())

    async def run(self):
        """
        Connects to RocketChat and subscribes to all direct message channels with the agent's username.
        """

        # Create chat instance and connect
        self.chat = RocketChatClient()
        await self.chat.start(*self.connection())

        # Subscribe to existing direct message channels
        for channel, category in await self.chat.get_channels():
            if category == "d":
                logger.info("Listening on %s", (channel, category))
                await self.chat.subscribe_to_channel_messages(channel, self.message)
                self.subscriptions.add(channel)

        # Add callback to subscribe to new direct message channels
        await self.chat.subscribe_to_channel_changes(self.subscribe)

        # Event loop
        await self.chat.run_forever()

    def message(self, channel, sender, uid, thread, text, qualifier):
        """
        Runs text through a txtai workflow and sends the response.

        Args:
            channel: channel id
            sender: message sender id
            uid: message id
            thread: thread id
            text: message text
            qualifer: message qualifier
        """

        # Add thread id to messages if it's missing
        # This happens when this process was restarted
        # Thread can be added to send_message to return a threaded response
        if thread and thread not in self.messages:
            self.messages.add(thread)

        # Respond to message if message not sent from self
        if sender != self.chat.user_id and uid not in self.messages and not qualifier:
            logger.info("Processing message: %s", (channel, sender, uid, thread, text, qualifier))

            # Send message text through workflow and get response
            response = self.process(text)

            # Mark this input message as processed
            self.messages.add(uid)

            # Send response
            self.asyncrun(self.chat.send_message(response, channel))

    def subscribe(self, channel, category):
        """
        Subscribes this agent to messages in channel if it's a direct channel.

        Args:
            channel: channel id
            category: channel category
        """

        if channel not in self.subscriptions and category == "d":
            logger.info("Adding channel %s", (channel, category))
            self.asyncrun(self.chat.subscribe_to_channel_messages(channel, self.message))

            # Save channel subscription
            self.subscriptions.add(channel)

    def asyncrun(self, function):
        """
        Runs function through an async task.

        Args:
            function: function to run
        """

        asyncio.create_task(function)
