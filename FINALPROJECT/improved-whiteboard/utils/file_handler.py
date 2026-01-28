"""
File Handler Utility
Handles file operations like saving PNG exports
"""

import os
from datetime import datetime
import config

class FileHandler:
    def __init__(self):
        """Initialize file handler"""
        # Create exports folder if it doesn't exist
        if not os.path.exists(config.EXPORT_FOLDER):
            os.makedirs(config.EXPORT_FOLDER)
            print(f"📁 Created export folder: {config.EXPORT_FOLDER}")
    
    def generate_filename(self) -> str:
        """
        Generate filename with timestamp
        
        Returns:
            str: Filename (e.g., 'whiteboard_2026-01-21_14-30-45.png')
        """
        timestamp = datetime.now().strftime(config.EXPORT_FORMAT)
        return timestamp
    
    def get_export_path(self, filename: str = None) -> str:
        """
        Get full export file path
        
        Args:
            filename: Optional custom filename
            
        Returns:
            str: Full file path
        """
        if filename is None:
            filename = self.generate_filename()
        
        return os.path.join(config.EXPORT_FOLDER, filename)
    
    def list_exports(self) -> list:
        """
        List all exported files
        
        Returns:
            list: List of filenames in export folder
        """
        if not os.path.exists(config.EXPORT_FOLDER):
            return []
        
        files = [f for f in os.listdir(config.EXPORT_FOLDER) if f.endswith('.png')]
        files.sort(reverse=True)  # Most recent first
        return files
