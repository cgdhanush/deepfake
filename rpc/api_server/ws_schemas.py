from datetime import datetime
from typing import Any, TypedDict

from pydantic import BaseModel, ConfigDict

from deepfake.enums import RPCMessageType, RPCRequestType


class BaseArbitraryModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class WSRequestSchema(BaseArbitraryModel):
    type: RPCRequestType
    data: Any | None = None


class WSMessageSchemaType(TypedDict):
    # Type for typing to avoid doing pydantic typechecks.
    type: RPCMessageType
    data: dict[str, Any] | None


class WSMessageSchema(BaseArbitraryModel):
    type: RPCMessageType
    data: Any | None = None
    model_config = ConfigDict(extra="allow")


# ------------------------------ REQUEST SCHEMAS ----------------------------


class WSSubscribeRequest(WSRequestSchema):
    type: RPCRequestType = RPCRequestType.SUBSCRIBE
    data: list[RPCMessageType]



# ------------------------------ MESSAGE SCHEMAS ----------------------------


class WSErrorMessage(WSMessageSchema):
    type: RPCMessageType = RPCMessageType.EXCEPTION
    data: str


# --------------------------------------------------------------------------
