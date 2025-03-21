"""
Storage module for handling different storage backends.
"""
from storage.factory import StorageFactory
from storage.strategy import StorageStrategy, StorageContext
from storage.google_drive import GoogleDriveStorage

__all__ = [
    'StorageFactory',
    'StorageStrategy',
    'StorageContext',
    'GoogleDriveStorage'
]