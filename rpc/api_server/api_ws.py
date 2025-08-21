import logging
import time
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket
from pydantic import ValidationError

from deepfake.enums import RPCMessageType, RPCRequestType
from deepfake.exceptions import DeepfakeException
from deepfake.rpc.api_server.api_auth import validate_ws_token
from deepfake.rpc.api_server.deps import get_message_stream, get_rpc
from deepfake.rpc.api_server.ws.channel import WebSocketChannel, create_channel
from deepfake.rpc.api_server.ws.message_stream import MessageStream
from deepfake.rpc.api_server.ws_schemas import (
    WSErrorMessage,
    WSMessageSchema,
    WSRequestSchema,
)
from deepfake.rpc.rpc import RPC


logger = logging.getLogger(__name__)

# Private router, protected by API Key authentication
router = APIRouter()


async def channel_reader(channel: WebSocketChannel, rpc: RPC):
    """
    Iterate over the messages from the channel and process the request
    """
    async for message in channel:
        try:
            await _process_consumer_request(message, channel, rpc)
        except DeepfakeException:
            logger.exception(f"Error processing request from {channel}")
            response = WSErrorMessage(data="Error processing request")

            await channel.send(response.dict(exclude_none=True))


async def channel_broadcaster(channel: WebSocketChannel, message_stream: MessageStream):
    """
    Iterate over messages in the message stream and send them
    """
    async for message, ts in message_stream:
        if channel.subscribed_to(message.get("type")):
            # Log a warning if this channel is behind
            # on the message stream by a lot
            if (time.time() - ts) > 60:
                logger.warning(
                    f"Channel {channel} is behind MessageStream by 1 minute,"
                    " this can cause a memory leak if you see this message"
                    " often, consider reducing pair list size or amount of"
                    " consumers."
                )

            await channel.send(message, use_timeout=True)


async def _process_consumer_request(request: dict[str, Any], channel: WebSocketChannel, rpc: RPC):
    """
    Validate and handle a request from a websocket consumer
    """
    # Validate the request, makes sure it matches the schema
    try:
        websocket_request = WSRequestSchema.model_validate(request)
    except ValidationError as e:
        logger.error(f"Invalid request from {channel}: {e}")
        return

    type_, data = websocket_request.type, websocket_request.data
    response: WSMessageSchema

    logger.debug(f"Request of type {type_} from {channel}")

    # If we have a request of type SUBSCRIBE, set the topics in this channel
    if type_ == RPCRequestType.SUBSCRIBE:
        # If the request is empty, do nothing
        if not data:
            return

        # If all topics passed are a valid RPCMessageType, set subscriptions on channel
        if all([any(x.value == topic for x in RPCMessageType) for topic in data]):
            channel.set_subscriptions(data)

        # We don't send a response for subscriptions
        return

@router.websocket("/message/ws")
async def message_endpoint(
    websocket: WebSocket,
    token: str = Depends(validate_ws_token),
    rpc: RPC = Depends(get_rpc),
    message_stream: MessageStream = Depends(get_message_stream),
):
    if token:
        async with create_channel(websocket) as channel:
            await channel.run_channel_tasks(
                channel_reader(channel, rpc), channel_broadcaster(channel, message_stream)
            )
