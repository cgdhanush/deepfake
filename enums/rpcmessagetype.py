from enum import Enum


class RPCMessageType(str, Enum):
    STATUS = "status"
    WARNING = "warning"
    EXCEPTION = "exception"
    STARTUP = "startup"
    
    OTHER = "other"

    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value


# Enum for parsing requests from ws consumers
class RPCRequestType(str, Enum):
    SUBSCRIBE = "subscribe"

    def __str__(self):
        return self.value


NO_ECHO_MESSAGES = (RPCMessageType.OTHER)
