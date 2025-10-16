#!/usr/bin/env python

from redis import asyncio as aioredis
import asyncio
import json

import django

django.setup()


from django.template import Context, Template
from django.template.loader import get_template

from sesame.utils import get_user
from websockets.asyncio.server import broadcast, serve
from websockets.frames import CloseCode

from chat.models import Conversation


CONNECTIONS = {}


def get_conversations(user):
    return set(list(user.conversations.all().values_list("pk", flat=True)))


def get_rendered_message_list(conversation_id: int):
    conversation: Conversation = Conversation.objects.get(pk=conversation_id)
    template = get_template("message/_ws_list.html")
    return template.render(
        context={
            "conversation": conversation,
            "messages": conversation.messages.not_deleted().not_drafts(),
        }
    )


async def handler(websocket):
    """Authenticate user and register connection in CONNECTIONS."""
    print(f"Connecting")
    payload = await websocket.recv()
    print(f"Received {payload}")
    try:
        payload = json.loads(payload)
        print("getting user")
        user = await asyncio.to_thread(get_user, payload["token"])
        if user is None:
            print(f"Invalid user authentication {payload}")
            await websocket.close(CloseCode.INTERNAL_ERROR, "authentication failed")
            return
    except json.JSONDecodeError:
        print(f"Failed to parse payload: {payload}")
        return

    convo_ids = await asyncio.to_thread(get_conversations, user)
    print(f"Got conversations {convo_ids} for user {user}")
    CONNECTIONS[websocket] = {"user_id": user.pk, "conversation_ids": convo_ids}
    try:
        await websocket.wait_closed()
    finally:
        print(f"Disconnected")
        del CONNECTIONS[websocket]


async def process_events():
    """Listen to events in Redis and process them."""
    redis = aioredis.from_url("redis://127.0.0.1:6379/1")
    pubsub = redis.pubsub()
    await pubsub.subscribe("events")
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        payload = message["data"].decode()

        event = json.loads(payload)
        recipients = (
            websocket
            for websocket, connection in CONNECTIONS.items()
            if connection["user_id"] in event["target_ids"]
        )

        print("Sending conversation %s.." % event["conversation_id"])
        html = await asyncio.to_thread(
            get_rendered_message_list, event["conversation_id"]
        )
        broadcast(recipients, html)


async def main():
    async with serve(handler, "localhost", 8888):
        await process_events()  # runs forever


if __name__ == "__main__":
    asyncio.run(main())
