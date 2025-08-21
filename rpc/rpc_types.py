from datetime import datetime
from typing import Any, Literal, TypedDict

from deepfake.enums import RPCMessageType


ProfitLossStr = Literal["profit", "loss"]


class RPCSendMsgBase(TypedDict):
    pass
    # ty1pe: Literal[RPCMessageType]


class RPCStatusMsg(RPCSendMsgBase):
    """Used for Status, Startup and Warning messages"""

    type: Literal[RPCMessageType.STATUS, RPCMessageType.STARTUP, RPCMessageType.WARNING]
    status: str

