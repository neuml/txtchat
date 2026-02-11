"""
Mattermost module
"""

import json
import logging

import httpx
import websockets

from websockets.exceptions import ConnectionClosedOK, ConnectionClosed

from .base import Chat

# Logging configuration
logger = logging.getLogger(__name__)


class Mattermost(Chat):
    """
    Chat provider for Mattermost.
    """

    def __init__(self, config, action):
        super().__init__(config, action)

        url, token = config.get("url"), config.get("token")

        self.baseurl = url.rstrip("/")
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Use async httpx client
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

        # State information
        self.userid = None
        self.channels = set()

    async def start(self):
        while True:
            try:
                # Get user id
                response = await self.client.get(f"{self.baseurl}/api/v4/users/me")
                data = response.raise_for_status().json()

                self.userid = data["id"]
                logger.info("Started as: %s (ID: %s)", data["username"], self.userid)

                await self.listen()

            except (ConnectionClosedOK, ConnectionClosed):
                logger.warning("WebSocket connection closed reconnecting...")

    async def finish(self):
        await self.client.aclose()

    async def listen(self):
        """
        Listens for new messages.
        """

        # WebSocket URL is typically the base URL with ws:// or wss:// protocol
        protocol = "wss" if self.baseurl.startswith("https") else "ws"
        url = f"{protocol}://{self.baseurl.split('://', 1)[1]}/api/v4/websocket"
        logger.info("Connecting to WebSocket: %s", url)

        async with websockets.connect(url, additional_headers={"Authorization": f"Bearer {self.token}"}) as websocket:
            # Send authentication challenge response
            await websocket.send(json.dumps({"seq": 1, "action": "authentication_challenge", "data": {"token": self.token}}))
            logger.info("WebSocket connected. Listening for messages...")

            # Process incoming messages
            async for message in websocket:
                await self.process(json.loads(message))

    async def process(self, message):
        """
        Processes each incoming message.

        Args:
            message: incoming message
        """

        if message.get("event") == "posted":
            data = message.get("data", {})
            post = data.get("post", {})

            # Parse post, if necessary
            post = json.loads(post) if isinstance(post, str) else post

            channel = post.get("channel_id")
            message = post.get("message", "").strip()

            # Skip messages own messages and non-direct messages
            if post.get("user_id") != self.userid and (channel and message and await self.isdirect(channel)):
                logger.info("Received DM: %s", message)

                # Send typing indicator
                await self.typing(channel)

                # Generate response
                response = self.action(message, session=channel)

                # Send response
                await self.sendmessage(channel, response)

    async def isdirect(self, channel):
        """
        Checks if channel is a direct message channel. Caches responses.

        Args:
            channel: channel to check

        Returns:
            True if this is a direct message, False otherwise
        """

        # Cache channel info to avoid repeated API calls
        if channel in self.channels:
            return True

        response = await self.client.get(f"{self.baseurl}/api/v4/channels/{channel}")
        channel = response.json()

        # 'D' indicates direct message
        if channel.get("type") == "D":
            self.channels.add(channel.get("id"))
            return True

        return False

    async def typing(self, channel):
        """
        Sends a typing indicator event.

        Args:
            channel: channel to send typing indicator
        """

        await self.client.post(f"{self.baseurl}/api/v4/users/me/typing", json={"channel_id": channel})

    async def sendmessage(self, channel, message):
        """
        Sends a message.

        Args:
            channel: channel to send message
            message: message to send
        """

        message = {"channel_id": channel, "message": str(message)}

        response = await self.client.post(f"{self.baseurl}/api/v4/posts", json=message)
        response.raise_for_status()
        logger.info("Sent response: %s", message)
