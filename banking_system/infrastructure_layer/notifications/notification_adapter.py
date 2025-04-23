from abc import ABC, abstractmethod

class NotificationAdapterInterface(ABC):
    """
    Interface for sending notifications (email/SMS).
    """
    @abstractmethod
    def send_email(self, recipient: str, subject: str, body: str) -> None:
        """Send an email notification."""
        pass

    @abstractmethod
    def send_sms(self, number: str, message: str) -> None:
        """Send an SMS notification."""
        pass