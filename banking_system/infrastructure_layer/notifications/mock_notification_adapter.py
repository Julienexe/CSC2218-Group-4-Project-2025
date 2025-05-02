from .notification_adapter import NotificationAdapterInterface

class MockNotificationAdapter(NotificationAdapterInterface):
    """
    A testing adapter that logs both email and SMS calls.
    """
    def send_email(self, recipient: str, subject: str, body: str) -> None:
        print(f"[MOCK ADAPTER EMAIL] To: {recipient}, Subject: {subject} : {body}")

    def send_sms(self, number: str, message: str) -> None:
        print(f"[MOCK ADAPTER SMS] To: {number}: {message}")