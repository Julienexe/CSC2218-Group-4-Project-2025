"""
Strategy pattern implementation for different storage backends.
"""
from abc import ABC, abstractmethod


class StorageStrategy(ABC):
    """Abstract base class for storage strategies."""
    
    @abstractmethod
    def upload(self, content, metadata):
        """
        Upload content to storage.
        
        Args:
            content (str): The content to upload
            metadata (dict): Additional metadata for the upload
            
        Returns:
            dict: Result of the upload operation
        """
        pass


class StorageContext:
    """
    Context class that maintains a reference to the concrete strategy.
    """
    
    def __init__(self, strategy=None):
        """
        Initialize with a strategy.
        
        Args:
            strategy (StorageStrategy, optional): The storage strategy to use
        """
        self._strategy = strategy
    
    def set_strategy(self, strategy):
        """
        Change the strategy at runtime.
        
        Args:
            strategy (StorageStrategy): The new strategy to use
        """
        self._strategy = strategy
    
    def upload(self, content, metadata):
        """
        Execute the strategy's upload method.
        
        Args:
            content (str): The content to upload
            metadata (dict): Additional metadata for the upload
            
        Returns:
            dict: Result of the upload operation
        """
        if not self._strategy:
            raise ValueError("No storage strategy set")
        
        return self._strategy.upload(content, metadata)