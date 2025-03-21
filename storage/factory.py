"""
Factory for creating storage strategy instances.
"""
from storage.google_drive import GoogleDriveStorage
from storage.strategy import StorageContext


class StorageFactory:
    """
    Factory class for creating storage strategies.
    """
    
    @staticmethod
    def create_storage(storage_type):
        """
        Create a storage strategy based on the specified type.
        
        Args:
            storage_type (str): The type of storage strategy to create
            
        Returns:
            StorageContext: The storage context with the strategy set
        """
        context = StorageContext()
        
        if storage_type == 'google_drive':
            context.set_strategy(GoogleDriveStorage())
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
        
        return context