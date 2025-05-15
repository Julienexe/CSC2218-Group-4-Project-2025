from application_layer.repository_interfaces import NotificationAdapterInterface

class NotificationAdapter(NotificationAdapterInterface):
    def __init__(self):
        # {account_id: set of notification_types}
        self._preferences = {}

    def notify(self, message):
        # For demonstration, just print the message
        print(f"Notification sent: {message}")

    def save_notification_preference(self, account_id, notification_type):
        if account_id not in self._preferences:
            self._preferences[account_id] = set()
        self._preferences[account_id].add(notification_type)
        return True

    def remove_notification_preference(self, account_id, notification_type):
        if account_id in self._preferences and notification_type in self._preferences[account_id]:
            self._preferences[account_id].remove(notification_type)
            return True
        return False

    def get_notification_preferences(self, account_id):
        return list(self._preferences.get(account_id, []))