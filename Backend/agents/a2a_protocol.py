"""
A2A (Agent-to-Agent) Protocol - Standardized communication between agents
"""
from typing import Dict, Any, Optional
import structlog
from datetime import datetime
import json

logger = structlog.get_logger()


class A2AMessage:
    """Standardized A2A message format"""
    
    def __init__(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type
        self.payload = payload
        self.correlation_id = correlation_id or f"msg_{datetime.utcnow().timestamp()}"
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "A2AMessage":
        """Create message from dictionary"""
        return cls(
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            correlation_id=data.get("correlation_id")
        )


class A2AProtocol:
    """A2A Protocol handler for agent communication"""
    
    # Message types
    MESSAGE_TYPES = {
        "REQUEST": "request",
        "RESPONSE": "response",
        "NOTIFICATION": "notification",
        "ERROR": "error"
    }
    
    def __init__(self):
        self.message_queue: list = []
        self.message_history: list = []
    
    def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> A2AMessage:
        """Send A2A message"""
        message = A2AMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload
        )
        
        self.message_queue.append(message)
        self.message_history.append(message.to_dict())
        
        logger.info(
            "A2A message sent",
            sender=sender_id,
            receiver=receiver_id,
            type=message_type,
            correlation_id=message.correlation_id
        )
        
        return message
    
    def receive_message(self, receiver_id: str) -> Optional[A2AMessage]:
        """Receive A2A message for specific receiver"""
        for i, message in enumerate(self.message_queue):
            if message.receiver_id == receiver_id:
                self.message_queue.pop(i)
                logger.info(
                    "A2A message received",
                    receiver=receiver_id,
                    sender=message.sender_id,
                    correlation_id=message.correlation_id
                )
                return message
        return None
    
    def send_request(
        self,
        sender_id: str,
        receiver_id: str,
        request_payload: Dict[str, Any]
    ) -> A2AMessage:
        """Send request message"""
        return self.send_message(
            sender_id,
            receiver_id,
            self.MESSAGE_TYPES["REQUEST"],
            request_payload
        )
    
    def send_response(
        self,
        sender_id: str,
        receiver_id: str,
        response_payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> A2AMessage:
        """Send response message"""
        message = A2AMessage(
            sender_id,
            receiver_id,
            self.MESSAGE_TYPES["RESPONSE"],
            response_payload,
            correlation_id
        )
        self.message_queue.append(message)
        self.message_history.append(message.to_dict())
        return message
    
    def send_notification(
        self,
        sender_id: str,
        receiver_id: str,
        notification_payload: Dict[str, Any]
    ) -> A2AMessage:
        """Send notification message"""
        return self.send_message(
            sender_id,
            receiver_id,
            self.MESSAGE_TYPES["NOTIFICATION"],
            notification_payload
        )
    
    def send_error(
        self,
        sender_id: str,
        receiver_id: str,
        error_payload: Dict[str, Any]
    ) -> A2AMessage:
        """Send error message"""
        return self.send_message(
            sender_id,
            receiver_id,
            self.MESSAGE_TYPES["ERROR"],
            error_payload
        )
    
    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """Get message history"""
        history = self.message_history[-limit:]
        if agent_id:
            return [
                msg for msg in history
                if msg["sender_id"] == agent_id or msg["receiver_id"] == agent_id
            ]
        return history

