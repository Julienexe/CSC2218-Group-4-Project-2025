from typing import List
from banking_system.application_layer.repository_interfaces import NotificationRepositoryInterface

class NotificationPreferencesRepository(NotificationRepositoryInterface):
    def __init__(self) -> None:
        """
        In-memory storage for notification preferences.
        """
        self._prefs: dict[str, set[str]] = {}

    def save_notification_preference(self, account_id: str, notification_type: str) -> bool:
        """
        Saves a notification preference for an account.
        """
        self._prefs.setdefault(account_id, set()).add(notification_type)
        return True

    def remove_notification_preference(self, account_id: str, notification_type: str) -> bool:
        """
        Removes a notification preference for an account.
        """
        types = self._prefs.get(account_id)
        if types and notification_type in types:
            types.remove(notification_type)
            return True
        return False

    def get_notification_preferences(self, account_id: str) -> List[str]:
        """
        Gets all notification preferences for an account.
        """
        return list(self._prefs.get(account_id, []))
