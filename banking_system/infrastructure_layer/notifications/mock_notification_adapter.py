from .notification_adapter import NotificationAdapterInterface

class MockNotificationAdapter(NotificationAdapterInterface):
    """
    A mock adapter that logs notifications to the console for testing.
    """
    def send_email(self, recipient: str, subject: str, body: str) -> None:
        print(f"[MOCK EMAIL] To: {recipient}, Subject: {subject}\n{body}")

    def send_sms(self, number: str, message: str) -> None:
        print(f"[MOCK SMS] To: {number}: {message}")
