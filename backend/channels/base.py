from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SendResult:
    success: bool
    response: dict = field(default_factory=dict)
    error_message: str = ""

    def __bool__(self):
        return self.success


class BaseChannel(ABC):
    """
    Abstract base class for all notification channels.
    Every channel (WhatsApp, Email, WebPush) must implement the send() method.
    """

    @abstractmethod
    def send(self, user, template, context: dict):
        """
        Send a notification to the given user using the provided template and context.

        Args:
            user:     Django User instance
            template: NotificationTemplate model instance
            context:  dict of rendered variables (e.g. {'name': 'Alice', 'email': '...'})

        Returns:
            SendResult with success/failure and provider response details.
        """
        raise NotImplementedError
