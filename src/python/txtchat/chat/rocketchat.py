"""
RocketChat module
"""

import hashlib
import json
import logging
import time

import httpx
import websockets

from websockets.exceptions import ConnectionClosedOK, ConnectionClosed

from .base import Chat

# Logging configuration
logger = logging.getLogger(__name__)


class RocketChat(Chat):
    """
    Chat provider for RocketChat.
    """

    def __init__(self, config, action):
        super().__init__(config, action)

        # Get base url
        self.baseurl = config.get("url").rstrip("/")

        # Authentication
        self.username = config.get("username")
        self.password = config.get("password")

        # Use async httpx client
        self.client = httpx.AsyncClient(timeout=30.0)

        # Authentication token
        self.userid = None
        self.token = None

    async def start(self):
        while True:
            try:
                # Login via REST API to get token
                await self.login()

                # Start websocket listener
                await self.listen()

            except (ConnectionClosedOK, ConnectionClosed):
                logger.warning("WebSocket connection closed reconnecting...")

    async def finish(self):
        await self.client.aclose()

    async def login(self):
        """
        Login via the REST API.
        """

        response = await self.client.post(f"{self.baseurl}/api/v1/login", json={"username": self.username, "password": self.password})
        result = response.raise_for_status().json()

        self.userid = result["data"]["userId"]
        self.token = result["data"]["authToken"]

        # Update client headers for authenticated requests
        self.client.headers.update({"X-Auth-Token": self.token or "", "X-User-Id": self.userid or ""})

        logger.info("Logged in as: %s (ID: %s)", self.username, self.userid)

    async def listen(self):
        """
        Listens for new messages.
        """

        # WebSocket URL is typically the base URL with ws:// or wss:// protocol
        protocol = "wss" if self.baseurl.startswith("https") else "ws"
        url = f"{protocol}://{self.baseurl.split('://', 1)[1]}/websocket"

        logger.info("Connecting to WebSocket: %s", url)

        async with websockets.connect(url) as websocket:
            # Login to server
            await self.connect(websocket)

            # Subscribe to existing direct message channels
            await self.subscribe(websocket)

            logger.info("Listening for messages...")

            # Process incoming messages
            async for message in websocket:
                await self.process(json.loads(message), websocket)

    async def connect(self, websocket):
        """
        Connects the RocketChat websocket listener.

        Args:
            websocket: open websocket connection
        """

        # Send connect message
        await websocket.send(json.dumps({"msg": "connect", "version": "1", "support": ["1"]}))

        # Wait for connected response
        response = await websocket.recv()
        logger.info("WebSocket connected: %s", response)

        # Send login message
        await websocket.send(json.dumps({"msg": "method", "method": "login", "id": "1", "params": [{"resume": self.token}]}))

        # Wait for login response
        response = await websocket.recv()
        logger.info("Login response: %s", response)

    async def subscribe(self, websocket):
        """
        Subscribes to new messages.

        Args:
            websocket: open websocket connection
        """

        # Get rooms list
        response = await self.client.get(f"{self.baseurl}/api/v1/rooms.get")
        result = response.raise_for_status().json()

        logger.info("Rooms API response: %s", result)

        # Get rooms
        rooms = result["update"] if "update" in result else []

        for room in rooms:
            # 'c' for channel, 'd' for direct
            rid, rtype = room["_id"], room.get("t", "c")

            if rtype == "d":
                # Subscribe to room messages
                await websocket.send(json.dumps({"msg": "sub", "id": f"sub_{rid}", "name": "stream-room-messages", "params": [rid, False]}))
                logger.info("Subscribed to room: %s (%s)", room.get("name", rid), rtype)

        # Subscribe to new channel changes
        await self.subscribechannels(websocket)

    async def subscribechannels(self, websocket):
        """
        Subscribes to channel changes.

        Args:
            websocket: open websocket connection
        """

        # Subscribe to user notifications for channel changes
        message = {"msg": "sub", "id": "channel_changes_sub", "name": "stream-notify-user", "params": [f"{self.userid}/rooms-changed", False]}

        await websocket.send(json.dumps(message))
        logger.info("Subscribed to channel changes")

    async def process(self, message, websocket):
        """
        Processes an incoming message.

        Args:
            message: incoming message
            websocket: open websocket connection
        """

        mtype = message.get("msg")
        if mtype == "changed":
            # Process stream message
            args = message.get("fields", {}).get("args", [])
            if args:
                collection = message.get("collection")
                if collection == "stream-room-messages":
                    await self.onmessage(args[0], websocket)
                elif collection == "stream-notify-user":
                    await self.onchannel(args, websocket)
        elif mtype == "ping":
            # Respond to ping with pong
            await websocket.send(json.dumps({"msg": "pong"}))

    async def onmessage(self, event, websocket):
        """
        Analyzes and responds to an incoming message.

        Args:
            event: incoming message event
            websocket: open websocket connection
        """

        # Skip messages own messages
        if event.get("u", {}).get("_id") == self.userid:
            return

        rid = event.get("rid")
        message = event.get("msg", "").strip()

        if rid and message:
            logger.info("Received DM: %s", message)

            # Send typing indicator
            await self.typing(rid, websocket)

            # Generate response while user sees typing indicator
            response = self.action(message, session=rid)

            # Send the message via REST API to ensure delivery as websocket can sometimes be closed
            await self.sendmessage(rid, response)

    async def onchannel(self, args, websocket):
        """
        Analyzes an incoming channel change event.

        Args:
            args: incoming event data
            websocket: open websocket connection
        """

        if not args or len(args) < 2:
            return

        etype, data = args[0], args[1]
        if etype != "removed":
            rid = data.get("_id")
            rtype = data.get("t")

            # Subscribe if this is a new channel
            if rtype == "d" and rid:
                # Subscribe to room messages
                await websocket.send(json.dumps({"msg": "sub", "id": f"sub_{rid}", "name": "stream-room-messages", "params": [rid, False]}))
                logger.info("Subscribed to new direct channel: %s", rid)

    async def typing(self, rid, websocket):
        """
        Sends a typing indicator event.

        Args:
            rid: room id
            websocket: open websocket connection
        """

        await websocket.send(
            json.dumps(
                {
                    "msg": "method",
                    "method": "stream-notify-room",
                    "id": f"typing_{int(time.time() * 1000)}",
                    "params": [f"{rid}/user-activity", self.username, ["user-typing"]],
                }
            )
        )

    async def sendmessage(self, rid, message):
        """
        Sends a message.

        Args:
            rid: room id
            message: message to send
        """

        # Generate unique message ID
        uid = hashlib.md5(f"{time.time()}:{rid}".encode()).hexdigest()[:12]

        # Use REST API to send message
        response = await self.client.post(f"{self.baseurl}/api/v1/chat.sendMessage", json={"message": {"_id": uid, "rid": rid, "msg": str(message)}})
        response.raise_for_status().json()

        logger.info("Sent response: %s", message)
